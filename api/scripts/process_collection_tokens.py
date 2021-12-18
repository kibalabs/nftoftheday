import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging
import os

import asyncclick as click
import boto3
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.retriever import StringFieldFilter
from core.web3.eth_client import RestEthClient
from databases import Database

from notd.block_processor import BlockProcessor
from notd.collection_processor import CollectionProcessor
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable
from notd.token_client import TokenClient
from notd.token_metadata_processor import TokenMetadataProcessor


@click.command()
@click.option('-a', '--collection-address', 'address', required=True, type=str)
@click.option('-d', '--defer', 'shouldDefer', default=False, is_flag=True)
async def process_collection(address: str, shouldDefer: bool):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = Retriever(database=database)

    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    s3Client = boto3.client(service_name='s3', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    requester = Requester()
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    openseaClient = OpenseaClient(requester=requester)
    tokenClient = TokenClient(requester=requester, ethClient=ethClient)
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient)

    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, openseaClient=openseaClient, tokenClient=tokenClient, requester=requester, tokenMetadataProcessor=tokenMetadataProcessor, collectionProcessor=collectionProcessor, revueApiKey=None)

    await database.connect()
    retrievedCollectionTokenMetadatas = await retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=address),
            ],
        )
    for tokenMetadata in range(len(retrievedCollectionTokenMetadatas)):
        tokenId = retrievedCollectionTokenMetadatas[tokenMetadata].tokenId
        if shouldDefer:
            await notdManager.update_token_metadata_deferred(registryAddress=address, tokenId=tokenId, shouldForce=True)
        else:
            await notdManager.update_token_metadata(registryAddress=address, tokenId=tokenId, shouldForce=True)
    await database.disconnect()
    await requester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(process_collection())
