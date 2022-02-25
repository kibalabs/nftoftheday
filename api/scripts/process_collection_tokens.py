import asyncio
import logging
import os
import sys

import asyncclick as click
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.database import Database
from core.store.retriever import StringFieldFilter
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_processor import BlockProcessor
from notd.collection_processor import CollectionProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor


@click.command()
@click.option('-a', '--collection-address', 'address', required=True, type=str)
@click.option('-d', '--defer', 'shouldDefer', default=False, is_flag=True)
async def process_collection(address: str, shouldDefer: bool):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)

    s3manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    requester = Requester()

    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    openseaApiKey = os.environ['OPENSEA_API_KEY']
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    revueApiKey = os.environ['REVUE_API_KEY']
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, tokenManager=tokenManager, requester=requester, revueApiKey=revueApiKey)

    await database.connect()
    await s3manager.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    retrievedCollectionTokenMetadatas = await retriever.list_token_metadatas(
        fieldFilters=[
            StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=address),
        ],
    )
    for tokenMetadata in retrievedCollectionTokenMetadatas:
        if shouldDefer:
            await notdManager.update_token_metadata_deferred(registryAddress=address, tokenId=tokenMetadata.tokenId, shouldForce=True)
        else:
            await notdManager.update_token_metadata(registryAddress=address, tokenId=tokenMetadata.tokenId, shouldForce=True)
    await database.disconnect()
    await s3manager.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()
    await requester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(process_collection())
