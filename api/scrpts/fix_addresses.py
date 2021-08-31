
import os
import asyncio
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, MetaData
from notd.chain_utils import normalize_address

async def fix_address():
    db_string = (f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')# pylint: disable=invalid-name
    db = create_engine(db_string) # pylint: disable=invalid-name
    meta = MetaData(db) # pylint: disable=invalid-name
    table = Table('tbl_token_transfers', meta,
                       Column('to_address', String),
                       Column('from_address', String),
                       Column('id',String)) # pylint: disable=invalid-name
    conn=db.connect()

    result_set = conn.execute(table.select().order_by(table.c.id) ) # pylint: disable=invalid-name
    for to_address,from_address,_ in result_set: # pylint: disable=invalid-name
        if len(to_address)>42:
            fixedAddress=(normalize_address(to_address))  # pylint: disable=invalid-name
            update = table.update().where(table.c.to_address==to_address).values(to_address = fixedAddress)
            conn.execute(update)
        if len(from_address)>42:
            fixedAddress=(normalize_address(from_address))  # pylint: disable=invalid-name
            update = table.update().where(table.c.from_address==from_address).values(from_address = fixedAddress) # pylint: disable=no-value-for-parameter
            conn.execute(update)

if __name__ == '__main__':
    asyncio.run(fix_address())
