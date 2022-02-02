import csv
import datetime
import os
import sys
import asyncio
import logging
import boto3
import json
from databases import Database


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import asyncclick as click

from notd.store.schema import TokenCollectionsTable, TokenMetadataTable
from notd.store.schema_conversions import collection_from_row
from core.util import date_util
from core.s3_manager import S3Manager


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=True, type=int)
@click.option('-e', '--end-id-number', 'endId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def download_from_s3(startId: int, endId: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    bucketName = os.environ['S3_BUCKET']
    
    await database.connect()
    currentId = startId
    while currentId < endId:
        start = currentId
        end = min(currentId + batchSize, endId)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenCollectionsTable.select()
            query = query.where(TokenCollectionsTable.c.collectionId >= start)
            query = query.where(TokenCollectionsTable.c.collectionId < end)
        collections = [collection_from_row(row) async for row in database.iterate(query=query)]

        with open('api/scripts/names.csv', 'w', newline='') as csvfile:
            for collection in collections:
                fieldNames = []
                for s3_file in (await s3manager.list_directory_files(s3Directory=f'{bucketName}/token-metadatas/{collection.address}')): 
                    s3json = json.loads(await s3manager.read_file(sourcePath=f'{s3_file.bucket}/{s3_file.path}'))
                    fieldNames = [collection.address] + list(s3json.keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldNames)
                    writer.writeheader()
        currentId = currentId + batchSize
        
    await database.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(download_from_s3())
