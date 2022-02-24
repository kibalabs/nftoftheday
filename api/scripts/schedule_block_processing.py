import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
from typing import Optional

import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.messages import ProcessBlockMessageContent


@click.command()
@click.option('-b', '--block-number', 'blockNumber', required=False, type=int)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=False, type=int, default=0)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=False, type=int)
async def run(blockNumber: Optional[int], startBlockNumber: Optional[int], endBlockNumber: Optional[int]):
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

    await workQueue.connect()
    if blockNumber:
        await workQueue.send_message(message=ProcessBlockMessageContent(blockNumber=blockNumber).to_message())
    elif startBlockNumber and endBlockNumber:
        for blockNumber in range(startBlockNumber, endBlockNumber):
            await workQueue.send_message(message=ProcessBlockMessageContent(blockNumber=blockNumber).to_message())
    else:
        raise Exception('Either blockNumber or startBlockNumber and endBlockNumber must be passed in.')
    await workQueue.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run(_anyio_backend='asyncio')
