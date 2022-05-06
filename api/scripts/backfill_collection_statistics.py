
import asyncio
import sys
import os
import logging
import asyncclick as click

from core.util import list_util
from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.token_manager import TokenManager
from notd.store.schema import BlocksTable
from notd.store.saver import Saver
from notd.store.retriever import Retriever
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.date_util import date_hour_from_datetime


@click.command()
@click.option('-s', '--start-block-number', 'startBlock', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlock', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=3)
async def backfill_collection_statistics(startBlock: int, endBlock: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    tokenQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None, collectionActivityProcessor=collectionActivityProcessor)

    await database.connect()
    await tokenQueue.connect()
    currentBlockNumber = startBlock
    while currentBlockNumber < endBlock:
        start = currentBlockNumber
        end = start + batchSize

        logging.info(f'Working on {start} to {end}...')
        tokenTransfers = await retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(BlocksTable.c.blockNumber.key, gte=start),
                DateFieldFilter(BlocksTable.c.blockNumber.key, lt=end),
            ],
        )
        pairs = {(tokenTransfer.registryAddress, date_hour_from_datetime(tokenTransfer.blockDate)) for tokenTransfer in tokenTransfers}
        for pairChunk in list_util.generate_chunks(lst=list(pairs), chunkSize=5):
            await asyncio.gather(*[tokenManager.update_activity_for_collection(address=registryAddress, startDate=startDate) for registryAddress, startDate in pairChunk])
        
        currentBlockNumber = end

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_collection_statistics())
