
import logging
from operator import and_
import os
import asyncio
import asyncclick as click
from core.store.retriever import Direction, IntegerFieldFilter, Order, StringFieldFilter
from databases.core import Database

from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.sql.expression import select
from notd.chain_utils import normalize_address
from notd.store.schema import TokenTransfersTable as table
from notd.store.retriever import Retriever


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int,default=12839300)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int,default=12839320)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=25)
@click.option('-a', '--owner-address', 'ownerAddress', required=True, type=str, default='0x18090cDA49B21dEAffC21b4F886aed3eB787d032')
async def new_registries(startBlockNumber,endBlockNumber,batchSize,ownerAddress):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')#pylint: disable=invalid-name
    retriever = Retriever(database)

    await database.connect()
    currentBlocknumber = startBlockNumber
    while currentBlocknumber < endBlockNumber:
        nextBlockNumber = currentBlocknumber + batchSize
        start = min(currentBlocknumber,startBlockNumber)
        end = max(currentBlocknumber,nextBlockNumber)
        currentBlocknumber = nextBlockNumber

        fieldFilter = [
            IntegerFieldFilter (fieldName=table.c.blockNumber.key,gte=start),
            IntegerFieldFilter (fieldName=table.c.blockNumber.key,lt=end),
        ]
        orders = [Order(fieldName=table.c.tokenTransferId.key,direction=Direction.ASCENDING)]
        ownedTokens = []
        async with database.transaction():
            async for tokenTransfer in retriever.generate_token_transfers(fieldFilters=fieldFilter,orders=orders):
                if tokenTransfer.toAddress == ownerAddress:
                    ownedTokens.append(tokenTransfer)
            tokenTransferOwned = [str(tokenTransfer.tokenTransferId) for tokenTransfer in ownedTokens]
            logging.info(f'Got {len(ownedTokens)} : {tokenTransferOwned}')
    
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(new_registries())
    
