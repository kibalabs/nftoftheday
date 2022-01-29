import os
import sys
import asyncio
import logging
import boto3
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.web3.eth_client import RestEthClient

from notd.block_processor import BlockProcessor




async def download_from_s3():
    sqsClient = boto3.client(service_name='sqs', region_name='us-east-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    requester = Requester()
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    requester = Requester()
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    bucketName = os.environ['S3_BUCKET']
    
    set_of_attributes = set()
    for s3_file in (await s3manager.list_directory_files(s3Directory=f'{bucketName}/token-metadatas/')):
        a = await s3manager.read_file(sourcePath=f'{s3_file.bucket}/{s3_file.path}')
        f = json.loads(a)
        b = set(list(f.keys()))
        set_of_attributes = set_of_attributes | b
    print(set_of_attributes)
    return


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(download_from_s3())