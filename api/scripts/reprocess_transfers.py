from contextvars import Token
import os
import sys

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
    requester = Requester()
    openseaClient = OpenseaClient(requester=requester)
    tokenClient = TokenClient(requester=requester, ethClient=ethClient)
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester,ethClient=ethClient,s3manager=s3Manager,bucketName=os.environ['S3_BUCKET'])
    #slackClient = SlackClient()
    collectionProcessor=CollectionProcessor(requester=requester,ethClient=ethClient)
    #blockNumber = await blockProcessor.get_latest_block_number()
    revueApiKey = ""
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=workQueue ,openseaClient=openseaClient, tokenClient=tokenClient, requester=requester,tokenMetadataProcessor=tokenMetadataProcessor, collectionProcessor=collectionProcessor,  revueApiKey=revueApiKey)
    await database.connect()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        await notdManager.process_block_range(startBlockNumber=start, endBlockNumber=end)
        async with database.transaction():
            query = TokenTransfersTable.select()
            query = query.where(TokenTransfersTable.c.blockNumber >= start)
            query = query.where(TokenTransfersTable.c.blockNumber < end)
            query = query.where(TokenTransfersTable.c.tokenType == None)
            query = query.where(TokenTransfersTable.c.amount == None)
            tokenTransfersToChange = [token_transfer_from_row(row) async for row in database.iterate(query=query)]
            logging.info(f'Updating {len(tokenTransfersToChange)} transfers...')
            for tokenTransfer in tokenTransfersToChange:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenTransfer.tokenTransferId)
                values = {
                    TokenTransfersTable.c.tokenType.key: 'erc721single',
                    TokenTransfersTable.c.amount.key: 1,
                }
                await database.execute(query=query, values=values)            
        currentBlockNumber = currentBlockNumber + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_transfers())
