import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from databases.core import Database

from notd.chain_utils import normalize_address
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

from sqlalchemy.sql.expression import func as sqlalchemyfunc




@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
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

        tokenTransferToChange = []
        async with database.transaction():
            query = TokenTransfersTable.select()
            query = query.where(sqlalchemyfunc.length(TokenTransfersTable.c.toAddress) != 42)
            query = query.where(TokenTransfersTable.c.blockNumber >= start)
            query = query.where(TokenTransfersTable.c.blockNumber < end)

            async for row in retriever.database.iterate(query=query):
                tokenTransfer = token_transfer_from_row(row)
                tokenTransferToChange.append(tokenTransfer)

            for token in tokenTransferToChange:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == token.tokenTransferId)
                values = {
                    TokenTransfersTable.c.toAddress.key: normalize_address(token.toAddress),
                    TokenTransfersTable.c.fromAddress.key: normalize_address(token.fromAddress),
                }
                await database.execute(query=query, values=values)
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
