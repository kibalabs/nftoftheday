import logging
import os
import time

import asyncclick as click
import boto3
from core.http.basic_authentication import BasicAuthentication
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.web3.eth_client import RestEthClient
from databases import Database

from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient
from notd.store.retriever import NotdRetriever
from notd.store.saver import Saver
from notd.token_client import TokenClient


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

    infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
    infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    openseaClient = OpenseaClient(requester=requester)
    tokenClient = TokenClient(requester=requester, ethClient=ethClient)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, openseaClient=openseaClient, tokenClient=tokenClient, requester=requester)

    await database.connect()
    isReverse = batchSize < 0
    currentBlockNumber = startBlockNumber
    exceptionCount = 0
    while (isReverse and currentBlockNumber > endBlockNumber) or (not isReverse and currentBlockNumber < endBlockNumber):
        nextBlockNumber = currentBlockNumber + batchSize
        start = min(currentBlockNumber, nextBlockNumber)
        end = max(currentBlockNumber, nextBlockNumber)
        logging.info(f'Working on {start} to {end}')
        try:
            await notdManager.process_block_range(startBlockNumber=start, endBlockNumber=end)
        except Exception as exception:
            logging.error(f'Failed due to: {str(exception)[:200]}')
            exceptionCount += 1
            if exceptionCount > 3:
                logging.error(f'Failed 3 times in a row, bailing out. Next to process is {start}-{end}')
                break
            time.sleep(60)
            continue
        currentBlockNumber = nextBlockNumber
        exceptionCount = 0
    await database.disconnect()
    await requester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')
