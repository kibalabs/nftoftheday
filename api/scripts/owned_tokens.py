import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from databases.core import Database
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row


@click.command()
@click.option('-o', '--owner-address', 'ownerAddress', required=False, type=str)
async def owned_tokens(ownerAddress: Optional[str]):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    retriever = Retriever(database=database)

    await database.connect()
    boughtTokens = []
    soldTokens= []
    async with database.transaction():
        query = TokenTransfersTable.select()
        query = query.where(TokenTransfersTable.c.toAddress == ownerAddress)
        async for row in retriever.database.iterate(query=query):
            tokenTransfer = token_transfer_from_row(row)
            boughtTokens.append(tokenTransfer)

        query = TokenTransfersTable.select()
        query = query.where(TokenTransfersTable.c.fromAddress == ownerAddress)
        async for row in retriever.database.iterate(query=query):
            tokenTransfer = token_transfer_from_row(row)
            soldTokens.append(tokenTransfer)

        uniqueBoughtTokens = set(boughtTokens)
        uniqueSoldTokens = set(soldTokens)
        tokensOwned = uniqueBoughtTokens - uniqueSoldTokens

        for tokenTransfer in tokensOwned:
            logging.info(f'Tokens Owned: registry_address: {tokenTransfer.registryAddress}, token_id: {tokenTransfer.tokenId}')

    await database.disconnect()
    logging.info(f'Got {len(tokensOwned)} total owned')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(owned_tokens())
