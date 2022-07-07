import asyncio
import os
import sys
import time

import asyncclick as click
from core import logging
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.util import list_util
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable
from notd.token_manager import TokenManager


@click.command()
@click.option('-r', '--registry-address', 'registryAddress', required=True, type=str)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def reprocess_transfers(registryAddress: str, startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None, collectionActivityProcessor=None)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, tokenManager=tokenManager, requester=requester, revueApiKey=None)

    await database.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    await slackClient.post(text=f'reprocess_blocks_registry → 🚧 started: {startBlockNumber}-{endBlockNumber}')
    try:
        currentBlockNumber = startBlockNumber
        while currentBlockNumber < endBlockNumber:
            start = currentBlockNumber
            end = min(currentBlockNumber + batchSize, endBlockNumber)
            logging.info(f'Working on {start} to {end}...')
            query = (
                TokenTransfersTable.select()
                    .with_only_columns([TokenTransfersTable.c.blockNumber])
                    .filter(TokenTransfersTable.c.blockNumber >= start)
                    .filter(TokenTransfersTable.c.blockNumber < end)
                    .where(TokenTransfersTable.c.registryAddress == registryAddress)
                    .group_by(TokenTransfersTable.c.blockNumber)
            )
            result = await database.execute(query=query)
            blocksToReprocess = {row[0] for row in result}
            logging.info(f'Reprocessing {len(blocksToReprocess)} blocks')
            for chunk in list_util.generate_chunks(lst=list(blocksToReprocess), chunkSize=10):
                await asyncio.gather(*[notdManager.process_block(blockNumber=blockNumber, shouldSkipProcessingTokens=True) for blockNumber in chunk])
            currentBlockNumber = currentBlockNumber + batchSize
        await slackClient.post(text=f'reprocess_blocks_registry → ✅ completed : {startBlockNumber}-{endBlockNumber}')
    except Exception as exception:
        await slackClient.post(text=f'reprocess_blocks_registry → ❌ error: {startBlockNumber}-{endBlockNumber}\n```{str(exception)}```')
        raise exception
    finally:
        await database.disconnect()
        await workQueue.disconnect()
        await tokenQueue.disconnect()
        await requester.close_connections()
        await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_transfers())
