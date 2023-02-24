import asyncio
import os
import sys

import asyncclick as click
from core import logging
from core.store.database import Database
from core.util.chain_util import normalize_address
from sqlalchemy.sql import functions as sqlalchemyfunc
from sqlalchemy.sql.expression import or_

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
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
        currentBlockNumber = end
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
