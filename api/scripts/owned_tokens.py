import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from databases.core import Database
from sqlalchemy.sql.expression import or_
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

@click.command()
@click.option('-a', '--owner-address', 'ownerAddress', required=False, type=str)
async def ownedTokens(ownerAddress: Optional[str]):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    retriever = Retriever(database=database)
    await database.connect()

    boughtTokens = []
    soldTokens=[]
    async with database.transaction():
        async for tokenTransfer in retrieve_token_transfer(ownerAddress=ownerAddress, retriever=retriever):
            if tokenTransfer.toAddress == ownerAddress:
                boughtTokens.append(tokenTransfer.tokenId)
            if tokenTransfer.fromAddress == ownerAddress:
                soldTokens.append(tokenTransfer.tokenId)

        uniqueBoughtTokens = set(boughtTokens)
        uniqueSoldTokens = set(soldTokens)
        tokensOwned = uniqueBoughtTokens - uniqueSoldTokens
        for tokenTransfer in tokensOwned:
            query = TokenTransfersTable.select(TokenTransfersTable.c.tokenId == tokenTransfer)
            query = query.where(TokenTransfersTable.c.tokenId == tokenTransfer)
            rows = await database.fetch_all(query=query)
            for row in rows:
                print(row[2],row[5])

    await database.disconnect()
    logging.info(f'Got {len(tokensOwned)} total owned')

async def retrieve_token_transfer(ownerAddress,retriever):
    query = TokenTransfersTable.select()
    query = query.where(or_(TokenTransfersTable.c.toAddress == ownerAddress,TokenTransfersTable.c.fromAddress == ownerAddress))

    async for row in retriever.database.iterate(query=query):
        tokenTransfer = token_transfer_from_row(row)
        yield tokenTransfer

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(ownedTokens())
