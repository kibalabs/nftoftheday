
import asyncio
import logging
import os
import sys

import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.database import Database
from core.store.retriever import  DateFieldFilter
from core.store.retriever import IntegerFieldFilter
from core.util import list_util
from core.store.retriever import Order
from core.store.retriever import Direction

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import CollectionHourlyActivityTable
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.date_util import date_hour_from_datetime
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
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
                IntegerFieldFilter(BlocksTable.c.blockNumber.key, lt=endBlockNumber),
            ],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.ASCENDING)],
        )
        collectionHourlyActivities = await retriever.list_collections_activity(
            fieldFilters=[
                DateFieldFilter(CollectionHourlyActivityTable.c.date.key, gte=tokenTransfers[0].blockDate),
                DateFieldFilter(CollectionHourlyActivityTable.c.date.key, lte=tokenTransfers[-1].blockDate),
            ],
        )
        processedPairs = {(collectionHourlyActivity.address, collectionHourlyActivity.date) for collectionHourlyActivity in collectionHourlyActivities}
        pairs = {(tokenTransfer.registryAddress, date_hour_from_datetime(tokenTransfer.blockDate)) for tokenTransfer in tokenTransfers if (tokenTransfer.registryAddress, date_hour_from_datetime(tokenTransfer.blockDate)) not in processedPairs}
        print(len(pairs))
        for pairChunk in list_util.generate_chunks(lst=list(pairs), chunkSize=10):
            await asyncio.gather(*[tokenManager.update_activity_for_collection(address=registryAddress, startDate=startDate) for registryAddress, startDate in pairChunk])
        currentBlockNumber = endBlockNumber

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_collection_activities())
