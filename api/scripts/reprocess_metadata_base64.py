import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import base64
import json
import logging

import asyncclick as click
import boto3
from core.queues.sqs_message_queue import SqsMessageQueue
from databases.core import Database

from notd.messages import UpdateTokenMetadataMessageContent
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable
from notd.store.schema_conversions import token_metadata_from_row


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=True, type=int)
@click.option('-e', '--end-id-number', 'endId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def reprocess_metadata_base64(startId: int, endId: int, batchSize: int):
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
            query = TokenMetadataTable.select()
            query = query.where(TokenMetadataTable.c.tokenMetadataId >= start)
            query = query.where(TokenMetadataTable.c.tokenMetadataId < end)
            query = query.where(TokenMetadataTable.c.metadataUrl.startswith('data:application/json;base64,'))
            query = query.where(TokenMetadataTable.c.name == None)
            tokenMetadatasToChange = [token_metadata_from_row(row) async for row in database.iterate(query=query)]
            logging.info(f'Updating {len(tokenMetadatasToChange)} transfers...')
            for tokenMetadata in tokenMetadatasToChange:
                try:
                    basestr = tokenMetadata.metadataUrl.replace('data:application/json;base64,', '', 1)
                    base64Metadata = basestr.encode('utf-8')
                    metadataBytes = base64.b64decode(base64Metadata)
                    tokenMetadataDict = json.loads(metadataBytes.decode('utf-8'))
                    await saver.update_token_metadata(tokenMetadataId=tokenMetadata.tokenMetadataId, name=tokenMetadataDict.get('name') ,imageUrl=tokenMetadataDict.get('image'), description=tokenMetadataDict.get('description'), attributes=tokenMetadataDict.get('attributes', []))
                except Exception as e:
                    logging.exception(f'Error processing {tokenMetadata.tokenMetadataId}: {e}')
                    await workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId).to_message())
        currentId = currentId + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata_base64())
