import asyncio
import logging
import os
import sys

import asyncclick as click
import sqlalchemy
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def add_message(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

    await database.connect()
    await workQueue.connect()
    cache = set()
    registryCache = set()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenTransfersTable.select()
            query = query.where(TokenTransfersTable.c.blockNumber >= start)
            query = query.where(TokenTransfersTable.c.blockNumber < end)
            query = query.where(sqlalchemy.tuple_(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId).not_in(
                TokenMetadataTable.select()
                    .with_only_columns([TokenMetadataTable.c.registryAddress,TokenMetadataTable.c.tokenId])
                    .group_by(TokenMetadataTable.c.registryAddress,TokenMetadataTable.c.tokenId)
            ))
            tokenTransfersToChange = [token_transfer_from_row(row) async for row in database.iterate(query=query)]
            for tokenTransfer in tokenTransfersToChange:
                if (tokenTransfer.registryAddress, tokenTransfer.tokenId) in cache:
                    continue
                cache.add((tokenTransfer.registryAddress, tokenTransfer.tokenId))
                await workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=tokenTransfer.registryAddress, tokenId=tokenTransfer.tokenId).to_message())
                if tokenTransfer.registryAddress in registryCache:
                    continue
                registryCache.add(tokenTransfer.registryAddress)
                await workQueue.send_message(message=UpdateCollectionMessageContent(address=tokenTransfer.registryAddress).to_message())
        currentBlockNumber = currentBlockNumber + batchSize
    await database.disconnect()
    await workQueue.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(add_message())
