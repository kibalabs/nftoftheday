import asyncio
import os
import sys

import asyncclick as click
from core import logging
from core.store.database import Database
from core.util.chain_util import normalize_address
from core.store.retriever import IntegerFieldFilter

from sqlalchemy.sql.expression import func as sqlalchemyfunc
from sqlalchemy.sql.expression import or_

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row
from notd.store.retriever import Retriever
from notd.store.saver import Saver


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    await database.connect()

    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlockNumber)
        logging.info(f'Working on {start} to {end}...')
        query = ( TokenTransfersTable.select()
                    .with_only_columns([
                        TokenTransfersTable.c.tokenTransferId,
                        TokenTransfersTable.c.toAddress,
                        TokenTransfersTable.c.registryAddress,
                        TokenTransfersTable.c.fromAddress,
                        TokenTransfersTable.c.operatorAddress,
                        TokenTransfersTable.c.contractAddress
                        ])
                    .where(TokenTransfersTable.c.blockNumber >= start)
                    .where(TokenTransfersTable.c.blockNumber < end)
                    )
        result = await database.execute(query=query)
        tokenTransferIdsToChange = [row[0] for row in result if normalize_address(row[1]) != row[1] or normalize_address(row[2]) != row[2] or normalize_address(row[3]) != row[3] or normalize_address(row[4]) != row[4] or normalize_address(row[5]) != row[5] ]
        print(tokenTransferIdsToChange)
        tokenTransfersToChange = await retriever.list_token_transfers(fieldFilters=[IntegerFieldFilter(fieldName=TokenTransfersTable.c.tokenTransferId.key, containedIn=tokenTransferIdsToChange)])
        logging.info(f'Normalizing {len(tokenTransferIdsToChange)} transfers...')
        for tokenTransfer in tokenTransfersToChange:
            values = {
                TokenTransfersTable.c.toAddress.key: normalize_address(tokenTransfer.toAddress),
                TokenTransfersTable.c.fromAddress.key: normalize_address(tokenTransfer.fromAddress),
                TokenTransfersTable.c.registryAddress.key: normalize_address(tokenTransfer.registryAddress),
                TokenTransfersTable.c.contractAddress.key: normalize_address(tokenTransfer.contractAddress),
                TokenTransfersTable.c.operatorAddress.key: normalize_address(tokenTransfer.operatorAddress),
            }
            query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenTransfer.tokenTransferId).values(values)
            await database.execute(query=query)
        currentBlockNumber = end
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
