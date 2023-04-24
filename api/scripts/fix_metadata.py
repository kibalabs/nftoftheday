import asyncio
import os
import sys

import asyncclick as click
from core import logging
from core.store.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenMetadatasTable


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=True, type=int)
@click.option('-e', '--end-id-number', 'endId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def reprocess_metadata(startId: int, endId: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)

    await database.connect()

    currentId = startId
    while currentId < endId:
        start = currentId
        end = min(currentId + batchSize, endId)
        logging.info(f'Working on {start} to {end}...')
        async with database.create_transaction() as connection:
            imageFixingQuery = (
                TokenMetadatasTable.update()
                    .where(TokenMetadatasTable.c.tokenMetadataId >= start)
                    .where(TokenMetadatasTable.c.tokenMetadataId < end)
                    .where(TokenMetadatasTable.c.imageUrl == 'None')
                    .values({TokenMetadatasTable.c.imageUrl: None})
                    .returning(TokenMetadatasTable.c.tokenMetadataId)
            )
            result = await database.execute(query=imageFixingQuery, connection=connection)
            updatedTokenIds = [tokenId for (tokenId, ) in result]
            print('updated imageUrls:', len(updatedTokenIds), updatedTokenIds[:3])
            youtubeFixingQuery = (
                TokenMetadatasTable.update()
                    .where(TokenMetadatasTable.c.tokenMetadataId >= start)
                    .where(TokenMetadatasTable.c.tokenMetadataId < end)
                    .where(TokenMetadatasTable.c.youtubeUrl == 'None')
                    .values({TokenMetadatasTable.c.youtubeUrl: None})
                    .returning(TokenMetadatasTable.c.tokenMetadataId)
            )
            result = await database.execute(query=youtubeFixingQuery, connection=connection)
            updatedTokenIds = [tokenId for (tokenId, ) in result]
            print('updated youtubeUrls', len(updatedTokenIds), updatedTokenIds[:3])
            animationFixingQuery = (
                TokenMetadatasTable.update()
                    .where(TokenMetadatasTable.c.tokenMetadataId >= start)
                    .where(TokenMetadatasTable.c.tokenMetadataId < end)
                    .where(TokenMetadatasTable.c.animationUrl == 'None')
                    .values({TokenMetadatasTable.c.animationUrl: None})
                    .returning(TokenMetadatasTable.c.tokenMetadataId)
            )
            result = await database.execute(query=animationFixingQuery, connection=connection)
            updatedTokenIds = [tokenId for (tokenId, ) in result]
            print('updated animationUrls', len(updatedTokenIds), updatedTokenIds[:3])
            frameImageFixingQuery = (
                TokenMetadatasTable.update()
                    .where(TokenMetadatasTable.c.tokenMetadataId >= start)
                    .where(TokenMetadatasTable.c.tokenMetadataId < end)
                    .where(TokenMetadatasTable.c.frameImageUrl == 'None')
                    .values({TokenMetadatasTable.c.frameImageUrl: None})
                    .returning(TokenMetadatasTable.c.tokenMetadataId)
            )
            result = await database.execute(query=frameImageFixingQuery, connection=connection)
            updatedTokenIds = [tokenId for (tokenId, ) in result]
            print('updated frameImageUrls', len(updatedTokenIds), updatedTokenIds[:3])
        currentId = currentId + batchSize
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata())
