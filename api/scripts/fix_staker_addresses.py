import os
import sys
import asyncio

import logging
from core.store.database import Database
from core.util.chain_util import normalize_address

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenStakingsTable
from notd.store.retriever import Retriever
from notd.store.saver import Saver

async def fix_staker_address():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    await database.connect()
    async with saver.create_transaction() as connection:
        tokenStakings = await retriever.list_token_stakings()
        for tokenStaking in tokenStakings:
            values = {
                TokenStakingsTable.c.ownerAddress.key: normalize_address(tokenStaking.ownerAddress),
            }
            query = TokenStakingsTable.update().where(TokenStakingsTable.c.tokenStakingId == tokenStaking.tokenStakingId).values(values)
            await retriever.database.execute(query=query, connection=connection)
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_staker_address())