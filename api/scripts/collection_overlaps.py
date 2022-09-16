import asyncio
import csv
import os
import sys
from collections import defaultdict

from core.store.database import Database
from sqlalchemy.sql.expression import func as sqlalchemyfunc

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionOverlapsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView


async def collection_overlaps():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["REMOTE_DB_USERNAME"], password=os.environ["REMOTE_DB_PASSWORD"], host=os.environ["REMOTE_DB_HOST"], port=os.environ["REMOTE_DB_PORT"], name=os.environ["REMOTE_DB_NAME"])    
    databaseConnectionString1 = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    # databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    database1 = Database(connectionString=databaseConnectionString1)
    retriever = Retriever(database=database)
    saver = Saver(database=database1)
    await database1.connect()
    await database.connect()
    for collection in GALLERY_COLLECTIONS:
        # query = (
        #     TokenCollectionOverlapsTable.select()
        #     .with_only_columns([TokenCollectionOverlapsTable.c.ownerAddress])
        #     .where(TokenCollectionOverlapsTable.c.registryAddress == collection)
        # )
        query = (
            TokenOwnershipsTable.select()
            .with_only_columns([TokenOwnershipsTable.c.ownerAddress])
            .where(TokenOwnershipsTable.c.registryAddress == collection)
        )
        result = await retriever.database.execute(query=query)
        holders = {row[0] for row in result}
        print('here-1', len(holders))
        collectionsHeldByHolders = set()
        holdingQuery = (
            TokenOwnershipsTable.select()
            .with_only_columns([TokenOwnershipsTable.c.registryAddress.distinct()])
            .where(TokenOwnershipsTable.c.ownerAddress.in_(holders))
        )
        holdingResult = await retriever.database.execute(query=holdingQuery)
        holding = {registryAddress for registryAddress, in holdingResult}
        collectionsHeldByHolders = collectionsHeldByHolders | holding
        print('here-2', len(collectionsHeldByHolders))
        for registryAddress in collectionsHeldByHolders:
            print(registryAddress)
            overlapQuery = (
                UserRegistryOrderedOwnershipsMaterializedView.select()
                .with_only_columns([sqlalchemyfunc.count(TokenOwnershipsTable.c.ownerAddress.distinct()),
                                    sqlalchemyfunc.count(TokenOwnershipsTable.c.tokenId)])
                .join(TokenOwnershipsTable, TokenOwnershipsTable.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
                .where(TokenOwnershipsTable.c.registryAddress == registryAddress)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex == 1)
            )
            overlapResult = await retriever.database.execute(query=overlapQuery)
            # overlap = [(collection, registryAddress, ownerCount, tokenCount) for ownerCount, tokenCount in overlapResult]
            await asyncio.gather(*[saver.create_collection_overlap(registryAddress=registryAddress, galleryAddress=collection, ownerCount=ownerCount, tokenCount=tokenCount) for ownerCount, tokenCount in overlapResult]) 
        break
        # print(collection)
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(collection_overlaps())
