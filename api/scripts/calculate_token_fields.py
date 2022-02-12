import asyncio
import csv
import json
import logging
import os
import sys
from collections import defaultdict
from typing import List
from typing import Optional

import asyncclick as click
import boto3
from core.s3_manager import S3Manager
from databases import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenCollectionsTable
from notd.store.schema_conversions import collection_from_row


@click.option('-s', '--start-collection-id', 'startCollectionId', required=False, type=int)
@click.option('-e', '--end-collection-id', 'endCollectionId', required=False, type=int)
@click.command()
async def calculate_token_fields(startCollectionId: Optional[int], endCollectionId: Optional[int]):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    bucketName = os.environ['S3_BUCKET']

    await database.connect()
    query = TokenCollectionsTable.select()
    if startCollectionId:
        query = query.where(TokenCollectionsTable.c.collectionId >= startCollectionId)
    if endCollectionId:
        query = query.where(TokenCollectionsTable.c.collectionId < endCollectionId)
    collections = [collection_from_row(row) async for row in database.iterate(query=query)]
    rows = []
    fields = set()
    for collection in collections:
        logging.info(f'Working on {collection.address}')
        collectionDirectory = f'{bucketName}/token-metadatas/{collection.address}/'
        index = 0
        async for tokenFile in s3manager.generate_directory_files(s3Directory=collectionDirectory):
            logging.info(f'Working on file {tokenFile.bucket}/{tokenFile.path}')
            if index > 3:
                break
            try:
                tokenDict = json.loads(await s3manager.read_file(sourcePath=f'{tokenFile.bucket}/{tokenFile.path}'))
                tokenDict['tokenId'] = tokenFile.path.split('/')[2]
                if tokenDict.get('attributes'):
                    tokenDict['attributes'] = ",".join(list(set(key for attribute in tokenDict.get('attributes', []) for key in attribute.keys()))) if isinstance(tokenDict.get('attributes', []), List) else [attribute for attribute in tokenDict.get('attributes')]
                else:
                    tokenDict['attributes'] = None
                tokenDict['description'] = tokenDict["description"][:10] if tokenDict.get('description') else None
                tokenDict['collection'] = collection.address
                fields.update(tokenDict.keys())
                rows.append(tokenDict)
            except Exception as exception:
                logging.exception(exception)
            index += 1

    with open(f'./output{startCollectionId}-{endCollectionId}.tsv', 'w') as outFile:
        dictWriter = csv.DictWriter(outFile, fields, delimiter='\t')
        dictWriter.writeheader()
        dictWriter.writerows(rows)

    fieldCounts = defaultdict(int)
    for row in rows:
        for key, value in row.items():
            if value:
                fieldCounts[key] += 1
    print(fieldCounts)


    await database.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(calculate_token_fields())
