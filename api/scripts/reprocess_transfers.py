from contextvars import Token
import os
import sys

from core.store.retriever import IntegerFieldFilter


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
import boto3
from core.queues.sqs_message_queue import SqsMessageQueue
from core.http.basic_authentication import BasicAuthentication
from core.requester import Requester
from core.s3_manager import S3Manager

from core.web3.eth_client import RestEthClient
from databases.core import Database

# from notd.messages import UpdateTokenMetadataMessageContent
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable, TokenTransfersTable
from notd.store.schema_conversions import token_metadata_from_row, token_transfer_from_row
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.block_processor import BlockProcessor
from notd.model import RetrievedTokenTransfer, TokenTransfer
from notd.collection_processor import CollectionProcessor
from notd.manager import NotdManager
from notd.opensea_client import OpenseaClient
from notd.store.retriever import Retriever
from notd.token_client import TokenClient


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=5)
async def reprocess_transfers(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = Retriever(database=database)

    sqsClient = boto3.client(service_name='sqs', region_name='us-east-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3Manager = S3Manager(s3Client=s3Client)
    infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
    infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    
    await database.connect()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        print(currentBlockNumber)
        retrievedTokenTransfers = await blockProcessor.get_transfers_in_block(blockNumber=currentBlockNumber)
        tokenTransferInDb = await retriever.list_token_transfers(
            fieldFilters=[
                IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, gte=start),
                IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, lt=end)
            ])
        
        print(len(set(retrievedTokenTransfers)-set(a)))
        #print(retrievedTokenTransfers)
        currentBlockNumber = currentBlockNumber + 1
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_transfers())
