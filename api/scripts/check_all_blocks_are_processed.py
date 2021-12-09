import os
import sys

import boto3
from core.queues.sqs_message_queue import SqsMessageQueue



sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from databases.core import Database
from sqlalchemy.sql.expression import distinct, func as sqlalchemyfunc
from notd.messages import ProcessBlocksMessageContent

from notd.store.schema_conversions import token_transfer_from_row

from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def check_all_processed(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    #database = Database(f'postgresql://{os.environ["REMOTE_DB_USERNAME"]}:{os.environ["REMOTE_DB_PASSWORD"]}@{os.environ["REMOTE_DB_HOST"]}:{os.environ["REMOTE_DB_PORT"]}/{os.environ["REMOTE_DB_NAME"]}')
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')#pylint: disable=invalid-name
    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    blocks_processed = []
    await database.connect()

    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenTransfersTable.select().with_only_columns([TokenTransfersTable.c.blockNumber]).distinct(TokenTransfersTable.c.blockNumber)
            rows = await database.fetch_all(query)
            for row in rows:
                blocks_processed.append(row[0])
        currentBlockNumber = currentBlockNumber + batchSize
    await database.disconnect()
    notProcessed = set(range(startBlockNumber,endBlockNumber)) - set(blocks_processed)
    await workQueue.send_message(message=ProcessBlocksMessageContent(blockNumbers=notProcessed).to_message())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(check_all_processed())
