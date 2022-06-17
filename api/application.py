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

from notd.api.api_v1 import create_api as create_v1_api
from notd.api.response_builder import ResponseBuilder
from notd.block_processor import BlockProcessor
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_processor import CollectionProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor

requestIdHolder = RequestIdHolder()
name = os.environ.get('NAME', 'notd-api')
version = os.environ.get('VERSION', 'local')
environment = os.environ.get('ENV', 'dev')
isRunningDebugMode = environment == 'dev'

if isRunningDebugMode:
    logging.init_basic_logging()
else:
    logging.init_json_logging(name=name, version=version, environment=environment, requestIdHolder=requestIdHolder)

databaseConnectionString = Database.create_psql_connection_string(username=os.environ["REMOTE_DB_USERNAME"], password=os.environ["REMOTE_DB_PASSWORD"], host=os.environ["REMOTE_DB_HOST"], port=os.environ["REMOTE_DB_PORT"], name=os.environ["REMOTE_DB_NAME"])
#databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
database = Database(connectionString=databaseConnectionString)
saver = Saver(database=database)
retriever = Retriever(database=database)
s3manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
blockProcessor = BlockProcessor(ethClient=ethClient)
requester = Requester()
tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
openseaApiKey = os.environ['OPENSEA_API_KEY']
collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
revueApiKey = os.environ['REVUE_API_KEY']
tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor, tokenOwnershipProcessor=tokenOwnershipProcessor, collectionActivityProcessor=collectionActivityProcessor)
notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, tokenManager=tokenManager, requester=requester, revueApiKey=revueApiKey)
responseBuilder = ResponseBuilder(retriever=retriever)

app = FastAPI()
app.include_router(router=create_health_api(name=name, version=version, environment=environment))
app.include_router(prefix='/v1', router=create_v1_api(notdManager=notdManager, responseBuilder=responseBuilder))
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
    'https://sprites-gallery.kibalabs.com',
], allow_origin_regex='https://.*\.tokenpage\.xyz')

@app.on_event('startup')
async def startup():
    await database.connect()
    await s3manager.connect()
    await workQueue.connect()
    await tokenQueue.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    await s3manager.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()
    await awsRequester.close_connections()
    await requester.close_connections()
