import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import asyncio
import base64
import json
import logging

import asyncclick as click
from databases.core import Database

from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable
from notd.store.schema_conversions import token_metadata_from_row


@click.command()
@click.option('-s', '--start-id-number', 'startIDNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endIDNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def fix_metadata(startIDNumber: int, endIDNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database)
    await database.connect()

    currentIDNumber = startIDNumber
    while currentIDNumber < endIDNumber:
        start = currentIDNumber
        end = min(currentIDNumber + batchSize, endIDNumber)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenMetadataTable.select()
            query = query.where(TokenMetadataTable.c.tokenMetadataId >= start)
            query = query.where(TokenMetadataTable.c.tokenMetadataId < end)
            query = query.where(TokenMetadataTable.c.metadataUrl.startswith('data:application/json;base64'))
            print(query)
            tokenMetadatasToChange = [token_metadata_from_row(row) async for row in database.iterate(query=query)]
            logging.info(f'Updating {len(tokenMetadatasToChange)} transfers...')
            for tokenMetadata in tokenMetadatasToChange:
                basestr = tokenMetadata.metadataUrl.replace('data:application/json;base64', '')
                base64Metadata = basestr.encode('utf-8')
                metadataBytes = base64.b64decode(base64Metadata)
                tokenMetadataDict = json.loads(metadataBytes.decode('utf-8'))
                await saver.update_token_metadata(tokenMetadataId=tokenMetadata.tokenMetadataId, name=tokenMetadataDict.get('name') ,imageUrl=tokenMetadataDict.get('image'), description=tokenMetadataDict.get('description'), attributes=tokenMetadataDict.get('attributes'))
    currentIDNumber = currentIDNumber + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(fix_metadata())
