import asyncio
import os
import logging

import boto3
from databases import Database
from web3 import Web3

from notd.block_processor import BlockProcessor
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from notd.core.sqs_message_queue import SqsMessageQueue
from notd.core.requester import Requester
from notd.core.slack_client import SlackClient
from notd.core.message_queue_processor import MessageQueueProcessor
from notd.notd_message_processor import NotdMessageProcessor
from notd.manager import NotdManager

async def main():
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = NotdRetriever(database=database)

    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    requester = Requester()

    w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/rdYIr6T2nBgJvtKlYQxmVH3bvjW2DLxi'))
    blockProcessor = BlockProcessor(web3Connection=w3)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue)

    processor = NotdMessageProcessor(notdManager=notdManager)
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    messageQueueProcessor = MessageQueueProcessor(queue=workQueue, messageProcessor=processor, slackClient=slackClient)

    await database.connect()
    await messageQueueProcessor.run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
