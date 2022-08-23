import asyncio
import os
import sys

import csv
import asyncclick as click
from core import logging
from core.store.database import Database
from core.util.chain_util import normalize_address

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenTransfersTable


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def fix_address(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    dataColumns =['start', 'end', 'badOperatorCount', 'badContractCount']
    await database.connect()
    with open('un-normalizedBlocks.csv', mode='w') as blocksCsvFile:
        currentBlockNumber = startBlockNumber
        writer = csv.DictWriter(blocksCsvFile, fieldnames=dataColumns)
        while currentBlockNumber < endBlockNumber:
            badOperatorCount = 0
            badContractCount = 0
            start = currentBlockNumber
            end = min(currentBlockNumber + batchSize, endBlockNumber)
            logging.info(f'Working on {start} to {end}...')
            query = ( TokenTransfersTable.select()
                        .with_only_columns([TokenTransfersTable.c.operatorAddress, TokenTransfersTable.c.contractAddress])
                        .where(TokenTransfersTable.c.blockNumber >= start)
                        .where(TokenTransfersTable.c.blockNumber < end)
                        )
            result = await database.execute(query=query)
            for (operatorAddress, contractAddress) in result:
                if normalize_address(operatorAddress) != operatorAddress:
                    badOperatorCount += 1
                if normalize_address(contractAddress) != contractAddress:
                    badContractCount += 1
            writer.writerow({"start": start, "end": end, "badOperatorCount": badOperatorCount, "badContractCount": badContractCount})
            currentBlockNumber = end
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_address())
