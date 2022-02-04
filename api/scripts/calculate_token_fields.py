import csv
import datetime
import os
import sys
import asyncio
import logging
from typing import List
import boto3
import json
from databases import Database


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import asyncclick as click

from notd.store.schema import TokenCollectionsTable, TokenMetadataTable
from notd.store.schema_conversions import collection_from_row
from core.util import date_util
from core.s3_manager import S3Manager

@click.option('-s', '--start-collection-id', 'collectionStartId', required=True, type=int)
@click.option('-e', '--end-collection-id', 'collectionEndId', required=True, type=int)
@click.command()
async def calculate_token_fields(collectionStartId: int, collectionEndId: int,):
    database = Database(f'postgresql://{os.environ["REMOTE_DB_USERNAME"]}:{os.environ["REMOTE_DB_PASSWORD"]}@{os.environ["REMOTE_DB_HOST"]}:{os.environ["REMOTE_DB_PORT"]}/{os.environ["REMOTE_DB_NAME"]}')
    #database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    bucketName = os.environ['S3_BUCKET']
    
    await database.connect()
    query = TokenCollectionsTable.select()
    query = query.where(TokenCollectionsTable.c.collectionId >= collectionStartId)
    query = query.where(TokenCollectionsTable.c.collectionId < collectionEndId)
    collections = [collection_from_row(row) async for row in database.iterate(query=query)]

    rows = []
    fields = set()
    for collection in collections:
        logging.info(f'Working on {collection.collectionId}')
        tokenFiles = await s3manager.list_directory_files(s3Directory=f'{bucketName}/token-metadatas/{collection.address}')
        for index, tokenFile in enumerate(tokenFiles):
            if index > 2:
                break
            tokenDict = json.loads(await s3manager.read_file(sourcePath=f'{tokenFile.bucket}/{tokenFile.path}'))
            tokenDict['attributes'] = ",".join(list(set(key for attribute in tokenDict.get('attributes', []) for key in attribute.keys()))) if isinstance(tokenDict.get('attributes', []), List) else [attribute for attribute in tokenDict.get('attributes')]
            tokenDict['description'] = tokenDict["description"][:10] if tokenDict.get('description') else None 
            tokenDict['collection'] = collection.address
            fields.update(tokenDict.keys())
            rows.append(tokenDict)

    with open('./output.tsv', 'w') as outFile:
        dictWriter = csv.DictWriter(outFile, fields, delimiter='\t')
        dictWriter.writerows(rows)
        
        
    await database.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(calculate_token_fields())
