import asyncio
import logging
import os
import sys
import time

import asyncclick as click
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.slack_client import SlackClient
from core.store.database import Database
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_processor import CollectionProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor


# Initial run from -s 0 -e 50000000 -b 100
async def process_token_ownership(tokenManager: TokenManager, registryAddress: str, tokenId: str) -> None:
    await tokenManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId)


@click.command()
@click.option('-s', '--start-token-id', 'startTokenId', required=True, type=int)
@click.option('-e', '--end-token-id', 'endTokenId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def process_token_ownerships(startTokenId: int, endTokenId: int, batchSize: int):
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
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')

    await database.connect()
    await workQueue.connect()
    await s3manager.connect()
    await tokenQueue.connect()

    await database.connect()
    await slackClient.post(text=f'process_token_ownerships → 🚧 started: {startTokenId}-{endTokenId}')
    try:
        currentTokenId = startTokenId
        while currentTokenId < endTokenId:
            start = currentTokenId
            end = min(currentTokenId + batchSize, endTokenId)
            currentTokenId = end
            logging.info(f'Working on {start}-{end}')
            query = TokenMetadataTable.select() \
                .where(TokenMetadataTable.c.tokenMetadataId >= start) \
                .where(TokenMetadataTable.c.tokenMetadataId < end)
            tokenMetadatas = await retriever.query_token_metadatas(query=query)
            await asyncio.gather(*[process_token_ownership(tokenManager=tokenManager, registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId) for tokenMetadata in tokenMetadatas])
        await slackClient.post(text=f'process_token_ownerships → ✅ completed : {startTokenId}-{endTokenId}')
    except Exception as exception:
        await slackClient.post(text=f'process_token_ownerships → ❌ error: {startTokenId}-{endTokenId}\n```{str(exception)}```')
        raise exception
    finally:
        await database.disconnect()
        await workQueue.disconnect()
        await tokenQueue.disconnect()
        await s3manager.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(process_token_ownerships())
