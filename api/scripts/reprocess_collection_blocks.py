import asyncio
import datetime
import logging
import os
import sys

import asyncclick as click
import sqlalchemy
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
from notd.token_manager import TokenManager
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable



@click.command()
@click.option('-c', '--collection-id', 'collectionId', required=True, type=str)
async def run(collectionId: str):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    requester = Requester()
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None)
    # NOTE(krishan711): use tokenqueue so its lower prioritized work
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=tokenQueue, tokenManager=tokenManager, requester=requester, revueApiKey=None)

    await database.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    # await slackClient.post(text=f'reprocess_collection_blocks → 🚧 started: {collectionId}')

    print(f'Reprocessing collection blocks: {collectionId}')
    minDate = datetime.datetime(2022, 4, 7)
    query = (
        sqlalchemy.select(BlocksTable.c.blockNumber) \
        .join(TokenTransfersTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber) \
        .filter(TokenTransfersTable.c.registryAddress == collectionId)
        .filter(BlocksTable.c.updatedDate < minDate)
    )
    results = await database.execute(query=query)
    blockNumbers = set(blockNumber for (blockNumber, ) in results)
    print(f'Processing {len(blockNumbers)} blocks')
    # await notdManager.process_blocks_deferred(blockNumbers=blockNumbers)
    for blockNumber in blockNumbers:
        await notdManager.process_block(blockNumber=blockNumber)
    await database.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()
    await requester.close_connections()
    await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
