
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
import sqlalchemy

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.activity_manager import ActivityManager
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.token_manager import TokenManager


async def backfill_collection_activities():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    tokenQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')

    # tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    collectionActivityManager = ActivityManager(saver=saver, retriever=retriever, workQueue=None, tokenQueue=tokenQueue, collectionActivityProcessor=collectionActivityProcessor)

    await database.connect()
    await tokenQueue.connect()
    query = (
        sqlalchemy.select(CollectionHourlyActivitiesTable.c.address, CollectionHourlyActivitiesTable.c.date)
        .where(CollectionHourlyActivitiesTable.c.mintCount == 0)
    )
    result = await database.execute(query=query)
    registryDatePairs = list(result)
    print(registryDatePairs)
    for pairChunk in list_util.generate_chunks(lst=registryDatePairs, chunkSize=50):
        print(pairChunk)
        await asyncio.gather(*[collectionActivityManager.update_activity_for_collection(address=registryAddress, startDate=startDate) for registryAddress, startDate in pairChunk])
    

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_collection_activities())
