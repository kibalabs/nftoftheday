import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from databases.core import Database
from sqlalchemy.sql.expression import distinct, func as sqlalchemyfunc

from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def check_all_processed(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["REMOTE_DB_USERNAME"]}:{os.environ["REMOTE_DB_PASSWORD"]}@{os.environ["REMOTE_DB_HOST"]}:{os.environ["REMOTE_DB_PORT"]}/{os.environ["REMOTE_DB_NAME"]}')
    #database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')#pylint: disable=invalid-name
    blocks_processed = []
    await database.connect()
    query = TokenTransfersTable.select().with_only_columns([TokenTransfersTable.c.blockNumber])
    query = query.where(TokenTransfersTable.c.blockNumber.in_(
        TokenTransfersTable.select().with_only_columns([TokenTransfersTable.c.blockNumber]).group_by(TokenTransfersTable.c.blockNumber)
    ))
    rows = await database.fetch_all(query)
    for row in rows:
        blocks_processed.append(row[0])
    await database.disconnect()
    print(f'Checking for x')
    for i in range(3919706,13708119):
        if i not in blocks_processed:
            print(i)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(check_all_processed())
