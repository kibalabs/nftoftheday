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
from notd.eth_client import RestEthClient
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from notd.core.sqs_message_queue import SqsMessageQueue
from notd.core.basic_authentication import BasicAuthentication
from notd.core.requester import Requester
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient
from notd.token_client import TokenClient

logging.basicConfig(level=logging.INFO)

database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
saver = Saver(database=database)
retriever = NotdRetriever(database=database)

sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
blockProcessor = BlockProcessor(ethClient=ethClient)
requester = Requester()
openseaClient = OpenseaClient(requester=requester)
tokenClient = TokenClient(requester=requester, ethClient=ethClient)
notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, openseaClient=openseaClient, tokenClient=tokenClient, requester=requester)

app = FastAPI()
app.include_router(router=create_health_api())
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
