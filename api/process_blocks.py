import asyncio
import os
import json
import logging
from typing import Optional
import time

import asyncclick as click
import boto3
from web3 import Web3
from databases import Database

from notd.block_processor import BlockProcessor
from notd.block_processor import RestEthClient
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from notd.core.sqs_message_queue import SqsMessageQueue
from notd.core.aws_requester import AwsRequester
from notd.core.requester import Requester
from notd.core.slack_client import SlackClient
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i: i + n]

@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=25)
async def run(startBlockNumber: int, endBlockNumber: int, batchSize: int):
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

    await database.connect()

    isReverse = batchSize < 0
    currentBlockNumber = startBlockNumber
    while (isReverse and currentBlockNumber > endBlockNumber) or (not isReverse and currentBlockNumber < endBlockNumber):
        nextBlockNumber = currentBlockNumber + batchSize
        start = min(currentBlockNumber, nextBlockNumber)
        end = max(currentBlockNumber, nextBlockNumber)
        logging.info(f'Working on {start} to {end}')
        try:
            await notdManager.process_block_range(startBlockNumber=start, endBlockNumber=end)
        except Exception as exception:
            logging.error(f'Failed due to: {str(exception)[:200]}')
            continue
        currentBlockNumber = nextBlockNumber
        time.sleep(2)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')
