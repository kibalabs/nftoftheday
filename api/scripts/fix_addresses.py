
import os
import asyncio
import asyncclick as click

from sqlalchemy import create_engine
from notd.chain_utils import normalize_address
from notd.store.schema import TokenTransfersTable as table

@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    dbString = (f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')#pylint: disable=invalid-name
    db = create_engine(dbString) # pylint: disable=invalid-name

    conn = db.connect()

    resultSet = conn.execute(table.select().where(table.c.block_number.between(startBlockNumber,endBlockNumber)).order_by(table.c.id) ) #pylint: disable=invalid-name
    for toAddress, fromAddress, _ in resultSet:
        if len(toAddress) > 42:
            fixedAddress = normalize_address(toAddress)
            update = table.update().where(table.c.to_address == toAddress).values(to_address = fixedAddress)
            conn.execute(update)
        if len(fromAddress) > 42:
            fixedAddress = normalize_address(fromAddress)
            update = table.update().where(table.c.from_address == fromAddress).values(from_address = fixedAddress)
            conn.execute(update)

if __name__ == '__main__':
    asyncio.run(fix_address())
