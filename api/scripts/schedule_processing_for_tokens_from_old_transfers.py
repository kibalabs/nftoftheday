import asyncio
import logging
import os
import sys

import sqlalchemy
import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue
from core.aws_requester import AwsRequester
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.database import Database
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_processor import CollectionProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

async def _add_messages(pair: tuple, tokensToProcess: set, collectionsToProcess: set, tokenManager: TokenManager, cache: set, registryCache: set):
    if pair in cache:
        pass
    cache.add(pair)
    tokensToProcess.add(pair)
    if pair[0] in registryCache:
        pass
    registryCache.add(pair[0])
    collectionsToProcess.add(pair[0])
    print('len(tokensToProcess)', len(tokensToProcess))
    print('len(collectionsToProcess)', len(collectionsToProcess))
    await tokenManager.update_token_metadata(registryAddress=pair[0], tokenId=pair[1])
    await tokenManager.update_collections_deferred(addresses=list(collectionsToProcess))

@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def add_message(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    s3manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    requester = Requester()
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    openseaApiKey = os.environ['OPENSEA_API_KEY']
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor)

    await database.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    cache = set()
    registryCache = set()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        query = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
            .where(TokenTransfersTable.c.blockNumber >= start)
            .where(TokenTransfersTable.c.blockNumber < end)
        )
        result = await database.execute(query=query,)
        tokensToProcess = set()
        collectionsToProcess = set()
        await asyncio.gather(*[_add_messages(pair=(registryAddress, tokenId),tokenManager=tokenManager, tokensToProcess=tokensToProcess, collectionsToProcess=collectionsToProcess ,cache=cache, registryCache=registryCache) for (registryAddress,tokenId) in result])
        currentBlockNumber = end
        
    await database.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(add_message())
