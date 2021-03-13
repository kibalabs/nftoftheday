import asyncio
import os
import json
import logging
from typing import Optional

import asyncclick as click
import boto3
from web3 import Web3
from databases import Database

from notd.block_processor import BlockProcessor
from notd.block_processor import Web3EthClient
from notd.manager import NotdManager
from notd.core.requester import Requester
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from notd.core.sqs_message_queue import SqsMessageQueue

@click.command()
@click.option('-b', '--block-number', 'blockNumber', required=False, type=int)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=False, type=int, default=0)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=False, type=int)
async def run(blockNumber: Optional[int], startBlockNumber: Optional[int], endBlockNumber: Optional[int]):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = NotdRetriever(database=database)

    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

    w3 = Web3(Web3.HTTPProvider(endpoint_uri=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}'))
    requester = Requester()
    web3EthClient = Web3EthClient(web3Connection=w3)
    blockProcessor = BlockProcessor(ethClient=web3EthClient)
    manager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue)

    await database.connect()
    # await manager.receive_new_blocks()
    if blockNumber:
        await manager.process_block(blockNumber=blockNumber)
    elif startBlockNumber and endBlockNumber:
        await manager.process_block_range(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber)
    else:
        raise Exception('Either blockNumber or startBlockNumber and endBlockNumber must be passed in.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')
