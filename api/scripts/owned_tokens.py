import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter ,OneOfFilter, StringFieldFilter
from core.store.retriever import Order
from databases.core import Database

from notd.chain_utils import normalize_address
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int,default=1)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int,default=13000)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=10000)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://obafemi:obafemi@{os.environ["REMOTE_DB_HOST"]}:{os.environ["REMOTE_DB_PORT"]}/{os.environ["REMOTE_DB_NAME"]}')
    retriever = Retriever(database=database)
    await database.connect()

    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        nextBlockNumber = currentBlockNumber + batchSize
        start = min(currentBlockNumber, nextBlockNumber)
        end = max(currentBlockNumber, nextBlockNumber)
        currentBlockNumber = nextBlockNumber
        logging.info(f'Working on {start} to {end}')
        myAddress = '0x18090cDA49B21dEAffC21b4F886aed3eB787d032'

        fieldFilters = [
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, gte=start),
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, lt=end),

            OneOfFilter(filters = [
                StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=myAddress),
            ]),
        ]
        orders = [Order(fieldName=TokenTransfersTable.c.tokenTransferId.key, direction=Direction.ASCENDING)]
        tokenTransfersToChange = []
        async with database.transaction():
            async for tokenTransfer in retriever.generate_token_transfers(filters=fieldFilters, orders=orders):
                if len(tokenTransfer.toAddress) != 42 or len(tokenTransfer.fromAddress) != 42:
                    tokenTransfersToChange.append(tokenTransfer)
            tokenTransferIdsToChange = [str(tokenTransfer.tokenTransferId) for tokenTransfer in tokenTransfersToChange]
            logging.info(f'Got {len(tokenTransfersToChange)} changes: {",".join(tokenTransferIdsToChange)}')
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
