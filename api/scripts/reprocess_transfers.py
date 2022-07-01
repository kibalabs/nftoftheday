import asyncio
import os
import sys
import time

import asyncclick as click
from core import logging
from core.aws_requester import AwsRequester
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.web3.eth_client import RestEthClient
from core.queues.sqs_message_queue import SqsMessageQueue

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def reprocess_transfers(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    #NOTE Change to aws credentials before final push
    workQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/FemiKiBa')
    tokenQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/FemiKiBa')
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    notdManager = NotdManager(blockProcessor=None, saver=saver, retriever=retriever, workQueue=None, tokenManager=None, requester=requester, revueApiKey=None)

    await database.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        async with saver.create_transaction() as connection:
            query = (
                TokenTransfersTable.select()
                        .with_only_columns([TokenTransfersTable.c.blockNumber])
                    .filter(TokenTransfersTable.c.blockNumber >= start)
                    .filter(TokenTransfersTable.c.blockNumber < end)
                    .where(TokenTransfersTable.c.contractAddress == None)
                    .group_by(TokenTransfersTable.c.blockNumber)
            )
            result = await database.execute(query=query)
            blocksToReprocess = {row[0] for row in result}
            logging.info(f'Reprocessing {len(blocksToReprocess)} blocks')
            await notdManager.process_blocks_deferred(blockNumbers=list(blocksToReprocess), shouldSkipProcessingTokens=True) 
        currentBlockNumber = currentBlockNumber + batchSize

    await database.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_transfers())
