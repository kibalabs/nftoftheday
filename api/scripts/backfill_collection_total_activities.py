import asyncio
import logging
import os
import sys

import asyncclick as click
import sqlalchemy
import tqdm
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
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import TokenCollectionsTable


async def update_total_activity_for_collection(activityManager: ActivityManager, address: str) -> None:
    await activityManager.update_total_activity_for_collection(address=address)

@click.command()
async def backfill_collection_activities_mint_count():
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

    collectionAddressesQuery = (
        sqlalchemy.select(TokenCollectionsTable.c.address)  # type: ignore[no-untyped-call]
    )
    collectionAddressResults = await retriever.database.execute(query=collectionAddressesQuery)
    collectionAddresses = {registryAddress for (registryAddress, ) in collectionAddressResults}
    print(f'Got {len(collectionAddresses)} collectionAddresses')
    collectionAddressesCompletedQuery = (
        sqlalchemy.select(CollectionTotalActivitiesTable.c.address)  # type: ignore[no-untyped-call]
        .where(CollectionTotalActivitiesTable.c.mintCount != None)
    )
    collectionAddressesCompletedResults = await retriever.database.execute(query=collectionAddressesCompletedQuery)
    collectionAddressesCompleted = {registryAddress for (registryAddress, ) in collectionAddressesCompletedResults}
    print(f'Got {len(collectionAddressesCompleted)} collectionAddressesCompleted')
    collectionsToProcess = collectionAddresses - collectionAddressesCompleted
    print(f'Got {len(collectionsToProcess)} collectionsToProcess')
    # messages = [UpdateActivityForCollectionMessageContent(address=address, startDate=startDate).to_message() for (address, startDate) in registryDatePairs]
    # await tokenQueue.send_messages(messages=messages)
    for pairChunk in tqdm.tqdm(list_util.generate_chunks(lst=list(collectionsToProcess), chunkSize=50)):
        await asyncio.gather(*[update_total_activity_for_collection(activityManager=activityManager, address=registryAddress) for registryAddress in pairChunk])

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_collection_activities_mint_count())
