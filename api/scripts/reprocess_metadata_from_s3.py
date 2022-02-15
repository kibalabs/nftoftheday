import asyncio
import json
import logging
import os
import sys
from typing import Optional

import asyncclick as click
import boto3
from core.s3_manager import S3Manager
from core.store.database import Database
from core.requester import Requester
from core.s3_manager import S3Manager
from core.aws_requester import AwsRequester
from core.store.database import Database
from core.web3.eth_client import RestEthClient
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable
from notd.store.schema_conversions import token_metadata_from_row
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.collection_processor import CollectionProcessor
from notd.model import TokenMetadata

from core.util import list_util



async def _reprocess_batch(tokenManger: TokenManager, retrievedTokenMetadata: TokenMetadata): 
    logging.info(f'Updating Token {(retrievedTokenMetadata.registryAddress)},TokenId {retrievedTokenMetadata.tokenId}')
    await tokenManger.save_token_metadata(retrievedTokenMetadata=retrievedTokenMetadata)
    #logging.info(f'Saving Token Metadata for {retrievedTokenMetadata.tokenMetadataId}')
    #await tokenManger.update_token_metadata(registryAddress=retrievedTokenMetadata.registryAddress, tokenId=retrievedTokenMetadata.tokenId, shouldForce=True)


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=False, type=int)
@click.option('-e', '--end-id-number', 'endId', required=False, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)

async def reprocess_metadata(startId: Optional[int], endId: Optional[int], batchSize: Optional[int]):

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    tokenQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    s3manager = S3Manager(s3Client=s3Client)
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    requester = Requester()
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    requester = Requester()
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    openseaApiKey = os.environ['OPENSEA_API_KEY']
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    tokenManger = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor)

    await database.connect()
    currentId = startId
    while currentId < endId:
        start = currentId
        end = min(currentId + batchSize, endId)
        logging.info(f'Working on {start} to {end}...')
        query = TokenMetadataTable.select()
        query = query.where(TokenMetadataTable.c.tokenMetadataId >= start)
        query = query.where(TokenMetadataTable.c.tokenMetadataId < end)
        query = query.order_by(TokenMetadataTable.c.tokenMetadataId.asc())
        tokenMetadatasToChange = [token_metadata_from_row(row) for row in await database.execute(query=query)]
        s3TokenMetadata = []
        logging.info(f'Updating {len(tokenMetadatasToChange)} transfers...')
        for tokenMetadata in tokenMetadatasToChange:
            tokenDirectory = f'{os.environ["S3_BUCKET"]}/token-metadatas/{tokenMetadata.registryAddress}/{tokenMetadata.tokenId}/'
            tokenFile = None
            tokenMetadataFiles = [file async for file in s3manager.generate_directory_files(s3Directory=tokenDirectory)]
            if len(tokenMetadataFiles) > 0:
                tokenFile=(tokenMetadataFiles[len(tokenMetadataFiles)-1])
                tokenMetadataJson = await s3manager.read_file(sourcePath=f'{tokenFile.bucket}/{tokenFile.path}')
                tokenMetadataDict = json.loads(tokenMetadataJson)
                s3TokenMetadata += [await tokenMetadataProcessor._get_token_metadata_from_data(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, metadataUrl=tokenMetadata.metadataUrl, tokenMetadataDict=tokenMetadataDict)]

        for batch in list_util.generate_chunks(s3TokenMetadata, chunkSize=10):
            await asyncio.gather(*[_reprocess_batch(tokenManger=tokenManger, retrievedTokenMetadata=retrievedTokenMetadata) for retrievedTokenMetadata in batch])
            print("done")
        currentId = currentId + batchSize

    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata())
