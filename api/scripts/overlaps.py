import asyncio
import csv
import os
import sys
from collections import defaultdict

from core.store.database import Database
from sqlalchemy.sql.expression import func as sqlalchemyfunc

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import GALLERY_COLLECTIONS, COLLECTION_SPRITE_CLUB_ADDRESS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView
from notd.store.schema_conversions import collection_overlap_from_row


async def collection_overlaps():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["REMOTE_DB_USERNAME"], password=os.environ["REMOTE_DB_PASSWORD"], host=os.environ["REMOTE_DB_HOST"], port=os.environ["REMOTE_DB_PORT"], name=os.environ["REMOTE_DB_NAME"])
    databaseConnectionString1 = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    database1 = Database(connectionString=databaseConnectionString1)

    retriever = Retriever(database=database)
    saver = Saver(database=database1)
    await database.connect()
    await database1.connect()
    # for address in GALLERY_COLLECTIONS:
    address = COLLECTION_SPRITE_CLUB_ADDRESS
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
    result = await retriever.database.execute(query=query)
    
    galleryCountQuery = (
        UserRegistryOrderedOwnershipsMaterializedView.select()
        .with_only_columns([UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress,sqlalchemyfunc.count(UserRegistryOrderedOwnershipsMaterializedView.c.tokenId)])
        .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == address)
        .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
    )
    galleryCountResult = await retriever.database.execute(query=galleryCountQuery)
    galleryCountMap = {owner:galleryCount for owner, galleryCount in galleryCountResult}
    # print(len(galleryCountMap), sum(list(galleryCountMap.values())))
    # return
    async with saver.create_transaction() as connection:
        for  ownerAddress, registryAddress , tokenCount in result:
            await saver.create_collection_overlap(galleryAddress=address, registryAddress=registryAddress, ownerAddress=ownerAddress, tokenCount=tokenCount, galleryCount=galleryCountMap[ownerAddress], connection=connection)
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(collection_overlaps())
