import asyncio
import logging
import os
import sys
from unittest import result

import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.database import Database
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.util import list_util
import sqlalchemy

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.date_util import date_hour_from_datetime
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema_conversions import token_transfer_from_row
from notd.token_manager import TokenManager


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=500)
async def backfill_token_transfers_date(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None, collectionActivityProcessor=collectionActivityProcessor)

    await database.connect()
    await tokenQueue.connect()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {currentBlockNumber} to {endBlockNumber}...')
        async with saver.create_transaction() as connection:
            query = (
                sqlalchemy.select([TokenTransfersTable.c.tokenTransferId, BlocksTable.c.createdDate, BlocksTable.c.updatedDate]).join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                .filter(TokenTransfersTable.c.blockNumber >= start)
                .filter(TokenTransfersTable.c.blockNumber < end)
                .where(TokenTransfersTable.c.createdDate == None)
                .where(TokenTransfersTable.c.updatedDate == None)
            )
            result = await database.execute(query=query)
            tokenTransfersToChange = [(row[0], row[1], row[2]) for row in result]
            logging.info(f'Updating {len(tokenTransfersToChange)} transfers...')
            for tokenTransferId, createdDate, updatedDate in tokenTransfersToChange:
                    values = {
                        TokenTransfersTable.c.createdDate.key: createdDate,
                        TokenTransfersTable.c.updatedDate.key: updatedDate,
                    }
                    query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenTransferId).values(values)
                    await database.execute(query=query, connection=connection)

        currentBlockNumber = endBlockNumber

    await database.disconnect()
    await tokenQueue.disconnect()
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_token_transfers_date())
