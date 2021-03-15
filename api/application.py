import os
import logging

import boto3
from databases import Database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3

from notd.api.api_v1 import create_api as create_v1_api
from notd.api.health import create_api as create_health_api
from notd.block_processor import BlockProcessor
from notd.block_processor import RestEthClient
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from notd.core.sqs_message_queue import SqsMessageQueue
from notd.core.aws_requester import AwsRequester
from notd.core.requester import Requester
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient

logging.basicConfig(level=logging.INFO)

database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
saver = Saver(database=database)
retriever = NotdRetriever(database=database)

sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
ethClient = RestEthClient(url='https://nd-z2a4tjsdtfbzbk2zsq5r4pahky.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
blockProcessor = BlockProcessor(ethClient=ethClient)
requester = Requester()
openseaClient = OpenseaClient(requester=requester)
notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, openseaClient=openseaClient)

app = FastAPI()
app.include_router(router=create_health_api())
app.include_router(prefix='/v1', router=create_v1_api(notdManager=notdManager))
app.add_middleware(CORSMiddleware, allow_credentials=True, allow_methods=['*'], allow_headers=['*'], expose_headers=[
    'X-Response-Time',
    'X-Server',
    'X-Server-Version',
    'X-Kiba-Token',
], allow_origins=[
    'https://notd.kibalabs.com',
    'http://localhost:3000',
])

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
