import asyncio
import os
import time

from core import logging
from core.aws_requester import AwsRequester
from core.queues.message_queue_processor import MessageQueueProcessor
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.slack_client import SlackClient
from core.store.database import Database
from core.util.value_holder import RequestIdHolder
from core.web3.eth_client import RestEthClient

from notd.block_processor import BlockProcessor
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_processor import CollectionProcessor
from notd.manager import NotdManager
from notd.notd_message_processor import NotdMessageProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_attributes_processor import TokenAttributeProcessor
from notd.token_listing_processor import TokenListingProcessor
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor


async def main():
    requestIdHolder = RequestIdHolder()
    name = os.environ.get('NAME', 'notd-api')
    version = os.environ.get('VERSION', 'local')
    environment = os.environ.get('ENV', 'dev')
    isRunningDebugMode = environment == 'dev'

    if isRunningDebugMode:
        logging.init_basic_logging()
    else:
        logging.init_json_logging(name=name, version=version, environment=environment, requestIdHolder=requestIdHolder)

    openseaApiKey = os.environ['OPENSEA_API_KEY']
    revueApiKey = os.environ['REVUE_API_KEY']
    accessKeyId = os.environ['AWS_KEY']
    accessKeySecret = os.environ['AWS_SECRET']

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    s3manager = S3Manager(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret)
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    awsRequester = AwsRequester(accessKeyId=accessKeyId, accessKeySecret=accessKeySecret)
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester)
    tokenAttributeProcessor = TokenAttributeProcessor(retriever=retriever)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor, tokenOwnershipProcessor=tokenOwnershipProcessor, collectionActivityProcessor=collectionActivityProcessor, tokenListingProcessor=tokenListingProcessor, tokenAttributeProcessor=tokenAttributeProcessor)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, tokenManager=tokenManager, requester=requester, revueApiKey=revueApiKey)

    processor = NotdMessageProcessor(notdManager=notdManager)
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    workQueueProcessor = MessageQueueProcessor(queue=workQueue, messageProcessor=processor, slackClient=slackClient, requestIdHolder=requestIdHolder)
    tokenQueueProcessor = MessageQueueProcessor(queue=tokenQueue, messageProcessor=processor, slackClient=slackClient, requestIdHolder=requestIdHolder)

    await database.connect()
    await s3manager.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    try:
        while True:
            # hasProcessedWork = await workQueueProcessor.execute_batch(batchSize=3, longPollSeconds=1, shouldProcessInParallel=True)
            # if hasProcessedWork:
            #     continue
            hasProcessedToken = await tokenQueueProcessor.execute_batch(batchSize=10, longPollSeconds=1, shouldProcessInParallel=True)
            if hasProcessedToken:
                continue
            logging.info('No message received.. sleeping')
            time.sleep(60)
    finally:
        await database.disconnect()
        await s3manager.disconnect()
        await workQueue.disconnect()
        await tokenQueue.disconnect()
        await requester.close_connections()

if __name__ == '__main__':
    asyncio.run(main())
