import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
from typing import Optional

import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from api.notd.messages import UpdateCollectionTokensMessageContent



@click.command()
@click.option('-b', '--block-number', 'blockNumber', required=False, type=int)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=False, type=int, default=0)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=False, type=int)
async def run(address: str, shouldForce: Optional[bool]):
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')

    await tokenQueue.connect()
    await tokenQueue.send_message(message=UpdateCollectionTokensMessageContent(address=address, shouldForce=shouldForce).to_message())
    await tokenQueue.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run(_anyio_backend='asyncio')
