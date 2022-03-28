import asyncio
import logging
import os
import sys
from typing import Sequence

import asyncclick as click
import sqlalchemy
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.database import Database
from core.store.retriever import StringFieldFilter
from core.util import list_util
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_processor import CollectionProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor


async def _update_token_metadatas(tokensToProcess: Sequence[tuple], tokenManager: TokenManager, retriever: Retriever):
    query = (
        TokenMetadataTable.select()
            .where(sqlalchemy.tuple_(TokenMetadataTable.c.registryAddress, TokenMetadataTable.c.tokenId).in_(tokensToProcess))
    )
    recentlyUpdatedTokenMetadatas = await retriever.query_token_metadatas(query=query)
    recentlyUpdatedTokenIds = set((tokenMetadata.registryAddress, tokenMetadata.tokenId) for tokenMetadata in recentlyUpdatedTokenMetadatas)
    tokensToUpdate = set(tokensToProcess) - recentlyUpdatedTokenIds
    print('len(tokensToUpdate)', len(tokensToUpdate))
    for tokensToUpdateChunk in list_util.generate_chunks(lst=list(tokensToUpdate), chunkSize=10):
        tokenProcessResults = await asyncio.gather(*[tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId) for (registryAddress, tokenId) in tokensToUpdateChunk], return_exceptions=True)
        tokenProcessSuccessCount = tokenProcessResults.count(None)
        if tokenProcessSuccessCount:
            print(f'{tokenProcessSuccessCount} / {len(tokenProcessResults)} token updates succeeded')
        # NOTE(krishan711): if less than 90% of things succeed, bail out
        if len(tokenProcessResults) >= 100 and tokenProcessSuccessCount / len(tokenProcessResults) < 0.9:
            raise Exception('Less than 90% of token updates failed!')


async def _update_collections(collectionsToProcess: Sequence[str], tokenManager: TokenManager, retriever: Retriever):
    recentlyUpdatedCollections = await retriever.list_collections(
        fieldFilters=[
            StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, containedIn=collectionsToProcess),
        ],
    )
    recentlyUpdatedAddresses = set(collection.address for collection in recentlyUpdatedCollections)
    collectionsToUpdate = set(collectionsToProcess) - recentlyUpdatedAddresses
    print('len(collectionsToUpdate)', len(collectionsToUpdate))
    for collectionsToUpdateChunk in list_util.generate_chunks(lst=list(collectionsToUpdate), chunkSize=50):
        collectionProcessResults = await asyncio.gather(*[tokenManager.update_collection(address=address) for address in collectionsToUpdateChunk], return_exceptions=True)
        collectionProcessSuccessCount = collectionProcessResults.count(None)
        if collectionProcessSuccessCount:
            print(f'{collectionProcessSuccessCount} / {len(collectionProcessResults)} collection updates succeeded')
        # NOTE(krishan711): if less than 90% of things succeed, bail out
        if len(collectionProcessResults) >= 100 and collectionProcessSuccessCount / len(collectionProcessResults) < 0.9:
            raise Exception('Less than 90% of collection updates failed!')


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
    tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor, tokenOwnershipProcessor=tokenOwnershipProcessor)
    revueApiKey = os.environ['REVUE_API_KEY']

    await database.connect()
    await workQueue.connect()
    await s3manager.connect()
    await tokenQueue.connect()
    cache = set()
    registryCache = set()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start}-{end}...')
        query = (
             sqlalchemy.select(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
             .where(TokenTransfersTable.c.blockNumber >= start)
             .where(TokenTransfersTable.c.blockNumber < end)
         )
        result = await database.execute(query=query,)
        tokensToProcess = set()
        collectionsToProcess = set()
        for (registryAddress, tokenId) in result:
            if (registryAddress, tokenId) in cache:
                continue
            cache.add((registryAddress, tokenId))
            tokensToProcess.add((registryAddress, tokenId))
            if registryAddress in registryCache:
                continue
            registryCache.add(registryAddress)
            collectionsToProcess.add(registryAddress)
        print('len(tokensToProcess)', len(tokensToProcess))
        print('len(collectionsToProcess)', len(collectionsToProcess))
        try:
            await _update_token_metadatas(tokensToProcess=tokensToProcess, tokenManager=tokenManager, retriever=retriever)
            await _update_collections(collectionsToProcess=collectionsToProcess, tokenManager=tokenManager, retriever=retriever)
        except:
            logging.error(f'Failed during: {start}-{end}')
            raise
        currentBlockNumber = end
    await database.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()
    await s3manager.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(add_message())
