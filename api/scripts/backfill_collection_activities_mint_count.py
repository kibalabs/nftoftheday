import asyncio
import logging
import os
import sys

import asyncclick as click
import sqlalchemy
from core import logging
from core.queues.sqs import SqsMessageQueue
from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.util import date_util
from core.util import list_util
from sqlalchemy.sql import functions as sqlalchemyfunc

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from notd.activity_manager import ActivityManager
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.messages import UpdateActivityForCollectionMessageContent
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlock', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlock', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=500)
async def backfill_collection_activities_mint_count(startBlock: int, endBlock: int, batchSize: int):
    accessKeyId = os.environ['AWS_KEY']
    accessKeySecret = os.environ['AWS_SECRET']

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    activityManager = ActivityManager(saver=saver, retriever=retriever, workQueue=None, tokenQueue=tokenQueue, collectionActivityProcessor=collectionActivityProcessor)

    await database.connect()
    await tokenQueue.connect()

    currentBlockNumber = startBlock
    while currentBlockNumber < endBlock:
        endBlockNumber = min(currentBlockNumber + batchSize, endBlock)
        logging.info(f'Working on {currentBlockNumber} to {endBlockNumber}...')
        registryDatesQuery = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress, BlocksTable.c.blockDate)  # type: ignore[no-untyped-call]
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(BlocksTable.c.blockNumber >= currentBlockNumber)
            .where(BlocksTable.c.blockNumber < endBlockNumber)
        )
        registryDatesResults = await retriever.database.execute(query=registryDatesQuery)
        registryDatePairs = {(registryAddress, date_util.date_hour_from_datetime(blockDate)) for (registryAddress, blockDate) in registryDatesResults}
        print(f'Got {len(registryDatePairs)} registryDatePairs')
        if len(registryDatePairs) == 0:
            print(f"Skipping {currentBlockNumber} to {endBlockNumber} with 0 registryDatePairs ")
        else:
            minDate = min([date for _, date in registryDatePairs])
            maxDate = max([date for _, date in registryDatePairs])
            collectionHourlyActivities = await retriever.list_collection_activities(
                fieldFilters=[
                    DateFieldFilter(CollectionHourlyActivitiesTable.c.date.key, gte=minDate),
                    DateFieldFilter(CollectionHourlyActivitiesTable.c.date.key, lte=maxDate),
                ],
            )
            processedRegistryDatePairs = {(collectionHourlyActivity.address, collectionHourlyActivity.date) for collectionHourlyActivity in collectionHourlyActivities}
            registryDatePairsToProcess = {(registryAddress, date) for (registryAddress, date) in registryDatePairs if (registryAddress, date) not in processedRegistryDatePairs}
            print(f'Processing {len(registryDatePairsToProcess)} registryDatePairs')
            # messages = [UpdateActivityForCollectionMessageContent(address=address, startDate=startDate).to_message() for (address, startDate) in registryDatePairs]
            # await tokenQueue.send_messages(messages=messages)
            for pairChunk in list_util.generate_chunks(lst=list(registryDatePairsToProcess), chunkSize=50):
                await asyncio.gather(*[activityManager.update_activity_for_collection(address=registryAddress, startDate=startDate) for registryAddress, startDate in pairChunk])
        currentBlockNumber = endBlockNumber

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_collection_activities_mint_count())
