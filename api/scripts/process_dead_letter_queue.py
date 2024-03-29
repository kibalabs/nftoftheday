import asyncio
import os
import sys

from core import logging
from core.http.basic_authentication import BasicAuthentication
from core.queues.message_queue_processor import MessageQueueProcessor
from core.queues.sqs import SqsMessageQueue
from core.requester import Requester
from core.store.database import Database
from core.util.value_holder import RequestIdHolder
from core.web3.eth_client import RestEthClient
from pablo import PabloClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.activity_manager import ActivityManager
from notd.attribute_manager import AttributeManager
from notd.badge_manager import BadgeManager
from notd.badge_processor import BadgeProcessor
from notd.block_manager import BlockManager
from notd.block_processor import BlockProcessor
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_manager import CollectionManager
from notd.collection_overlap_manager import CollectionOverlapManager
from notd.collection_overlap_processor import CollectionOverlapProcessor
from notd.collection_processor import CollectionProcessor
from notd.delegation_manager import DelegationManager
from notd.listing_manager import ListingManager
from notd.lock_manager import LockManager
from notd.manager import NotdManager
from notd.notd_message_processor import NotdMessageProcessor
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.sub_collection_manager import SubCollectionManager
from notd.sub_collection_processor import SubCollectionProcessor
from notd.sub_collection_token_manager import SubCollectionTokenManager
from notd.sub_collection_token_processor import SubCollectionTokenProcessor
from notd.token_attributes_processor import TokenAttributeProcessor
from notd.token_listing_processor import TokenListingProcessor
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor
from notd.token_staking_manager import TokenStakingManager
from notd.token_staking_processor import TokenStakingProcessor
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
    raribleApiKey = os.environ['RARIBLE_API_KEY']
    revueApiKey = os.environ['REVUE_API_KEY']
    accessKeyId = os.environ['AWS_KEY']
    accessKeySecret = os.environ['AWS_SECRET']
    twitterBearerToken = os.environ["TWITTER_BEARER_TOKEN"]
    ethNodeUsername = os.environ["ETH_NODE_USERNAME"]
    ethNodePassword = os.environ["ETH_NODE_PASSWORD"]
    ethNodeUrl = os.environ["ETH_NODE_URL"]

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    ethNodeAuth = BasicAuthentication(username=ethNodeUsername, password=ethNodePassword)
    ethNodeRequester = Requester(headers={'Authorization': f'Basic {ethNodeAuth.to_string()}'})
    ethClient = RestEthClient(url=ethNodeUrl, requester=ethNodeRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    pabloClient = PabloClient(requester=requester)
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    raribleRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": raribleApiKey})
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, pabloClient=pabloClient, openseaRequester=openseaRequester)
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey)
    tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    lockManager = LockManager(retriever=retriever, saver=saver)
    tokenAttributeProcessor = TokenAttributeProcessor(retriever=retriever)
    collectionOverlapProcessor = CollectionOverlapProcessor(retriever=retriever)
    activityManager = ActivityManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, collectionActivityProcessor=collectionActivityProcessor)
    attributeManager = AttributeManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, tokenAttributeProcessor=tokenAttributeProcessor)
    collectionManager = CollectionManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor)
    subCollectionProcessor = SubCollectionProcessor(openseaRequester=openseaRequester, collectionManager=collectionManager)
    subCollectionManager = SubCollectionManager(retriever=retriever, saver=saver, workQueue=workQueue, subCollectionProcessor=subCollectionProcessor)
    subCollectionTokenProcessor = SubCollectionTokenProcessor(openseaRequester=openseaRequester)
    subCollectionTokenManager = SubCollectionTokenManager(retriever=retriever, saver=saver, subCollectionTokenProcessor=subCollectionTokenProcessor, subCollectionManager=subCollectionManager)
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester, raribleRequester=raribleRequester, lockManager=lockManager, collectionManger=collectionManager)
    collectionOverlapManager = CollectionOverlapManager(saver=saver, retriever=retriever, workQueue=workQueue, collectionOverlapProcessor=collectionOverlapProcessor)
    ownershipManager = OwnershipManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenOwnershipProcessor=tokenOwnershipProcessor, lockManager=lockManager, collectionManager=collectionManager)
    listingManager = ListingManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenListingProcessor=tokenListingProcessor)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenMetadataProcessor=tokenMetadataProcessor, collectionManager=collectionManager, ownershipManager=ownershipManager)
    twitterManager = TwitterManager(saver=saver, retriever=retriever, requester=requester, workQueue=workQueue, twitterBearerToken=twitterBearerToken)
    badgeProcessor = BadgeProcessor(retriever=retriever, saver=saver)
    badgeManager = BadgeManager(retriever=retriever, saver=saver, workQueue=workQueue, badgeProcessor=badgeProcessor)
    delegationManager = DelegationManager(ethClient=ethClient)
    tokenStakingProcessor = TokenStakingProcessor(ethClient=ethClient, retriever=retriever)
    tokenStakingManager = TokenStakingManager(retriever=retriever, saver=saver, tokenQueue=tokenQueue, workQueue=workQueue, tokenStakingProcessor=tokenStakingProcessor)
    blockManager = BlockManager(saver=saver, retriever=retriever, workQueue=workQueue, blockProcessor=blockProcessor, tokenManager=tokenManager, collectionManager=collectionManager, ownershipManager=ownershipManager, tokenStakingManager=tokenStakingManager)
    notdManager = NotdManager(saver=saver, retriever=retriever, workQueue=workQueue, blockManager=blockManager, tokenManager=tokenManager, activityManager=activityManager, attributeManager=attributeManager, collectionManager=collectionManager, ownershipManager=ownershipManager, listingManager=listingManager, twitterManager=twitterManager, collectionOverlapManager=collectionOverlapManager, badgeManager=badgeManager, delegationManager=delegationManager, tokenStakingManager=tokenStakingManager, subCollectionTokenManager=subCollectionTokenManager, subCollectionManager=subCollectionManager, requester=requester, revueApiKey=revueApiKey)
    processor = NotdMessageProcessor(notdManager=notdManager)

    dlWorkQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue-dl')
    workQueueProcessor = MessageQueueProcessor(queue=dlWorkQueue, messageProcessor=processor, notificationClients=[], requestIdHolder=requestIdHolder)

    await database.connect()
    await dlWorkQueue.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    try:
        while True:
            hasProcessedWork = await workQueueProcessor.execute_batch(batchSize=1, longPollSeconds=1, shouldProcessInParallel=True)
            if not hasProcessedWork:
                break
    finally:
        await database.disconnect()
        await dlWorkQueue.disconnect()
        await workQueue.disconnect()
        await tokenQueue.disconnect()
        await requester.close_connections()
        await ethNodeRequester.close_connections()

if __name__ == '__main__':
    asyncio.run(main())
