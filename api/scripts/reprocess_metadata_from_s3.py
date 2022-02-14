from datetime import datetime
import json
import os
import sys
import time
from typing import Optional
from api.notd.store.retriever import Retriever

from api.notd.token_manager import TokenManager 

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
@click.option('-s', '--start-id-number', 'startId', required=False, type=int)
@click.option('-e', '--end-id-number', 'endId', required=False, type=int)
async def reprocess_metadata(startId: Optional[int], endId: Optional[int]):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    #sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    tokenManger = TokenManager(saver=saver, retriever=retriever, tokenQueue=None, collectionProcessor=None, tokenMetadataProcessor=None)
    
    await database.connect()
    query = TokenMetadataTable.select()
    if startId:
        query = query.where(TokenMetadataTable.c.tokenMetadataId >= startId)
    if endId:
        query = query.where(TokenMetadataTable.c.tokenMetadataId < endId)    
    tokenMetadatasToChange = [token_metadata_from_row(row) async for row in database.iterate(query=query)]
    logging.info(f'Updating {len(tokenMetadatasToChange)} transfers...')
    for tokenMetadata in tokenMetadatasToChange:
        tokenDirectory = f'{os.environ["S3_BUCKET"]}/token-metadatas/{tokenMetadata.registryAddress}/{tokenMetadata.tokenId}/'
        #print(tokenDirectory)
        tokenFile = None
        tokenMetadataFiles = [file async for file in s3manager.generate_directory_files(s3Directory=tokenDirectory)]
        if len(tokenMetadataFiles) > 0:
            tokenFile=(tokenMetadataFiles[len(tokenMetadataFiles)-1])
        if tokenFile:
            tokenMetadataJson = await s3manager.read_file(sourcePath=f'{tokenFile.bucket}/{tokenFile.path}')
            tokenMetadataDict = json.loads(tokenMetadataJson)
            logging.info(f'Processed: {tokenMetadata.tokenMetadataId}')
            await tokenManger.update_token_metadata()
           
                # await workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId).to_message())
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata())
