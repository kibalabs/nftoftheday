from typing import List

import sqlalchemy

from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenTransfersTable

RUDEBOYS_OWNER_ADDRESS = '0xAb3e5a900663ea8C573B8F893D540D331fbaB9F5'
RUDEBOYS_ONE_OF_ONE_TOKENS = ['25']

class RudeboysBadgeProcessor:

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever= retriever
        self.saver= saver

    async def get_minter_badge_holders(self) -> List[str]:
        query = (
            sqlalchemy.select(sqlalchemy.func.distinct(TokenTransfersTable.c.toAddress).label('toAddress'))
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.fromAddress == RUDEBOYS_OWNER_ADDRESS)
        )
        result = await self.retriever.database.execute(query=query)
        minterBadgeHolders = [row.toAddress for row in result]
        # print(minterBadgeHolders, len(minterBadgeHolders))
        return minterBadgeHolders

    async def get_one_of_one_badge_holders(self) -> List[str]:
        oneOfOneQuery = (
            sqlalchemy.select(TokenMultiOwnershipsTable.c.tokenId)
            .where(TokenMultiOwnershipsTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenMultiOwnershipsTable.c.quantity == 1)
        )
        query = (
            sqlalchemy.select(sqlalchemy.func.distinct(TokenTransfersTable.c.toAddress).label('toAddress'))
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.tokenId.in_(oneOfOneQuery.select()))
        )
        result = await self.retriever.database.execute(query=query)
        oneOfOneBadgeHolders = [row.toAddress for row in result]
        # print(oneOfOneBadgeHolders, len(oneOfOneBadgeHolders))
        return oneOfOneBadgeHolders
        