import datetime
from typing import List
from typing import Tuple

import sqlalchemy
from sqlalchemy import Select
from sqlalchemy.sql import functions as sqlalchemyfunc

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
RUDEBOYS_FIRST_TEN_MINTED_TOKENS: List[str] = []

class RudeboysBadgeProcessor(CollectionBadgeProcessor):

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever= retriever
        self.saver= saver

    async def calculate_all_gallery_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        minterBadgeHolders = await self.calculate_minter_badge_holders()
        oneOfOneBadgeHolders = await self.calculate_one_of_one_badge_holders()
        neverSoldBadgeHolders =  await self.calculate_never_sold_badge_holders()
        collectorBadgeHolders =  await self.calculate_collector_badge_holders()
        hodlerBadgeHolders =  await self.calculate_hodler_badge_holders()
        diamondHandsBadgeHolders =  await self.calculate_diamond_hands_badge_holders()
        enthusiastBadgeHolders =  await self.calculate_enthusiast_badge_holders()
        seeingDoubleBadgeHolders =  await self.calculate_seeing_double_badge_holders()
        firstTenBadgeHolders =  await self.calculate_first_ten_badge_holders()
        specialEditionBadgeHolders =  await self.calculate_special_edition_badge_holders()
        allBadges = minterBadgeHolders + oneOfOneBadgeHolders + specialEditionBadgeHolders + neverSoldBadgeHolders + collectorBadgeHolders + hodlerBadgeHolders + diamondHandsBadgeHolders + enthusiastBadgeHolders + seeingDoubleBadgeHolders + firstTenBadgeHolders
        return allBadges

    async def calculate_minter_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        query: Select = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('ownerAddress'), sqlalchemyfunc.min(BlocksTable.c.blockDate).label('achievedDate'))
            .join(BlocksTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber, isouter=True)
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.fromAddress == RUDEBOYS_OWNER_ADDRESS)
            .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.toAddress)
        )
        result = await self.retriever.database.execute(query=query)
        minterBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="MINTER", achievedDate=row.achievedDate) for row in result.mappings()]
        return minterBadgeHolders

    async def calculate_one_of_one_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        oneOfOneQuery: Select = (
            sqlalchemy.select(TokenMultiOwnershipsTable.c.tokenId)
            .where(TokenMultiOwnershipsTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .group_by(TokenMultiOwnershipsTable.c.tokenId)
            .having(sqlalchemyfunc.sum(TokenMultiOwnershipsTable.c.quantity) == 1)
        )
        query: Select = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('ownerAddress'), sqlalchemyfunc.min(BlocksTable.c.blockDate).label('achievedDate'))
            .join(BlocksTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber, isouter=True)
            .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(TokenTransfersTable.c.tokenId.in_(oneOfOneQuery))
            .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.toAddress)
        )
        result = await self.retriever.database.execute(query=query)
        oneOfOneBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="ONE_OF_ONE", achievedDate=row.achievedDate) for row in result.mappings()]
        return oneOfOneBadgeHolders

    async def calculate_never_sold_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        soldTokenQuery: Select = (
                sqlalchemy.select(TokenTransfersTable.c.fromAddress)
                .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
                .group_by(TokenTransfersTable.c.fromAddress)
            )
        query: Select = (
                sqlalchemy.select(TokenTransfersTable.c.registryAddress.label('registryAddress'), TokenTransfersTable.c.toAddress.label('ownerAddress'), sqlalchemyfunc.min(BlocksTable.c.blockDate).label('achievedDate'))
                .join(BlocksTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber, isouter=True)
                .where(TokenTransfersTable.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
                .where(TokenTransfersTable.c.toAddress.not_in(soldTokenQuery))
                .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.toAddress)
            )
        result = await self.retriever.database.execute(query=query)
        neverSoldBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="NEVER_SOLD", achievedDate=row.achievedDate) for row in result.mappings()]
        return neverSoldBadgeHolders

    async def _get_holders_per_limit(self, rewardTokenIndex: int) -> List[Tuple[str, str, datetime.datetime]]:
        query: Select = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, TokenMultiOwnershipsTable.c.latestTransferDate.label('achievedDate'))
            .join(TokenMultiOwnershipsTable, sqlalchemy.and_(TokenMultiOwnershipsTable.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, TokenMultiOwnershipsTable.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, TokenMultiOwnershipsTable.c.tokenId == UserRegistryOrderedOwnershipsMaterializedView.c.tokenId))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 0)
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex == rewardTokenIndex)
        )
        result = await self.retriever.database.execute(query=query)
        holders = [(registryAddress, ownerAddress, achievedDate) for registryAddress, ownerAddress, achievedDate in result] #pylint: disable=unnecessary-comprehension
        return holders

    async def calculate_collector_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        holders = await self._get_holders_per_limit(rewardTokenIndex=1)
        collectorBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="COLLECTOR", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return collectorBadgeHolders

    async def calculate_hodler_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        holders = await self._get_holders_per_limit(rewardTokenIndex=11)
        hodlerBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="HODLER", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return hodlerBadgeHolders

    async def calculate_diamond_hands_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        holders = await self._get_holders_per_limit(rewardTokenIndex=21)
        diamondHandsBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="DIAMOND_HANDS", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return diamondHandsBadgeHolders

    async def calculate_enthusiast_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        holders = await self._get_holders_per_limit(rewardTokenIndex=51)
        enthusiastBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey="ENTHUSIAST", achievedDate=achievedDate) for (registryAddress, ownerAddress, achievedDate) in holders]
        return enthusiastBadgeHolders

    async def calculate_seeing_double_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        query: Select = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, sqlalchemyfunc.min(TokenMultiOwnershipsTable.c.latestTransferDate).label('achievedDate'))
            .join(TokenMultiOwnershipsTable, sqlalchemy.and_(TokenMultiOwnershipsTable.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, TokenMultiOwnershipsTable.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, TokenMultiOwnershipsTable.c.tokenId == UserRegistryOrderedOwnershipsMaterializedView.c.tokenId))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity >= 2)
            .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        result = await self.retriever.database.execute(query=query)
        seeingDoubleBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="SEEING_DOUBLE", achievedDate=row.achievedDate) for row in result.mappings()]
        return seeingDoubleBadgeHolders

    async def calculate_first_ten_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        firstTenBadgeHolders: List[RetrievedGalleryBadgeHolder] = []
        return firstTenBadgeHolders

    async def calculate_special_edition_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        specialEditionBadgeHolders: List[RetrievedGalleryBadgeHolder] = []
        query: Select = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, sqlalchemyfunc.min(TokenMultiOwnershipsTable.c.latestTransferDate).label('achievedDate'))
            .join(TokenMultiOwnershipsTable, sqlalchemy.and_(TokenMultiOwnershipsTable.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, TokenMultiOwnershipsTable.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, TokenMultiOwnershipsTable.c.tokenId == UserRegistryOrderedOwnershipsMaterializedView.c.tokenId))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == COLLECTION_RUDEBOYS_ADDRESS)
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.tokenId.in_(RUDEBOYS_SPECIAL_EDITION_TOKENS))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 0)
            .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        result = await self.retriever.database.execute(query=query)
        specialEditionBadgeHolders = [RetrievedGalleryBadgeHolder(registryAddress=row.registryAddress, ownerAddress=row.ownerAddress, badgeKey="SEEING_DOUBLE", achievedDate=row.achievedDate) for row in result.mappings()]
        return specialEditionBadgeHolders
