import asyncio
import os
import sys

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
from pablo import PabloClient
from core.http.basic_authentication import BasicAuthentication

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.activity_manager import ActivityManager
from notd.attribute_manager import AttributeManager
from notd.block_manager import BlockManager
from notd.block_processor import BlockProcessor
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_manager import CollectionManager
from notd.collection_processor import CollectionProcessor
from notd.listing_manager import ListingManager
from notd.lock_manager import LockManager
from notd.manager import NotdManager
from notd.notd_message_processor import NotdMessageProcessor
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_attributes_processor import TokenAttributeProcessor
from notd.token_listing_processor import TokenListingProcessor
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor
from notd.twitter_manager import TwitterManager


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
    twitterBearerToken=os.environ["TWITTER_BEARER_TOKEN"]

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret)
    dlWorkQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue-dl')
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    # awsRequester = AwsRequester(accessKeyId=accessKeyId, accessKeySecret=accessKeySecret)
    # ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    infuraAuth = BasicAuthentication(username='', password=os.environ["INFURA_PROJECT_SECRET"])
    infuraRequester = Requester(headers={'Authorization': f'Basic {infuraAuth.to_string()}'})
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    pabloClient = PabloClient(requester=requester)
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3Manager=s3Manager, bucketName=os.environ['S3_BUCKET'], pabloClient=pabloClient)
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3Manager=s3Manager, bucketName=os.environ['S3_BUCKET'])
    tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    lockManager = LockManager(retriever=retriever, saver=saver)
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester, lockManager=lockManager)
    tokenAttributeProcessor = TokenAttributeProcessor(retriever=retriever)
    activityManager = ActivityManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, collectionActivityProcessor=collectionActivityProcessor)
    attributeManager = AttributeManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, tokenAttributeProcessor=tokenAttributeProcessor)
    collectionManager = CollectionManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor)
    ownershipManager = OwnershipManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenOwnershipProcessor=tokenOwnershipProcessor, collectionManager=collectionManager)
    listingManager = ListingManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenListingProcessor=tokenListingProcessor)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenMetadataProcessor=tokenMetadataProcessor, collectionManager=collectionManager)
    blockManager = BlockManager(saver=saver, retriever=retriever, workQueue=workQueue, blockProcessor=blockProcessor, tokenManager=tokenManager, collectionManager=collectionManager, ownershipManager=ownershipManager)
    twitterManager = TwitterManager(saver=saver, retriever=retriever, requester=requester, workQueue=workQueue, twitterBearerToken=twitterBearerToken)
    notdManager = NotdManager(saver=saver, retriever=retriever, workQueue=workQueue, blockManager=blockManager, tokenManager=tokenManager,  activityManager=activityManager,  attributeManager=attributeManager,  collectionManager=collectionManager,  ownershipManager=ownershipManager,  listingManager=listingManager,  twitterManager=twitterManager, requester=requester, revueApiKey=revueApiKey)

    processor = NotdMessageProcessor(notdManager=notdManager)
    slackClient = None #SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    workQueueProcessor = MessageQueueProcessor(queue=dlWorkQueue, messageProcessor=processor, slackClient=slackClient, requestIdHolder=requestIdHolder)

    await database.connect()
    await s3Manager.connect()
    await dlWorkQueue.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    try:
        while True:
            hasProcessedWork = await workQueueProcessor.execute_batch(batchSize=3, longPollSeconds=1, shouldProcessInParallel=True)
            if not hasProcessedWork:
                break
    finally:
        await database.disconnect()
        await s3Manager.disconnect()
        await dlWorkQueue.disconnect()
        await workQueue.disconnect()
        await tokenQueue.disconnect()
        await requester.close_connections()

if __name__ == '__main__':
    asyncio.run(main())
