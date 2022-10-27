from typing import List
import sqlalchemy

from notd.model import RetrievedCollectionOverlap
from notd.store.retriever import Retriever
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView


class CollectionOverlapProcessor():

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_overlap(self, registryAddress: str) -> List[RetrievedCollectionOverlap]:
        otherRegistrySubQuery = (
            sqlalchemy.select([UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.distinct()])
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
        )
        # NOTE(krishan711): for some reason the view takes too long but querying the two tables separately fits in the time
        otherSingleRegistryCountQuery = (
            sqlalchemy.select([TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress, sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId)])
            .where(TokenOwnershipsTable.c.ownerAddress.in_(otherRegistrySubQuery))
            .group_by(TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress)
        )
        otherSingleRegistryCountResult = await self.retriever.database.execute(query=otherSingleRegistryCountQuery)
        otherRegistryCounts = list(otherSingleRegistryCountResult)
        otherMultiRegistryCountQuery = (
            sqlalchemy.select([TokenMultiOwnershipsTable.c.ownerAddress, TokenMultiOwnershipsTable.c.registryAddress, sqlalchemy.func.sum(TokenMultiOwnershipsTable.c.quantity)])
            .where(TokenMultiOwnershipsTable.c.ownerAddress.in_(otherRegistrySubQuery))
            .where(TokenMultiOwnershipsTable.c.quantity > 0)
            .group_by(TokenMultiOwnershipsTable.c.ownerAddress, TokenMultiOwnershipsTable.c.registryAddress)
        )
        otherMultiRegistryCountResult = await self.retriever.database.execute(query=otherMultiRegistryCountQuery)
        otherRegistryCounts += list(otherMultiRegistryCountResult)
        registryCountQuery = (
            sqlalchemy.select([UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, sqlalchemy.func.sum(UserRegistryOrderedOwnershipsMaterializedView.c.quantity)])
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
            .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        registryCountResult = await self.retriever.database.execute(query=registryCountQuery)
        registryCountMap = {ownerAddress: int(quantity) for (ownerAddress, quantity, ) in registryCountResult}
        retrievedCollectionOverlaps = [
            RetrievedCollectionOverlap(
                registryAddress=registryAddress,
                otherRegistryAddress=otherRegistryAddress,
                ownerAddress=ownerAddress,
                otherRegistryTokenCount=int(otherRegistryTokenCount),
                registryTokenCount=registryCountMap[ownerAddress],
            ) for ownerAddress, otherRegistryAddress, otherRegistryTokenCount in otherRegistryCounts]
        return retrievedCollectionOverlaps
