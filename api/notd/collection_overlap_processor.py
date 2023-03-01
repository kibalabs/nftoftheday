import logging
import typing
from typing import Any
from typing import List
from typing import Tuple

import sqlalchemy
from core.util import chain_util
from core.util import list_util
from sqlalchemy import Select
from sqlalchemy.sql import functions as sqlalchemyfunc

from notd.model import RetrievedCollectionOverlap
from notd.store.retriever import Retriever
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView


class CollectionOverlapProcessor:

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_overlap(self, registryAddress: str) -> List[RetrievedCollectionOverlap]:
        registryOwnersQuery = (
            sqlalchemy.select(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.distinct())
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
        )
        registryOwnersResult = await self.retriever.database.execute(query=registryOwnersQuery)
        registryOwners = [ownerAddress for (ownerAddress, ) in registryOwnersResult if ownerAddress != chain_util.BURN_ADDRESS]
        otherOwnedRegistryCounts: List[Tuple[str, str, int]] = []
        logging.info(f'Calculating overlap for {len(registryOwners)} owners')
        for registryOwnersChunk in list_util.generate_chunks(lst=registryOwners, chunkSize=50):
            # otherOwnedRegistryCountQuery = (
            #     sqlalchemy.select(TokenOwnershipsView.c.ownerAddress, TokenOwnershipsView.c.registryAddress, sqlalchemyfunc.sum(TokenOwnershipsView.c.quantity))  # type: ignore[no-untyped-call]
            #     .where(TokenOwnershipsView.c.ownerAddress.in_(registryOwnersChunk))
            #     .where(TokenOwnershipsView.c.quantity > 0)
            #     .group_by(TokenOwnershipsView.c.ownerAddress, TokenOwnershipsView.c.registryAddress)
            # )
            # otherOwnedRegistryCountResult = await self.retriever.database.execute(query=otherOwnedRegistryCountQuery)
            # otherOwnedRegistryCounts += list(otherOwnedRegistryCountResult)
            # # NOTE(krishan711): for some reason the view takes too long but querying the two tables separately fits in the time
            otherOwnedSingleRegistryCountQuery = (
                sqlalchemy.select(TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress, sqlalchemyfunc.count(TokenOwnershipsTable.c.tokenId))  # type: ignore[no-untyped-call]
                .where(TokenOwnershipsTable.c.ownerAddress.in_(registryOwnersChunk))
                .group_by(TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress)
            )
            otherOwnedSingleRegistryCountResult = await self.retriever.database.execute(query=otherOwnedSingleRegistryCountQuery)
            otherOwnedRegistryCounts += typing.cast(List[Tuple[str, str, int]], list(otherOwnedSingleRegistryCountResult))
            otherOwnedMultiRegistryCountQuery: Select[Any] = (  # type: ignore[misc]
                sqlalchemy.select(TokenMultiOwnershipsTable.c.ownerAddress, TokenMultiOwnershipsTable.c.registryAddress, sqlalchemyfunc.sum(TokenMultiOwnershipsTable.c.quantity))  # type: ignore[no-untyped-call]
                .where(TokenMultiOwnershipsTable.c.ownerAddress.in_(registryOwnersChunk))
                .where(TokenMultiOwnershipsTable.c.quantity > 0)
                .group_by(TokenMultiOwnershipsTable.c.ownerAddress, TokenMultiOwnershipsTable.c.registryAddress)
            )
            otherOwnedMultiRegistryCountResult = await self.retriever.database.execute(query=otherOwnedMultiRegistryCountQuery)
            otherOwnedRegistryCounts += typing.cast(List[Tuple[str, str, int]], list(otherOwnedMultiRegistryCountResult))
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
            ) for ownerAddress, otherRegistryAddress, otherRegistryTokenCount in otherOwnedRegistryCounts]
        return retrievedCollectionOverlaps
