
import asyncio
import logging
import os
import sys

import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.util import list_util

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.date_util import date_hour_from_datetime
from notd.messages import UpdateActivityForCollectionMessageContent
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
                DateFieldFilter(BlocksTable.c.blockNumber.key, gte=currentBlockNumber),
                DateFieldFilter(BlocksTable.c.blockNumber.key, lt=endBlockNumber),
            ],
        )
        registryDatePairs = {(tokenTransfer.registryAddress, date_hour_from_datetime(tokenTransfer.blockDate)) for tokenTransfer in tokenTransfers}
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
