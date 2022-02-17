import asyncio
import logging
import os
import sys
import time

import asyncclick as click
from core.aws_requester import AwsRequester
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
async def reprocess_transfers(startBlockNumber: int, endBlockNumber: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    notdManager = NotdManager(blockProcessor=None, saver=saver, retriever=retriever, workQueue=None, tokenManager=None, requester=requester, revueApiKey=None)

    await database.connect()
    await slackClient.post(text=f'reprocess_transfers → 🚧 started: {startBlockNumber}-{endBlockNumber}')
    try:
        currentBlockNumber = startBlockNumber
        while currentBlockNumber < endBlockNumber:
            logging.info(f'Working on {currentBlockNumber}')
            try:
                retrievedTokenTransfers = await blockProcessor.process_block(blockNumber=currentBlockNumber)
            except Exception as exception:
                logging.info(f'Got exception whilst getting blocks: {str(exception)}. Will retry in 10 secs.')
                time.sleep(60)
                currentBlockNumber -= 1
                continue
            await notdManager._save_block_transfers(blockNumber=currentBlockNumber, retrievedTokenTransfers=retrievedTokenTransfers)
            currentBlockNumber = currentBlockNumber + 1
        await slackClient.post(text=f'reprocess_transfers → ✅ completed : {startBlockNumber}-{endBlockNumber}')
    except Exception as exception:
        await slackClient.post(text=f'reprocess_transfers → ❌ error: {startBlockNumber}-{endBlockNumber}\n```{str(exception)}```')
        raise exception
    finally:
        await database.disconnect()
        await requester.close_connections()
        await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_transfers())
