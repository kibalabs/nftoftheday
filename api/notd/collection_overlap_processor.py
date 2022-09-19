import datetime

from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from api.notd.model import RetrievedCollectionOverlap
from api.notd.store.schema import TokenOwnershipsTable, UserRegistryOrderedOwnershipsMaterializedView
from sqlalchemy.sql.expression import func as sqlalchemyfunc


from notd.date_util import date_hour_from_datetime
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.store.schema import TokenTransfersTable

class CollectionOverlapProcessor():
    
    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever = retriever
        self.saver = saver
    
    async def calculate_collection_overlap(self, address):
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
        galleryCountMap = {owner:galleryCount for owner, galleryCount in galleryCountResult}

        retrievedCollectionOverlaps = [RetrievedCollectionOverlap(galleryAddress=address, registryAddress=registryAddress, ownerAddress=ownerAddress, tokenCount=tokenCount, galleryCount=galleryCountMap[ownerAddress]) for registryAddress, ownerAddress, tokenCount in result]
        return retrievedCollectionOverlaps
