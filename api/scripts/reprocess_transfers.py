import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
import boto3
from core.queues.sqs_message_queue import SqsMessageQueue
from databases.core import Database

# from notd.messages import UpdateTokenMetadataMessageContent
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable, TokenTransfersTable
from notd.store.schema_conversions import token_metadata_from_row, token_transfer_from_row
from notd.token_metadata_processor import TokenMetadataProcessor


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=True, type=int)
@click.option('-e', '--end-id-number', 'endId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def reprocess_metadata(startId: int, endId: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database)
    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

    await database.connect()

    currentId = startId
    while currentId < endId:
        start = currentId
        end = min(currentId + batchSize, endId)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenTransfersTable.select()
            query = query.where(TokenTransfersTable.c.tokenTransfersId >= start)
            query = query.where(TokenTransfersTable.c.tokenTransfersId < end)
            query = query.where(TokenTransfersTable.c.tokenType == None)
            tokenTransfersToUpdate = [token_transfer_from_row(row) async for row in database.iterate(query=query)]
            logging.info(f'Updating {len(tokenTransfersToUpdate)} transfers...')
            for tokenTransfers in tokenTransfersToUpdate:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransfersId == tokenTransfers)
                values = {}
                values[TokenTransfersTable.c.tokenType.key] = 'erc721single'
                values[TokenTransfersTable.c.amount.key] = 1
            await database.execute(query=query, values=values)

        currentId = currentId + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata())
