from notd.store.schema import TokenTransfersTable, BlocksTable
from notd.store.saver import Saver
from notd.store.retriever import Retriever
from notd.messages import UpdateActivityForCollectionMessageContent
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.date_util import date_hour_from_datetime
import asyncio
import sys
import os
import logging
import datetime

from core.util import date_util
from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import date_util
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


async def refill_collection_statistics(startDate: datetime.date, endDate: datetime.date, period: int):
    databaseConnectionString = Database.create_psql_connection_string(
        username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    tokenQueue = SqsMessageQueue(
        region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    collectionStatisticsProcessor = CollectionActivityProcessor(
        retriever=retriever)

    await database.connect()
    await tokenQueue.connect()
    currentDate = startDate
    while currentDate < endDate:
        print(currentDate < endDate, currentDate, endDate)
        start = currentDate
        end = date_util.datetime_from_datetime(dt=currentDate, hours=period)

        logging.info(f'Working on {start} to {end}...')
        tokenTransfers = await retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(BlocksTable.c.blockDate.key, gte=start),
                DateFieldFilter(BlocksTable.c.blockDate.key, lt=end),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key,
                          direction=Direction.DESCENDING)],
        )
        pairs = list(set([(tokenTransfer.registryAddress, date_util.datetime_from_datetime(
            date_hour_from_datetime(tokenTransfer.blockDate), hours=1)) for tokenTransfer in tokenTransfers]))
        # DO this in Parallel for groups of 20
        await tokenManger.update_activity_for_collection()
        async with saver.create_transaction() as connection:
            for pair in pairs:
                collectionActivity = await collectionStatisticsProcessor.calculate_collection_hourly_activity(registryAddress=pair[0], date=pair[1])
                await saver.create_collection_hourly_activity(connection=connection, address=collectionActivity.address, date=collectionActivity.date, transferCount=collectionActivity.transferCount, saleCount=collectionActivity.saleCount, totalVolume=collectionActivity.totalVolume, minimumValue=collectionActivity.minimumValue, maximumValue=collectionActivity.maximumValue, averageValue=collectionActivity.averageValue,)
        currentDate = end

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(refill_collection_statistics(startDate=date_util.datetime_from_now(
        days=-14).replace(minute=0, second=0, microsecond=0), endDate=date_util.datetime_from_now().replace(minute=0, second=0, microsecond=0), period=1))
