import logging
import os

import boto3
from core.api.health import create_api as create_health_api
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.web3.eth_client import RestEthClient
from databases import Database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from notd.api.api_v1 import create_api as create_v1_api
from notd.block_processor import BlockProcessor
from notd.collection_processor import CollectionProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor

logging.basicConfig(level=logging.INFO)

database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
saver = Saver(database=database)
retriever = Retriever(database=database)

sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
tokenQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')

s3Client = boto3.client(service_name='s3', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
s3manager = S3Manager(s3Client=s3Client)

awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
blockProcessor = BlockProcessor(ethClient=ethClient)
requester = Requester()
tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient)
revueApiKey = os.environ['REVUE_API_KEY']
tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor, tokenMetadataProcessor=tokenMetadataProcessor)
notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, tokenManager=tokenManager, requester=requester, revueApiKey=revueApiKey)

app = FastAPI()
app.include_router(router=create_health_api(name=os.environ.get('NAME', 'notd'), version=os.environ.get('VERSION')))
app.include_router(prefix='/v1', router=create_v1_api(notdManager=notdManager))
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_methods=['*'], allow_headers=['*'], expose_headers=[
    'X-Response-Time',
    'X-Server',
    'X-Server-Version',
    'X-Kiba-Token',
], allow_origins=[
    'https://nft.tokenhunt.io',
    'http://localhost:3000',
])

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    await requester.close_connections()
