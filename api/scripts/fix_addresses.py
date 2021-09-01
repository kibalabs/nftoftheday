
import os
import asyncio
from sqlalchemy import create_engine
from notd.chain_utils import normalize_address
from notd.store.schema import TokenTransfersTable as table

async def fix_address():
    dbString = (f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')# pylint: disable=invalid-name
    db = create_engine(dbString) # pylint: disable=invalid-name

    conn = db.connect()

    result_set = conn.execute(table.select().order_by(table.c.id) ) # pylint: disable=invalid-name
    for toAddress,fromAddress,_ in result_set:
        if len(toAddress) > 42:
            fixedAddress = (normalize_address(toAddress))
            update = table.update().where(table.c.to_address == toAddress).values(to_address = fixedAddress)
            conn.execute(update)
        if len(fromAddress) > 42:
            fixedAddress = (normalize_address(fromAddress))
            update = table.update().where(table.c.from_address == fromAddress).values(from_address = fixedAddress)
            conn.execute(update)

if __name__ == '__main__':
    asyncio.run(fix_address())
