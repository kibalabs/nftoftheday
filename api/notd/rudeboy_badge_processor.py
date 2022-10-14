from typing import List

import sqlalchemy
from core.util import date_util

from notd.collection_badge_processor import CollectionBadgeProcessor
from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.model import RetrievedCollectionBadgeHolder
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenTransfersTable

RUDEBOYS_OWNER_ADDRESS = '0xAb3e5a900663ea8C573B8F893D540D331fbaB9F5'

class RudeboysBadgeProcessor(CollectionBadgeProcessor):

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever= retriever
        self.saver= saver

    async def get_all_badges(self) -> None:
        minterBadgeHolders = await self.get_minter_badge_holders()
        oneOfOneBadgeHolders = await self.get_one_of_one_badge_holders()
        allBadges = minterBadgeHolders + oneOfOneBadgeHolders
        return allBadges

    async def get_minter_badge_holders(self) -> List[RetrievedCollectionBadgeHolder]:
        query = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('toAddress'))
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.fromAddress == RUDEBOYS_OWNER_ADDRESS)
        )
        result = await self.retriever.database.execute(query=query)
        minterBadgeHolders = [RetrievedCollectionBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.toAddress, badgeKey="MINTER", achievedDate=date_util.datetime_from_now()) for row in result]
        return minterBadgeHolders

    async def get_one_of_one_badge_holders(self) -> List[RetrievedCollectionBadgeHolder]:
        oneOfOneQuery = (
            sqlalchemy.select(TokenMultiOwnershipsTable.c.tokenId)
            .where(TokenMultiOwnershipsTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenMultiOwnershipsTable.c.quantity == 1)
        )
        query = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('toAddress'))
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.tokenId.in_(oneOfOneQuery.select()))
        )
        result = await self.retriever.database.execute(query=query)
        oneOfOneBadgeHolders = [RetrievedCollectionBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.toAddress, badgeKey="ONE-OF-ONE", achievedDate=date_util.datetime_from_now()) for row in result]
        return oneOfOneBadgeHolders
