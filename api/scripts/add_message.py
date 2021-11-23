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
    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

    await database.connect()
    cache =set()
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
                cache.add((tokenTransfer.registryAddress,tokenTransfer.tokenId))
        currentBlockNumber = currentBlockNumber + batchSize
        collectionSet = set()
        for i in range(len(cache)):
            registryAddress = list(list(cache)[i])[0]
            tokenId = list(list(cache)[i])[1]
            await workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())
            collectionSet.add(registryAddress)
        for address in collectionSet:
            await workQueue.send_message(message=UpdateCollectionMessageContent(address=address).to_message())

    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(add_message())
