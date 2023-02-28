from typing import Any
from typing import List
from typing import Tuple

import sqlalchemy
from sqlalchemy import Select
from sqlalchemy.sql import functions as sqlalchemyfunc


from core.util import list_util
from core.util import chain_util

from notd.model import RetrievedCollectionOverlap
from notd.store.retriever import Retriever
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView


class CollectionOverlapProcessor():

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_overlap(self, registryAddress: str) -> List[RetrievedCollectionOverlap]:
        ownerRegistryQuery = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.distinct())
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
        )
        ownerRegistryResult = await self.retriever.database.execute(query=ownerRegistryQuery)
        otherRegistryAddresses = [registryAddress for registryAddress, in (ownerRegistryResult) if registryAddress != chain_util.BURN_ADDRESS]
        chunks = list_util.generate_chunks(lst=otherRegistryAddresses, chunkSize=5)
        # NOTE(krishan711): for some reason the view takes too long but querying the two tables separately fits in the time
        otherRegistryCounts = [] # type: ignore[misc]
        for chunk in chunks:
            otherSingleRegistryCountQuery = (
                sqlalchemy.select(TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress, sqlalchemyfunc.count(TokenOwnershipsTable.c.tokenId))  # type: ignore[no-untyped-call]
                .where(TokenOwnershipsTable.c.ownerAddress.in_(chunk))
                .group_by(TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress)
            )
            otherSingleRegistryCountResult = await self.retriever.database.execute(query=otherSingleRegistryCountQuery)
            otherRegistryCounts += list(otherSingleRegistryCountResult)
        otherMultiRegistryCountQuery: Select[Any] = (  # type: ignore[misc]
            sqlalchemy.select(TokenMultiOwnershipsTable.c.ownerAddress, TokenMultiOwnershipsTable.c.registryAddress, sqlalchemyfunc.sum(TokenMultiOwnershipsTable.c.quantity))  # type: ignore[no-untyped-call]
            .where(TokenMultiOwnershipsTable.c.ownerAddress.in_(ownerRegistryQuery))
            .where(TokenMultiOwnershipsTable.c.quantity > 0)
            .group_by(TokenMultiOwnershipsTable.c.ownerAddress, TokenMultiOwnershipsTable.c.registryAddress)
        )
        otherMultiRegistryCountResult = await self.retriever.database.execute(query=otherMultiRegistryCountQuery)
        otherRegistryCounts = list(otherMultiRegistryCountResult)
        registryCountQuery: Select[Any] = (  # type: ignore[misc]
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, sqlalchemyfunc.sum(UserRegistryOrderedOwnershipsMaterializedView.c.quantity))  # type: ignore[no-untyped-call]
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
