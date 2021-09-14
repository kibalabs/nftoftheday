import os
import sys
from typing import Optional, Sequence

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from core.store.retriever import FieldFilter, IntegerFieldFilter
from databases.core import Database

from notd.chain_utils import normalize_address
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable
from sqlalchemy.sql.expression import func as sqlalchemyfunc

from notd.store.schema_conversions import token_transfer_from_row



@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int, default=12839820)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int, default=12839850)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=15)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    retriever = Retriever(database=database)

    async def token(fieldFilters: Optional[Sequence[FieldFilter]] = None):
        query = TokenTransfersTable.select()
        query = query.where(sqlalchemyfunc.length(TokenTransfersTable.c.toAddress) != 42)
        if fieldFilters:
            query = retriever._apply_field_filters(query=query, table=TokenTransfersTable, fieldFilters=fieldFilters)
        
        async for row in retriever.database.iterate(query=query):
            tokenTransfer = token_transfer_from_row(row)
            yield tokenTransfer

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
        tokenTransferToChange = []
        async with database.transaction():  
            async for tokenTransfer in token(fieldFilters=fieldFilters):
                tokenTransferToChange.append(tokenTransfer.tokenTransferId)
            for tokenId in tokenTransferToChange:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenId)
                values = {
                        TokenTransfersTable.c.toAddress.key: normalize_address(tokenTransfer.toAddress),
                        TokenTransfersTable.c.fromAddress.key: normalize_address(tokenTransfer.fromAddress),
                    }
                await database.execute(query=query, values=values)
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
