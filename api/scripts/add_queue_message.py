import os
import sys

import boto3

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue
from databases.core import Database

from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def add_message(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    #sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    #workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    sqsClient = boto3.client(service_name='sqs', region_name='us-east-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    await database.connect()
    cache = set()
    registryCache = set()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            await database.connect()
            query = TokenTransfersTable.select()
            query = query.where(TokenTransfersTable.c.blockNumber >= start)
            query = query.where(TokenTransfersTable.c.blockNumber < end)
            query = query.where(TokenTransfersTable.c.registryAddress.in_(
                TokenTransfersTable.select()
                .with_only_columns([TokenTransfersTable.c.registryAddress])
                    .group_by(TokenTransfersTable.c.registryAddress)
            ))
            tokenTransfersToChange = [token_transfer_from_row(row) async for row in database.iterate(query=query)]
            for tokenTransfer in tokenTransfersToChange:
                if (tokenTransfer.registryAddress, tokenTransfer.tokenId) in cache:
                    pass
                else:
                    cache.add((tokenTransfer.registryAddress,tokenTransfer.tokenId))
                    await workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=tokenTransfer.registryAddress, tokenId=tokenTransfer.tokenId).to_message())
                    if tokenTransfer.registryAddress in registryCache:
                        pass
                    else:
                        await workQueue.send_message(message=UpdateCollectionMessageContent(address=tokenTransfer.registryAddress).to_message())

        logging.info(f'Found {len(cache)} unique tokens between {startBlockNumber} and {end}')
        currentBlockNumber = currentBlockNumber + batchSize
    

    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(add_message())
