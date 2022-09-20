from sqlalchemy.sql.expression import func as sqlalchemyfunc

from notd.model import RetrievedCollectionOverlap
from notd.store.retriever import Retriever
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView


class CollectionOverlapProcessor():

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_overlap(self, address: str):
        subQuery = (
        UserRegistryOrderedOwnershipsMaterializedView.select()
        .with_only_columns([UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.distinct()])
        .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == address)
        .subquery()
        )
        query = (
            TokenOwnershipsTable.select()
            .with_only_columns([TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress, sqlalchemyfunc.count(TokenOwnershipsTable.c.tokenId)])
            .where(TokenOwnershipsTable.c.ownerAddress.in_(subQuery.select()))
            .group_by(TokenOwnershipsTable.c.ownerAddress, TokenOwnershipsTable.c.registryAddress)
        )
        result = await self.retriever.database.execute(query=query)

        galleryCountQuery = (
            UserRegistryOrderedOwnershipsMaterializedView.select()
            .with_only_columns([UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress,sqlalchemyfunc.count(UserRegistryOrderedOwnershipsMaterializedView.c.tokenId)])
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == address)
            .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        galleryCountResult = await self.retriever.database.execute(query=galleryCountQuery)
        galleryCountMap = dict(list(galleryCountResult))
        retrievedCollectionOverlaps = [RetrievedCollectionOverlap(galleryAddress=address, registryAddress=registryAddress, ownerAddress=ownerAddress, tokenCount=tokenCount, galleryCount=galleryCountMap[ownerAddress]) for ownerAddress, registryAddress, tokenCount in result]
        return retrievedCollectionOverlaps
