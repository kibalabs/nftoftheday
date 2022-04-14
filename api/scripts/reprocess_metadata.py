import asyncio
from core import logging
import os
import sys

import asyncclick as click
from core.store.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.saver import Saver
from notd.store.schema import TokenMetadatasTable
from notd.store.schema_conversions import token_metadata_from_row
from notd.token_metadata_processor import TokenMetadataProcessor


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=True, type=int)
@click.option('-e', '--end-id-number', 'endId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def reprocess_metadata(startId: int, endId: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database)
    tokenMetadataProcessor = TokenMetadataProcessor(requester=None, ethClient=None, s3manager=None, bucketName=None)

    await database.connect()

    currentId = startId
    while currentId < endId:
        start = currentId
        end = min(currentId + batchSize, endId)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenMetadatasTable.select()
            query = query.where(TokenMetadatasTable.c.tokenMetadataId >= start)
            query = query.where(TokenMetadatasTable.c.tokenMetadataId < end)
            query = query.where(TokenMetadatasTable.c.metadataUrl.startswith('data:'))
            query = query.where(TokenMetadatasTable.c.name == None)
            tokenMetadatasToChange = [token_metadata_from_row(row) async for row in database.execute(query=query)]
            logging.info(f'Updating {len(tokenMetadatasToChange)} transfers...')
            for tokenMetadata in tokenMetadatasToChange:
                try:
                    tokenMetadataDict = tokenMetadataProcessor._resolve_data(dataString=tokenMetadata.metadataUrl, registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId)
                    if tokenMetadataDict:
                        logging.info(f'Processed: {tokenMetadata.tokenMetadataId}')
                        await saver.update_token_metadata(tokenMetadataId=tokenMetadata.tokenMetadataId, name=tokenMetadataDict.get('name') ,imageUrl=tokenMetadataDict.get('image'), description=tokenMetadataDict.get('description'), attributes=tokenMetadataDict.get('attributes', []))
                except Exception as e:
                    logging.exception(f'Error processing {tokenMetadata.tokenMetadataId}: {e}')
        currentId = currentId + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata())
