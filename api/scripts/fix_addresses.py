import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from databases.core import Database
from sqlalchemy.sql.expression import func as sqlalchemyfunc
from sqlalchemy.sql.expression import or_

from notd.chain_utils import normalize_address
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    await database.connect()

    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenTransfersTable.select()
            query = query.where(TokenTransfersTable.c.blockNumber >= start)
            query = query.where(TokenTransfersTable.c.blockNumber < end)
            query = query.where(or_(
                sqlalchemyfunc.length(TokenTransfersTable.c.toAddress) != 42,
                sqlalchemyfunc.length(TokenTransfersTable.c.toAddress) != 42,
            ))
            tokenTransfersToChange = [token_transfer_from_row(row) async for row in database.iterate(query=query)]
            logging.info(f'Updating {len(tokenTransfersToChange)} transfers...')
            for tokenTransfer in tokenTransfersToChange:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenTransfer.tokenTransferId)
                values = {
                    TokenTransfersTable.c.toAddress.key: normalize_address(tokenTransfer.toAddress),
                    TokenTransfersTable.c.fromAddress.key: normalize_address(tokenTransfer.fromAddress),
                }
                await database.execute(query=query, values=values)
        currentBlockNumber = currentBlockNumber + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
