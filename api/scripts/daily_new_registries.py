import asyncio
import os
import sys

import asyncclick as click
from core import logging
from core.store.database import Database
from sqlalchemy.sql.expression import func as sqlalchemyfunc

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenTransfersTable


@click.command()
async def daily_new_registries():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)

    await database.connect()
    query = TokenTransfersTable.select()
    query = query.where(
        TokenTransfersTable.c.blockDate.in_(TokenTransfersTable.select().with_only_columns(sqlalchemyfunc.min(TokenTransfersTable.c.blockDate)).group_by(TokenTransfersTable.c.registryAddress)))
    query = query.where(sqlalchemyfunc.date(TokenTransfersTable.c.blockDate) == sqlalchemyfunc.current_date())
    rows = await database.fetch_all(query)
    for row in rows:
        logging.info(f'Registry {row[2]} ')

    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(daily_new_registries())
