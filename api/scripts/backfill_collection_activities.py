
import asyncio
import logging
import os
import sys

import asyncclick as click
from core.queues.sqs import SqsMessageQueue
from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.util import date_util
from core.util import list_util

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.token_manager import TokenManager


@click.command()
@click.option('-s', '--start-block-number', 'startBlock', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlock', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=500)
async def backfill_collection_activities(startBlock: int, endBlock: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None, collectionActivityProcessor=collectionActivityProcessor)

    await database.connect()
    await tokenQueue.connect()
    currentBlockNumber = startBlock
    while currentBlockNumber < endBlock:
        endBlockNumber = min(currentBlockNumber + batchSize, endBlock)
        logging.info(f'Working on {currentBlockNumber} to {endBlockNumber}...')
        tokenTransfers = await retriever.list_token_transfers(
            fieldFilters=[
                IntegerFieldFilter(BlocksTable.c.blockNumber.key, gte=currentBlockNumber),
                IntegerFieldFilter(BlocksTable.c.blockNumber.key, lte=endBlockNumber),
            ],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.ASCENDING)],
        )
        if len(tokenTransfers) == 0:
            print(f"Skipping {currentBlockNumber} to {endBlockNumber} with 0 transfers ")
        else:
            collectionHourlyActivities = await retriever.list_collection_activities(
                fieldFilters=[
                    DateFieldFilter(CollectionHourlyActivitiesTable.c.date.key, gte=date_util.date_hour_from_datetime(tokenTransfers[0].blockDate)),
                    DateFieldFilter(CollectionHourlyActivitiesTable.c.date.key, lte=date_util.date_hour_from_datetime(tokenTransfers[-1].blockDate)),
                ],
            )
            processedPairs = {(collectionHourlyActivity.address, collectionHourlyActivity.date) for collectionHourlyActivity in collectionHourlyActivities}
            registryDatePairs = {(tokenTransfer.registryAddress, date_util.date_hour_from_datetime(tokenTransfer.blockDate)) for tokenTransfer in tokenTransfers if (tokenTransfer.registryAddress, date_util.date_hour_from_datetime(tokenTransfer.blockDate)) not in processedPairs}
            print(f'Processing {len(registryDatePairs)} pairs from {len(tokenTransfers)} transfers')
            # messages = [UpdateActivityForCollectionMessageContent(address=address, startDate=startDate).to_message() for (address, startDate) in registryDatePairs]
            # await tokenQueue.send_messages(messages=messages)
            for pairChunk in list_util.generate_chunks(lst=list(registryDatePairs), chunkSize=50):
                await asyncio.gather(*[tokenManager.update_activity_for_collection(address=registryAddress, startDate=startDate) for registryAddress, startDate in pairChunk])
        currentBlockNumber = endBlockNumber

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_collection_activities())
