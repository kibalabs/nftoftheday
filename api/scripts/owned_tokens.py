from enum import unique
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
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int,default=12839300)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int,default=12839320)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=20)

async def ownedTokens(startBlockNumber: int, endBlockNumber: int, batchSize: int, boughtTokens = [],soldTokens=[]):
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
        myAddress ='0x18090cDA49B21dEAffC21b4F886aed3eB787d032'.lower()

        fieldFilters = [
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, gte=start),
            IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, lt=end),

            OneOfFilter(filters = [
                StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=myAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.fromAddress.key,eq=myAddress)
            ]),
        ]
        #orders = [Order(fieldName=TokenTransfersTable.c.tokenTransferId.key, direction=Direction.ASCENDING)]
        async with database.transaction():
            async for tokenTransfer in retriever.generate_token_transfers(filters=fieldFilters):
                if tokenTransfer.toAddress == myAddress:
                    boughtTokens.append(tokenTransfer.tokenId)
                if tokenTransfer.fromAddress == myAddress:
                    soldTokens.append(tokenTransfer.tokenId)

            uniqueBoughtTokens = set(boughtTokens)
            uniqueSoldTokens = set(soldTokens)
            ownedTokens = uniqueBoughtTokens - uniqueSoldTokens
            for tokenTransfer in ownedTokens:
                query = TokenTransfersTable.select(TokenTransfersTable.c.tokenId == tokenTransfer)
            
            rows = await database.fetch_all(query=query)
            for row in rows:
                print(row[2])
        
    await database.disconnect()
    logging.info(f'Got {len(ownedTokens)} total owned')
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(ownedTokens())
