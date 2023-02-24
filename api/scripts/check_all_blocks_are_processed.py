import asyncio
import os
import sys

import asyncclick as click
from core import logging
from core.queues.sqs import SqsMessageQueue
from core.store.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.messages import ProcessBlocksMessageContent
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def check_all_processed(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    await database.connect()
    await workQueue.connect()

    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} - {end}...')
        async with database.transaction():
            query = (
                TokenTransfersTable.select()
                .with_only_columns(TokenTransfersTable.c.blockNumber)
                .filter(TokenTransfersTable.c.blockNumber >= start)
                .filter(TokenTransfersTable.c.blockNumber < end)
                .distinct(TokenTransfersTable.c.blockNumber)
            )
            processedBlocks = [row[0] for row in await database.fetch_all(query)]
        unprocessedBlocks = set(range(start, end)) - set(processedBlocks)
        logging.info(f'Processing {len(unprocessedBlocks)} blocks in {start} - {end}')
        await workQueue.send_message(message=ProcessBlocksMessageContent(blockNumbers=unprocessedBlocks).to_message())
        currentBlockNumber = currentBlockNumber + batchSize
    await database.disconnect()
    await workQueue.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(check_all_processed())
