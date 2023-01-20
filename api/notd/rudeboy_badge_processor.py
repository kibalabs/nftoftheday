from typing import List

import sqlalchemy

from notd.collection_badge_processor import CollectionBadgeProcessor
from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.model import RetrievedGalleryBadgeHolder
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenTransfersTable

RUDEBOYS_OWNER_ADDRESS = '0xAb3e5a900663ea8C573B8F893D540D331fbaB9F5'

class RudeboysBadgeProcessor(CollectionBadgeProcessor):

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever= retriever
        self.saver= saver

    async def calculate_all_gallery_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        minterBadgeHolders = await self.calculate_minter_badge_holders()
        oneOfOneBadgeHolders = await self.calculate_one_of_one_badge_holders()
        allBadges = minterBadgeHolders + oneOfOneBadgeHolders
        return allBadges

    async def calculate_minter_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        query = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('ownerAddress'), sqlalchemy.func.min(BlocksTable.c.blockDate).label('achievedDate'))
            .join(BlocksTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber, isouter=True)
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.fromAddress == RUDEBOYS_OWNER_ADDRESS)
            .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.toAddress)
        )
        result = await self.retriever.database.execute(query=query)
        minterBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="MINTER", achievedDate=row.achievedDate) for row in result.mappings()]
        return minterBadgeHolders

    async def calculate_one_of_one_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        oneOfOneQuery = (
            sqlalchemy.select(TokenMultiOwnershipsTable.c.tokenId)
            .where(TokenMultiOwnershipsTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .group_by(TokenMultiOwnershipsTable.c.tokenId)
            .having(sqlalchemy.func.sum(TokenMultiOwnershipsTable.c.quantity) == 1)
        )
        query = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('ownerAddress'), sqlalchemy.func.min(BlocksTable.c.blockDate).label('achievedDate'))
            .join(BlocksTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber, isouter=True)
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.tokenId.in_(oneOfOneQuery))
            .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.toAddress)
        )
        result = await self.retriever.database.execute(query=query)
        oneOfOneBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="ONE_OF_ONE", achievedDate=row.achievedDate) for row in result.mappings()]
        return oneOfOneBadgeHolders

    async def calculate_never_sold_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        soldTokenQuery = (
                sqlalchemy.select(TokenTransfersTable.c.fromAddress)
                .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
                .group_by(TokenTransfersTable.c.fromAddress)
            )
        query = (
                sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('ownerAddress'), sqlalchemy.func.min(BlocksTable.c.blockDate).label('achievedDate'))
                .join(BlocksTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber, isouter=True)
                .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
                .where(TokenTransfersTable.c.toAddress.not_in(soldTokenQuery))
                .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.toAddress)
            )
        result = await self.retriever.database.execute(query=query)
        neverSoldBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="NEVER_SOLD", achievedDate=row.achievedDate) for row in result.mappings()]
        return neverSoldBadgeHolders

    async def calculate_collector_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass

    async def calculate_holder_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass

    async def calculate_diamond_hands_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass

    async def calculate_holder_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass

    async def calculate_seeing_double_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass

    async def calculate_first_ten_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass

    async def calculate_member_of_month_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass

    async def calculate_special_edition_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass