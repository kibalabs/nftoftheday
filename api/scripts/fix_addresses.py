import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from core.store.retriever import IntegerFieldFilter
from databases.core import Database

from notd.chain_utils import normalize_address
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=5)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    retriever = Retriever(database=database)
    await database.connect()

    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        nextBlockNumber = currentBlockNumber + batchSize
        start = min(currentBlockNumber, nextBlockNumber)
        end = max(currentBlockNumber, nextBlockNumber)
        currentBlockNumber = nextBlockNumber
        logging.info(f'Working on {start} to {end}')

        fieldFilters = [
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, gte=start),
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, lt=end),
        ]
        tokenTransfersToChange = []
        async with database.transaction():
            async for tokenTransfer in retriever.normalize_bad_token_transfers(filters=fieldFilters, length=42):
                tokenTransfersToChange.append(tokenTransfer)
            logging.info(f'Got {len(tokenTransfersToChange)} changes:')
            for tokenTransfer in tokenTransfersToChange:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenTransfer.tokenTransferId)
                values = {
                    TokenTransfersTable.c.toAddress.key: normalize_address(tokenTransfer.toAddress),
                    TokenTransfersTable.c.fromAddress.key: normalize_address(tokenTransfer.fromAddress),
                }
                await database.execute(query=query, values=values)
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
