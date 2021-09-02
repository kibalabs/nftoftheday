import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
import asyncio
import asyncclick as click

from databases.core import Database
from core.store.retriever import Direction,IntegerFieldFilter, Order

from notd.store.retriever import Retriever
from notd.chain_utils import normalize_address
from notd.store.schema import TokenTransfersTable

@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int,default=12839300)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int,default=12839320)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=25)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')#pylint: disable=invalid-name
    retriever = Retriever(database=database)

    await database.connect()

    currentBlocknumber = startBlockNumber
    while currentBlocknumber < endBlockNumber:
        nextBlockNumber = currentBlocknumber + batchSize
        start = min(currentBlocknumber,startBlockNumber)
        end = max(currentBlocknumber,nextBlockNumber)
        currentBlocknumber = nextBlockNumber

        fieldFilter = [
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key,gte=start),
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key,lt=end)
        ]
        orders = [Order(fieldName=TokenTransfersTable.c.tokenTransferId.key,direction=Direction.ASCENDING)]
        tokenTransfersToChange = []
        async with database.transaction():
            async for tokenTransfer in retriever.generate_token_transfers(fieldFilters=fieldFilter,orders=orders):
                if len(tokenTransfer.toAddress) != 42 or len(tokenTransfer.fromAddress) !=42:
                    tokenTransfersToChange.append(tokenTransfer)
            tokenTransferIdsToChange = [str(tokenTransfer.tokenTransferId) for tokenTransfer in tokenTransfersToChange]
            logging.info(f'Got {len(tokenTransfersToChange)} changes: {",".join(tokenTransferIdsToChange)}')
            for tokenTransfer in tokenTransfersToChange:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenTransfer.tokenTransferId)
                values =  {
                    TokenTransfersTable.c.toAddress.key: normalize_address(tokenTransfer.toAddress),
                    TokenTransfersTable.c.fromAddress.key: normalize_address(tokenTransfer.fromAddress),
                
                }
                await database.execute(query=query,values=values)
    await database.disconnect()
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
