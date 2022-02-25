import logging
import os
import sys
from typing import Optional

import asyncclick as click
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.messages import UpdateCollectionTokensMessageContent


@click.command()
@click.option('-a', '--collection-address', 'address', required=True, type=str)
@click.option('-d', '--should-force', 'shouldForce', default=False, is_flag=True)
async def run(address: str, shouldForce: Optional[bool]):
    workQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    await workQueue.connect()
    await workQueue.send_message(message=UpdateCollectionTokensMessageContent(address=address, shouldForce=shouldForce).to_message())
    await workQueue.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')