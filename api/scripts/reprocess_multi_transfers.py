import asyncio
import logging
import os
import sys
from collections import defaultdict

import asyncclick as click
import sqlalchemy
from core import logging
from core.aws_requester import AwsRequester
from core.queues.sqs import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.util import chain_util
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row
from notd.token_manager import TokenManager


@click.command()
@click.option('-s', '--start-block-number', 'startBlock', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlock', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def reprocess_multi_transfers(startBlock: int, endBlock: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    #NOTE Change to aws credentials before final push
    workQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/FemiKiBa')
    tokenQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/FemiKiBa')
    requester = Requester()
    requester = Requester()
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    revueApiKey = os.environ['REVUE_API_KEY']
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None, collectionActivityProcessor=None)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=workQueue, tokenManager=tokenManager, requester=requester, revueApiKey=revueApiKey)

    await database.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    currentBlockNumber = startBlock
    while currentBlockNumber < endBlock:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlock)
        logging.info(f'Working on {start} to {end}...')
        async with saver.create_transaction() as connection:
            multiTransferSubquery = (
                TokenTransfersTable.select()
                .with_only_columns(TokenTransfersTable.c.transactionHash)
                .filter(TokenTransfersTable.c.blockNumber >= start)
                .filter(TokenTransfersTable.c.blockNumber < end)
                .group_by(TokenTransfersTable.c.transactionHash)
                .having(sqlalchemy.func.count(TokenTransfersTable.c.transactionHash) > 1)
                .subquery()
            )
            query = (
                TokenTransfersTable.select()
                .with_only_columns(TokenTransfersTable.c.blockNumber)
                .where(sqlalchemy.or_(
                    TokenTransfersTable.c.transactionHash.in_(sqlalchemy.select(multiTransferSubquery)),
                    TokenTransfersTable.c.registryAddress == '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85')
                )
            )
            result = await database.execute(query=query)
            blocksToReprocess = {row[0] for row in result}
            logging.info(f'Reprocessing {len(blocksToReprocess)} blocks')
            await notdManager.process_blocks_deferred(blockNumbers=list(blocksToReprocess), shouldSkipProcessingTokens=True)
            blocksToBackfill = set(list(range(start, end))) - blocksToReprocess
            logging.info(f'Back filling {len(blocksToBackfill)} blocks')
            values = {}
            values[TokenTransfersTable.c.isMultiAddress.key] = False
            values[TokenTransfersTable.c.isInterstitial.key] = False
            values[TokenTransfersTable.c.isSwap.key] =   False
            values[TokenTransfersTable.c.isBatch.key] = False
            query = TokenTransfersTable.update(TokenTransfersTable.c.blockNumber.in_(blocksToBackfill)).values(values)
            await database.execute(query=query)

        currentBlockNumber = currentBlockNumber + batchSize

    await database.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_multi_transfers())
