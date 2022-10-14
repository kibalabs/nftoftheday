import os

from core import logging
from core.api.health import create_api as create_health_api
from core.api.middleware.database_connection_middleware import DatabaseConnectionMiddleware
from core.api.middleware.exception_handling_middleware import ExceptionHandlingMiddleware
from core.api.middleware.logging_middleware import LoggingMiddleware
from core.api.middleware.server_headers_middleware import ServerHeadersMiddleware
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.database import Database
from core.util.value_holder import RequestIdHolder
from core.web3.eth_client import RestEthClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pablo import PabloClient

from notd.activity_manager import ActivityManager
from notd.api.api_v1 import create_api as create_v1_api
from notd.api.gallery_v1 import create_api as create_gallery_v1_api
from notd.api.gm_v1 import create_api as create_gm_v1_api
from notd.api.response_builder import ResponseBuilder
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
from notd.gallery_manager import GalleryManager
from notd.gm_manager import GmManager
from notd.listing_manager import ListingManager
from notd.lock_manager import LockManager
from notd.manager import NotdManager
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_attributes_processor import TokenAttributeProcessor
from notd.token_listing_processor import TokenListingProcessor
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor
from notd.twitter_manager import TwitterManager

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
workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
awsRequester = AwsRequester(accessKeyId=accessKeyId, accessKeySecret=accessKeySecret)
ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
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
collectionOverlapProcessor = CollectionOverlapProcessor(retriever=retriever)
activityManager = ActivityManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, collectionActivityProcessor=collectionActivityProcessor)
attributeManager = AttributeManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, tokenAttributeProcessor=tokenAttributeProcessor)
collectionManager = CollectionManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor)
ownershipManager = OwnershipManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenOwnershipProcessor=tokenOwnershipProcessor, lockManager=lockManager, collectionManager=collectionManager)
listingManager = ListingManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenListingProcessor=tokenListingProcessor)
collectionOverlapManager = CollectionOverlapManager(saver=saver, retriever=retriever, workQueue=workQueue, collectionOverlapProcessor=collectionOverlapProcessor)
tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenMetadataProcessor=tokenMetadataProcessor, collectionManager=collectionManager, ownershipManager=ownershipManager)
blockManager = BlockManager(saver=saver, retriever=retriever, workQueue=workQueue, blockProcessor=blockProcessor, tokenManager=tokenManager, collectionManager=collectionManager, ownershipManager=ownershipManager)
twitterManager = TwitterManager(saver=saver, retriever=retriever, requester=requester, workQueue=workQueue, twitterBearerToken=twitterBearerToken)
badgeProcessor = BadgeProcessor(retriever=retriever, saver=saver) 
badgeManager = BadgeManager(retriever=retriever, saver=saver, workQueue=workQueue, badgeProcessor=badgeProcessor)
notdManager = NotdManager(saver=saver, retriever=retriever, workQueue=workQueue, blockManager=blockManager, tokenManager=tokenManager,  activityManager=activityManager,  attributeManager=attributeManager,  collectionManager=collectionManager,  ownershipManager=ownershipManager,  listingManager=listingManager,  twitterManager=twitterManager, collectionOverlapManager=collectionOverlapManager, badgeManager=badgeManager, requester=requester, revueApiKey=revueApiKey)
responseBuilder = ResponseBuilder(retriever=retriever)
galleryManager = GalleryManager(ethClient=ethClient, retriever=retriever, saver=saver, twitterManager=twitterManager, collectionManager=collectionManager)
gmManager = GmManager(retriever=retriever, saver=saver)

app = FastAPI()
app.include_router(router=create_health_api(name=name, version=version, environment=environment))
app.include_router(prefix='/v1', router=create_v1_api(notdManager=notdManager, responseBuilder=responseBuilder))
app.include_router(prefix='/gallery/v1', router=create_gallery_v1_api(galleryManager=galleryManager, responseBuilder=responseBuilder))
app.include_router(prefix='/gm/v1', router=create_gm_v1_api(gmManager=gmManager, responseBuilder=responseBuilder))
app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(ServerHeadersMiddleware, name=name, version=version, environment=environment)
app.add_middleware(LoggingMiddleware, requestIdHolder=requestIdHolder)
app.add_middleware(DatabaseConnectionMiddleware, database=database)
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_methods=['*'], allow_headers=['*'], expose_headers=['*'], allow_origins=[
    'http://localhost:3000',
    'https://tokenhunt.io',
    'https://nft.tokenhunt.io',
    'https://pfpkit.xyz',
    'https://mdtp-gallery.kibalabs.com',
    'https://gallery.spriteclubnft.com',
    'https://gallery.milliondollartokenpage.com',
], allow_origin_regex='https://.*\.tokenpage\.xyz')

@app.on_event('startup')
async def startup():
    await database.connect()
    await s3Manager.connect()
    await workQueue.connect()
    await tokenQueue.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    await s3Manager.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()
    await awsRequester.close_connections()
    await openseaRequester.close_connections()
    await requester.close_connections()
