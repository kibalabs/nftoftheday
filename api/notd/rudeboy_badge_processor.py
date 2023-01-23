from typing import List
from typing import Tuple
import datetime

import sqlalchemy

from notd.collection_badge_processor import CollectionBadgeProcessor
from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.model import RetrievedGalleryBadgeHolder
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView

RUDEBOYS_OWNER_ADDRESS = '0xAb3e5a900663ea8C573B8F893D540D331fbaB9F5'
RUDEBOYS_SPECIAL_EDITION_TOKENS: List[int] = []

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

    async def _get_holders_per_limits(self, lowerLimit: int, higherLimit: int) -> List[Tuple[str, str, datetime.datetime]]:
        subQuery = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 0)
            .having(sqlalchemy.func.max(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex) >= lowerLimit)
            .having(sqlalchemy.func.max(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex) <= higherLimit)
            .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        query = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, TokenMultiOwnershipsTable.c.latestTransferDate.label('achievedDate'))
            .join(TokenMultiOwnershipsTable, sqlalchemy.and_(TokenMultiOwnershipsTable.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, TokenMultiOwnershipsTable.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, TokenMultiOwnershipsTable.c.tokenId == UserRegistryOrderedOwnershipsMaterializedView.c.tokenId))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.in_(subQuery))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex == lowerLimit)
        )
        result = await self.retriever.database.execute(query=query)
        holders = [(registryAddress, ownerAddress, achievedDate) for registryAddress, ownerAddress, achievedDate in result] #pylint: disable=unnecessary-comprehension
        return holders

    async def calculate_collector_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        holders = await self._get_holders_per_limits(lowerLimit=1, higherLimit=10)
        collectorBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="COLLECTOR", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return collectorBadgeHolders

    async def calculate_hodler_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        holders = await self._get_holders_per_limits(lowerLimit=11, higherLimit=20)
        hodlerBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="HODLER", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return hodlerBadgeHolders

    async def calculate_diamond_hands_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        holders = await self._get_holders_per_limits(lowerLimit=21, higherLimit=50)
        diamondHandsBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="DIAMOND_HANDS", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return diamondHandsBadgeHolders

    async def calculate_enthusiast_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        #NOTE(Femi-Ogunkola): Using a large value for higherLimit
        holders = await self._get_holders_per_limits(lowerLimit=51, higherLimit=3000)
        enthusiastBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="ENTHUSIAST", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return enthusiastBadgeHolders

    async def calculate_seeing_double_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        query = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, sqlalchemy.func.min(TokenMultiOwnershipsTable.c.latestTransferDate).label('achievedDate'), UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex)
            .join(TokenMultiOwnershipsTable, sqlalchemy.and_(TokenMultiOwnershipsTable.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, TokenMultiOwnershipsTable.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, TokenMultiOwnershipsTable.c.tokenId == UserRegistryOrderedOwnershipsMaterializedView.c.tokenId))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 2)
            .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        result = await self.retriever.database.execute(query=query)
        collectorBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="SEEING_DOUBLE", achievedDate=row.achievedDate) for row in result.mappings()]
        return collectorBadgeHolders

    async def calculate_first_ten_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        firstTenBadgeHolders: List[RetrievedGalleryBadgeHolder] = []
        return firstTenBadgeHolders

    async def calculate_member_of_month_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        memberOfMonthBadgeHolders: List[RetrievedGalleryBadgeHolder] = []
        return memberOfMonthBadgeHolders

    async def calculate_special_edition_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        specialEditionBadgeHolders: List[RetrievedGalleryBadgeHolder] = []
        return specialEditionBadgeHolders
