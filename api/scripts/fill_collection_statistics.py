from api.notd.manager import NotdManager
from api.notd.token_manager import TokenManager
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
from core.util import list_util

from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import date_util
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

#TODO USE CLICK
#async def refill_collection_statistics(startDate: datetime.date, endDate: datetime.date, batchHourSize: int):
async def refill_collection_statistics(startBlock: int, endBlock: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    tokenQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None, collectionActivityProcessor=collectionActivityProcessor)
    notdManager = NotdManager(blockProcessor=None, saver=saver, retriever=retriever, workQueue=tokenQueue, tokenManager=tokenManager, requester=None, revueApiKey=None )

    await database.connect()
    await tokenQueue.connect()
    currentBlockNumber = startBlock
    while currentBlockNumber < endBlock:
        print(currentBlockNumber < endBlock, currentBlockNumber, endBlock)
        start = currentBlockNumber
        end = start + batchSize

        logging.info(f'Working on {start} to {end}...')
        tokenTransfers = await retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(BlocksTable.c.blockNumber.key, gte=start),
                DateFieldFilter(BlocksTable.c.blockNumber.key, lt=end),
            ],
        )
    # currentDate = startDate
    # while currentDate < endDate:
    #     print(currentDate < endDate, currentDate, endDate)
    #     start = currentDate
    #     end = date_util.datetime_from_datetime(dt=currentDate, hours=batchHourSize)

    #     logging.info(f'Working on {start} to {end}...')
    #     tokenTransfers = await retriever.list_token_transfers(
    #         fieldFilters=[
    #             DateFieldFilter(BlocksTable.c.blockDate.key, gte=start),
    #             DateFieldFilter(BlocksTable.c.blockDate.key, lt=end),
    #         ],
    #     )
        pairs = {(tokenTransfer.registryAddress, date_hour_from_datetime(tokenTransfer.blockDate)) for tokenTransfer in tokenTransfers}
        #TODO FEMI-OGUNKOLA: DO this in Parallel for groups of 20
        for pairChunk in list_util.generate_chunks(lst=list(pairs), chunkSize=20):
            await asyncio.gather(*[notdManager.update_activity_for_collection(registryAddress=registryAddress, startDate=startDate) for registryAddress, startDate in pairChunk])
        
        currentDate = end

    await database.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(refill_collection_statistics(startDate=date_util.datetime_from_now(
        days=-14).replace(minute=0, second=0, microsecond=0), endDate=date_util.datetime_from_now().replace(minute=0, second=0, microsecond=0), batchHourSize=1))
