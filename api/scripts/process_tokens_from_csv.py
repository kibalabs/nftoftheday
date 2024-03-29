import asyncio
import os
import sys
from csv import DictReader

import asyncclick as click
from core import logging
from core.aws_requester import AwsRequester
from core.queues.sqs import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.database import Database
from core.util import list_util
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_processor import CollectionProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor


async def process_token_metadata(tokenManager: TokenManager, registryAddress: str, tokenId: str):
    print(registryAddress, tokenId)
    await tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=True)


@click.command()
@click.option('-f', '--file', 'inputFilePath', required=True, type=str)
async def run(inputFilePath: str):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    requester = Requester()
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3Manager=s3Manager, bucketName=os.environ['S3_BUCKET'])
    openseaApiKey = os.environ['OPENSEA_API_KEY']
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3Manager=s3Manager, bucketName=os.environ['S3_BUCKET'])
    tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor, tokenOwnershipProcessor=tokenOwnershipProcessor, collectionActivityProcessor=collectionActivityProcessor)

    await database.connect()
    await s3Manager.connect()
    await tokenQueue.connect()
    try:
        with open(inputFilePath, 'r') as inputFile:
            tokensToUpdate = list(DictReader(inputFile, delimiter='\t'))
        for tokensToUpdateSublist in list_util.generate_chunks(lst=tokensToUpdate, chunkSize=10):
            await asyncio.gather(*[process_token_metadata(tokenManager=tokenManager, registryAddress=tokenToUpdate['registry_address'], tokenId=tokenToUpdate['token_id']) for tokenToUpdate in tokensToUpdateSublist])
    finally:
        await database.disconnect()
        await s3Manager.disconnect()
        await tokenQueue.disconnect()
        await requester.close_connections()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
