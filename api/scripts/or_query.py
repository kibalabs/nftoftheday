import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
import asyncio
import asyncclick as click

from databases.core import Database
from core.store.retriever import Direction, IntegerFieldFilter, OneOfFilter, Order, StringFieldFilter

from notd.store.retriever import Retriever
from notd.chain_utils import normalize_address
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int, default=12839300)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int, default=12839320)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=20)
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
        myAddress = '0x18090cDA49B21dEAffC21b4F886aed3eB787d032'
        
       
        fieldFilters = [
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, gte=start),
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, lt=end),

            OneOfFilter(filters = [
                StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=myAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.fromAddress.key, eq=myAddress),
            ]),
        ]
        orders = [Order(fieldName=TokenTransfersTable.c.tokenTransferId.key, direction=Direction.ASCENDING)]

        async with database.transaction():
            async for tokenTransfer in retriever.generate_token_transfers(filters=fieldFilters,orders=orders):
                logging.info(f'tokenTransfer {tokenTransfer}')        
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
