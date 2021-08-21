import logging
import os
from typing import Optional

import asyncclick as click
import boto3
from core.queues.sqs_message_queue import SqsMessageQueue

from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ProcessBlocksMessageContent


@click.command()
@click.option('-b', '--block-number', 'blockNumber', required=False, type=int)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=False, type=int, default=0)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=False, type=int)
async def run(blockNumber: Optional[int], startBlockNumber: Optional[int], endBlockNumber: Optional[int]):
    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')

    if blockNumber:
        await workQueue.send_message(message=ProcessBlocksMessageContent(blockNumbers=[blockNumber]).to_message())
    elif startBlockNumber and endBlockNumber:
        await workQueue.send_message(message=ProcessBlockRangeMessageContent(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber).to_message())
    else:
        raise Exception('Either blockNumber or startBlockNumber and endBlockNumber must be passed in.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run(_anyio_backend='asyncio')
