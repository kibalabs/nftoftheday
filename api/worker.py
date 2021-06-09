import asyncio
import os
import logging

import boto3
from databases import Database
from web3 import Web3

from notd.block_processor import BlockProcessor
from notd.eth_client import RestEthClient
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from core.sqs_message_queue import SqsMessageQueue
from core.basic_authentication import BasicAuthentication
from core.requester import Requester
from core.slack_client import SlackClient
from core.message_queue_processor import MessageQueueProcessor
from core.requester import Requester
from notd.notd_message_processor import NotdMessageProcessor
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient
from notd.token_client import TokenClient

async def main():
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = NotdRetriever(database=database)

    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    requester = Requester()

    infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
    infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    openseaClient = OpenseaClient(requester=requester)
    tokenClient = TokenClient(requester=requester, ethClient=ethClient)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, openseaClient=openseaClient, tokenClient=tokenClient, requester=requester)

    processor = NotdMessageProcessor(notdManager=notdManager)
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    messageQueueProcessor = MessageQueueProcessor(queue=workQueue, messageProcessor=processor, slackClient=slackClient)

    await database.connect()
    await messageQueueProcessor.run()

    # NOTE(krishan711): This is to tidy up, I'm not sure if this will ever be called
    await database.disconnect()
    await requester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
