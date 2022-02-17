import asyncio
import datetime
import logging
import os
import sys

import asyncclick as click
import boto3
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
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def reprocess_bad_blocks(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    sqsClient = boto3.client(service_name='sqs', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    requester = Requester()
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    # NOTE(krishan711): use tokenqueue so its lower prioritized work
    notdManager = NotdManager(blockProcessor=None, saver=saver, retriever=retriever, workQueue=tokenQueue, tokenManager=None, requester=requester, revueApiKey=None)

    await database.connect()
    await slackClient.post(text=f'reprocess_bad_blocks → 🚧 started: {startBlockNumber}-{endBlockNumber}')
    try:
        currentBlockNumber = startBlockNumber
        while currentBlockNumber < endBlockNumber:
            start = currentBlockNumber
            end = min(start + batchSize, endBlockNumber)
            logging.info(f'Working on {start}-{end}')
            blockNumbers = set(range(start, end))
            processedBlocksQuey = (
                sqlalchemy.select(BlocksTable.c.blockNumber)
                .where(BlocksTable.c.blockNumber >= start)
                .where(BlocksTable.c.blockNumber < end)
            )
            results = await database.execute(query=processedBlocksQuey)
            processedBlocks = {blockNumber for (blockNumber, ) in results}
            logging.info(f'Ignoring {len(processedBlocks)} processedBlocks')
            blockNumbers = list(blockNumbers - processedBlocks)
            # blockUncleCounts = []
            # for chunk in list_util.generate_chunks(lst=blockNumbers, chunkSize=10):
            #     blockUncleCounts += await asyncio.gather(*[blockProcessor.ethClient.get_block_uncle_count(blockNumber=blockNumber) for blockNumber in chunk])
            #   blocksWithUncles = {blockNumber for (blockNumber, uncleCount) in zip(blockNumbers, blockUncleCounts) if uncleCount > 0}
            blocksWithUncles = set()
            logging.info(f'Found {len(blocksWithUncles)} blocks with uncles')
            blocksWithDuplicatesQuery = (
                sqlalchemy.select(TokenTransfersTable.c.blockNumber, sqlalchemy.func.count(sqlalchemy.func.distinct(TokenTransfersTable.c.blockHash)), sqlalchemy.func.count(sqlalchemy.func.distinct(TokenTransfersTable.c.blockDate)))
                .where(TokenTransfersTable.c.blockNumber >= start)
                .where(TokenTransfersTable.c.blockNumber < end)
                .group_by(TokenTransfersTable.c.blockNumber)
            )
            results = await database.execute(query=blocksWithDuplicatesQuery)
            blocksWithDuplicates = {blockNumber for (blockNumber, blockHashCount, blockDateCount) in results if blockHashCount > 1 or blockDateCount > 1}
            logging.info(f'Found {len(blocksWithDuplicates)} blocks with multiple blockHashes')
            badBlockTransactionsQuery = (
                sqlalchemy.select(TokenTransfersTable.c.transactionHash)
                .where(TokenTransfersTable.c.blockNumber.in_(blocksWithDuplicates))
            )
            results = await database.execute(query=badBlockTransactionsQuery)
            badBlockTransactions = {transactionHash for (transactionHash, ) in results}
            logging.info(f'Found {len(badBlockTransactions)} transactions in bad blocks')
            badBlockTransactionActualBlocks = set()
            for chunk in list_util.generate_chunks(lst=list(badBlockTransactions), chunkSize=10):
                transactionReceipts = await asyncio.gather(*[blockProcessor.get_transaction_receipt(transactionHash=transactionHash) for transactionHash in chunk])
                badBlockTransactionActualBlocks.update({transactionReceipt['blockNumber'] for transactionReceipt in transactionReceipts})
            badBlockTransactionBlocksQuery = (
                sqlalchemy.select(sqlalchemy.func.distinct(TokenTransfersTable.c.blockNumber))
                .where(TokenTransfersTable.c.transactionHash.in_(badBlockTransactions))
            )
            results = await database.execute(query=badBlockTransactionBlocksQuery)
            badBlockTransactionBlocks = {blockNumber for (blockNumber, ) in results}
            allBadBlocks = blocksWithUncles.union(badBlockTransactionActualBlocks).union(blocksWithDuplicates).union(badBlockTransactionBlocks)
            logging.info(f'Found {len(allBadBlocks)} blocks to reprocess')
            await notdManager.process_blocks_deferred(blockNumbers=allBadBlocks)
            insertQuery = BlocksTable.insert().from_select(
                [BlocksTable.c.createdDate.key, BlocksTable.c.updatedDate.key, BlocksTable.c.blockNumber.key, BlocksTable.c.blockHash.key, BlocksTable.c.blockDate.key],
                sqlalchemy.select(sqlalchemy.literal(datetime.datetime(2022, 2, 1)), sqlalchemy.literal(datetime.datetime(2022, 2, 1)), TokenTransfersTable.c.blockNumber, TokenTransfersTable.c.blockHash, TokenTransfersTable.c.blockDate)
                .where(TokenTransfersTable.c.blockNumber.in_(set(blockNumbers) - allBadBlocks))
                .where(TokenTransfersTable.c.blockNumber >= start)
                .where(TokenTransfersTable.c.blockNumber < end)
                .group_by(TokenTransfersTable.c.blockNumber, TokenTransfersTable.c.blockHash, TokenTransfersTable.c.blockDate)
            )
            async with database.create_transaction() as connection:
                await database.execute(connection=connection, query=insertQuery)
            currentBlockNumber = end
        await slackClient.post(text=f'reprocess_bad_blocks → ✅ completed : {startBlockNumber}-{endBlockNumber}')
    except Exception as exception:
        await slackClient.post(text=f'reprocess_bad_blocks → ❌ error: {startBlockNumber}-{endBlockNumber}\n```{str(exception)}```')
        raise exception
    finally:
        await database.disconnect()
        await requester.close_connections()
        await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_bad_blocks())
