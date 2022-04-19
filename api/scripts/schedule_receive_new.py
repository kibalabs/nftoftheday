import os
import sys

import asyncclick as click
from core import logging
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.messages import ReceiveNewBlocksMessageContent


@click.command()
async def run():
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    await workQueue.connect()
    await workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())
    await workQueue.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')
