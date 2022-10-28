import asyncio
import math
import os
import sys
import time

import asyncclick as click
from core import logging
from core.aws_requester import AwsRequester
from core.http.basic_authentication import BasicAuthentication
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.util import list_util
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_manager import BlockManager
from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.model import MARKETPLACE_ADDRESSES
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable
from notd.token_manager import TokenManager


async def reprocess_block(notdManager: NotdManager, blockNumber: int):
    try:
        await notdManager.process_block(blockNumber=blockNumber, shouldSkipProcessingTokens=True, shouldSkipUpdatingOwnerships=True)
    except Exception as exception:
        logging.error(f'Failed to process block {blockNumber}: {exception}')


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def reprocess_blocks(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    # infuraAuth = BasicAuthentication(username='', password=os.environ["INFURA_PROJECT_SECRET"])
    # infuraRequester = Requester(headers={'Authorization': f'Basic {infuraAuth.to_string()}'})
    # ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    blockManager = BlockManager(saver=saver, retriever=retriever, workQueue=None, blockProcessor=blockProcessor, tokenManager=None, collectionManager=None, ownershipManager=None)
    notdManager = NotdManager(saver=saver, retriever=retriever, workQueue=None, blockManager=blockManager, tokenManager=None, activityManager=None, attributeManager=None, collectionManager=None, ownershipManager=None, listingManager=None, requester=requester, revueApiKey=None)

    await database.connect()
    await slackClient.post(text=f'reprocess_blocks → 🚧 started: {startBlockNumber}-{endBlockNumber}')
    try:
        currentBlockNumber = startBlockNumber
        milestoneBlockSize = math.ceil((endBlockNumber - startBlockNumber) / 100)
        nextMilestoneBlockNumber = currentBlockNumber + milestoneBlockSize
        while currentBlockNumber < endBlockNumber:
            start = currentBlockNumber
            end = min(currentBlockNumber + batchSize, endBlockNumber)
            logging.info(f'Working on {start} to {end}...')
            query = (
                TokenTransfersTable.select()
                    .with_only_columns(TokenTransfersTable.c.blockNumber)
                    .filter(TokenTransfersTable.c.blockNumber >= start)
                    .filter(TokenTransfersTable.c.blockNumber < end)
                    .where(TokenTransfersTable.c.contractAddress.in_(MARKETPLACE_ADDRESSES))
                    .where(TokenTransfersTable.c.isOutbound == True)
                    .group_by(TokenTransfersTable.c.blockNumber)
            )
            result = await retriever.database.execute(query=query)
            blocksToReprocess = {row[0] for row in result}
            logging.info(f'Reprocessing {len(blocksToReprocess)} blocks')
            for chunk in list_util.generate_chunks(lst=list(blocksToReprocess), chunkSize=10):
                await asyncio.gather(*[reprocess_block(notdManager=notdManager, blockNumber=blockNumber) for blockNumber in chunk])
            currentBlockNumber = currentBlockNumber + batchSize
            if currentBlockNumber > nextMilestoneBlockNumber:
                await slackClient.post(text=f'reprocess_blocks → 🚧 still going: {currentBlockNumber} / {startBlockNumber}-{endBlockNumber}')
                nextMilestoneBlockNumber = currentBlockNumber + milestoneBlockSize
        await slackClient.post(text=f'reprocess_blocks → ✅ completed : {startBlockNumber}-{endBlockNumber}')
    except Exception as exception:
        await slackClient.post(text=f'reprocess_blocks → ❌ error: {startBlockNumber}-{endBlockNumber}\n```{str(exception)}```')
        raise exception
    finally:
        await database.disconnect()
        await requester.close_connections()
        await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_blocks())
