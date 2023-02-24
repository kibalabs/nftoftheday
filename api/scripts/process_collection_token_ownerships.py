import asyncio
import os
import sys
import time

import asyncclick as click
import sqlalchemy
from core import logging
from core.aws_requester import AwsRequester
from core.queues.sqs import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.slack_client import SlackClient
from core.store.database import Database
from core.util import chain_util
from core.util import list_util
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_processor import CollectionProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenOwnershipsTable
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor


# Initial run from -s 0 -e 50000000 -b 100
async def process_token_ownership(tokenManager: TokenManager, registryAddress: str, tokenId: str) -> None:
    print(f'Updating ownership for {registryAddress}/{tokenId}')
    await tokenManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId)


@click.command()
@click.option('-c', '--collection-adderss', 'collectionAddress', required=True, type=str)
async def process_collection_token_ownerships(collectionAddress: str):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    requester = Requester()
    tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
    tokenManager = TokenManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=tokenOwnershipProcessor, collectionActivityProcessor=None, tokenListingProcessor=None, tokenAttributeProcessor=None)

    await database.connect()
    await workQueue.connect()
    await s3Manager.connect()
    await tokenQueue.connect()
    await database.connect()

    collectionAddress = chain_util.normalize_address(value=collectionAddress)

    query = (
        TokenMetadatasTable.select()
            .join(TokenOwnershipsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenOwnershipsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenOwnershipsTable.c.tokenId), isouter=True)
            .where(TokenMetadatasTable.c.registryAddress == collectionAddress)
            .where(TokenOwnershipsTable.c.tokenOwnershipId == None)
    )
    tokenMetadatas = await retriever.query_token_metadatas(query=query)
    print(f'Found {len(tokenMetadatas)} token ownerships to create')
    for tokenMetadataChunk in list_util.generate_chunks(lst=tokenMetadatas, chunkSize=10):
        await asyncio.gather(*[process_token_ownership(tokenManager=tokenManager, registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId) for tokenMetadata in tokenMetadataChunk])

    await database.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()
    await s3Manager.disconnect()
    await requester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(process_collection_token_ownerships())
