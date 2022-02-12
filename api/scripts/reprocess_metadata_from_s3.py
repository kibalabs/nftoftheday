from datetime import datetime
import json
import os
import sys
import time 

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
import boto3
from core.queues.sqs_message_queue import SqsMessageQueue
from core.s3_manager import S3Manager
from core.util import date_util

from databases.core import Database

# from notd.messages import UpdateTokenMetadataMessageContent
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable
from notd.store.schema_conversions import token_metadata_from_row
from notd.token_metadata_processor import TokenMetadataProcessor


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=True, type=int)
@click.option('-e', '--end-id-number', 'endId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def reprocess_metadata(startId: int, endId: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database)
    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
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
            tokenMetadatasToChange = [token_metadata_from_row(row) async for row in database.iterate(query=query)]
            logging.info(f'Updating {len(tokenMetadatasToChange)} transfers...')
            for tokenMetadata in tokenMetadatasToChange:
                tokenDirectory = f'{os.environ["S3_BUCKET"]}/token-metadatas/{tokenMetadata.registryAddress}/{tokenMetadata.tokenId}/'
                #print(tokenDirectory)
                tokenFile = None
                a = [file async for file in s3manager.generate_directory_files(s3Directory=tokenDirectory)]
                if len(a) > 0:
                    tokenFile=(a[len(a)-1])
                if tokenFile:
                    try:
                        tokenMetadataDict = json.loads(await s3manager.read_file(sourcePath=f'{tokenFile.bucket}/{tokenFile.path}'))
                        if tokenMetadataDict:
                            logging.info(f'Processed: {tokenMetadata.tokenMetadataId}')
                            await saver.update_token_metadata(tokenMetadataId=tokenMetadata.tokenMetadataId, animationUrl=tokenMetadataDict.get('animation_url') ,backgroundColor=tokenMetadataDict.get('background_color'), youtubeUrl=tokenMetadataDict.get('youtube_url'))
                    except Exception as e:
                        logging.exception(f'Error processing {tokenMetadata.tokenMetadataId}: {e}')
                        # await workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId).to_message())
        currentId = currentId + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata())
