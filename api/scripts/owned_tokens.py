import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging
import collections

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

    ownerAddress = '0x63A2368F4B509438ca90186cb1C15156713D5834'
   
    #boughtTokens = {}
    boughtTokens = collections.defaultdict(list)
    soldTokens= {}
    async with database.transaction():
        query = TokenTransfersTable.select()
        query = query.where(TokenTransfersTable.c.toAddress == ownerAddress)
        async for row in retriever.database.iterate(query=query):
            tokenTransfer = token_transfer_from_row(row)
            boughtTokens[tokenTransfer.registryAddress].append(tokenTransfer.tokenId)
        
        query = TokenTransfersTable.select()
        query = query.where(TokenTransfersTable.c.fromAddress == ownerAddress)
        async for row in retriever.database.iterate(query=query):
            tokenTransfer = token_transfer_from_row(row)
            soldTokens[tokenTransfer.registryAddress] = tokenTransfer.tokenId
       
        print(boughtTokens.values())
        print(soldTokens)

        uniqueBoughtTokens = len(boughtTokens.values())
        uniqueSoldTokens = len(soldTokens.values())
        tokensOwned = uniqueBoughtTokens - uniqueSoldTokens
        print(tokensOwned)

    await database.disconnect()
    logging.info(f'Got {len(tokensOwned)} total owned')    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(ownedTokens())
