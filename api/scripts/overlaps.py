import asyncio
from collections import defaultdict
import os
import sys
from core.store.database import Database
from sqlalchemy.sql.expression import func as sqlalchemyfunc

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import GALLERY_COLLECTIONS
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView
from notd.store.schema import TokenOwnershipsTable
from notd.store.retriever import Retriever


async def collection_overlaps(address: str):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["REMOTE_DB_USERNAME"], password=os.environ["REMOTE_DB_PASSWORD"], host=os.environ["REMOTE_DB_HOST"], port=os.environ["REMOTE_DB_PORT"], name=os.environ["REMOTE_DB_NAME"])

    # databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    await database.connect()
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
    ownerRegistryPairs = list(result)
    print(ownerRegistryPairs)
    # with open('text.txt', 'w') as f:
    #     f.write(str(registryOwnerMap))
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(collection_overlaps(address='0x2744fE5e7776BCA0AF1CDEAF3bA3d1F5cae515d3'))