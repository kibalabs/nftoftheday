import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from databases.core import Database
from notd.store.schema import TokenTransfersTable
from sqlalchemy.sql.expression import func as sqlalchemyfunc


@click.command()
async def daily_new_registries():
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')#pylint: disable=invalid-name

    await database.connect()
    query = TokenTransfersTable.select()
    query = query.where(
        TokenTransfersTable.c.blockDate.in_(TokenTransfersTable.select().with_only_columns([sqlalchemyfunc.min(TokenTransfersTable.c.blockDate)]).group_by(TokenTransfersTable.c.registryAddress)))
    query = query.where(sqlalchemyfunc.date(TokenTransfersTable.c.blockDate) == sqlalchemyfunc.current_date())
    rows = await database.fetch_all(query)
    for row in rows:
        logging.info(f'Registry {row[2]} ')

    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(daily_new_registries())
