import logging
import os
from typing import Optional

import asyncclick as click
import boto3
from core.aws_requester import AwsRequester
from core.http.basic_authentication import BasicAuthentication
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.web3.eth_client import RestEthClient
from databases import Database

from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_client import TokenClient


@click.command()
@click.option('-b', '--block-number', 'blockNumber', required=False, type=int)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=False, type=int, default=0)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=False, type=int)
async def run(blockNumber: Optional[int], startBlockNumber: Optional[int], endBlockNumber: Optional[int]):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = Retriever(database=database)

    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

#     infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
#     infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
#     ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    openseaClient = OpenseaClient(requester=requester)
    tokenClient = TokenClient(requester=requester, ethClient=ethClient)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, openseaClient=openseaClient, tokenClient=tokenClient, requester=requester)

    await database.connect()
    #await notdManager.receive_new_blocks()
    if blockNumber:
         await notdManager.process_block(blockNumber=blockNumber)
    elif startBlockNumber and endBlockNumber:
         await notdManager.process_block_range(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber)
    else:
         raise Exception('Either blockNumber or startBlockNumber and endBlockNumber must be passed in.')
    await database.disconnect()
    await requester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')
