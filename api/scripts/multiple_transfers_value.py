import asyncio
import logging
import os
import sys
import sqlalchemy
from core.store.database import Database
import asyncclick as click


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable

@click.command()
@click.option('-s', '--start-block-number', 'startBlock', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlock', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def multiple_transfers_value(startBlock: int, endBlock: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)

    await database.connect()
    currentBlockNumber = startBlock
    while currentBlockNumber < endBlock:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlock)
        logging.info(f'Working on {start} to {end}...')
        async with saver.create_transaction() as connection:
            query = TokenTransfersTable.select() \
                        .with_only_columns([TokenTransfersTable.c.blockNumber, TokenTransfersTable.c.transactionHash, sqlalchemy.func.round(TokenTransfersTable.c.value/sqlalchemy.func.count(TokenTransfersTable.c.transactionHash))]) \
                        .filter(TokenTransfersTable.c.blockNumber >= start) \
                        .filter(TokenTransfersTable.c.blockNumber < end) \
                        .group_by(TokenTransfersTable.c.transactionHash,TokenTransfersTable.c.blockNumber, TokenTransfersTable.c.value,) \
                        .having(sqlalchemy.func.count(TokenTransfersTable.c.transactionHash) > 1)
            
            result = await database.execute(query=query)
            transactionHashValuepairs = [(row[1],row[2]) for row in result]
            logging.info(f'Updating {len(transactionHashValuepairs)} transfers...')
            for transactionHash, value in transactionHashValuepairs:
                values ={}
                values[TokenTransfersTable.c.value.key] = value        
                query = TokenTransfersTable.update(TokenTransfersTable.c.transactionHash == transactionHash).values(values)
                await database.execute(query=query, connection=connection)
        currentBlockNumber = endBlock

    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(multiple_transfers_value())
