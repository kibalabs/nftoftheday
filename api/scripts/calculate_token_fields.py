import asyncio
import csv
import json
import os
import sys
from collections import defaultdict
from typing import List
from typing import Optional

import asyncclick as click
from core import logging
from core.s3_manager import S3Manager
from core.store.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import TokenCollectionsTable
from notd.store.schema_conversions import collection_from_row


@click.option('-s', '--start-collection-id', 'startCollectionId', required=False, type=int)
@click.option('-e', '--end-collection-id', 'endCollectionId', required=False, type=int)
@click.command()
async def calculate_token_fields(startCollectionId: Optional[int], endCollectionId: Optional[int]):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    bucketName = os.environ['S3_BUCKET']

    await database.connect()
    await s3Manager.connect()
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
        async for tokenFile in s3Manager.generate_directory_files(s3Directory=collectionDirectory):
            logging.info(f'Working on file {tokenFile.bucket}/{tokenFile.path}')
            if index > 3:
                break
            try:
                tokenDict = json.loads(await s3Manager.read_file(sourcePath=f'{tokenFile.bucket}/{tokenFile.path}'))
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
    await s3Manager.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(calculate_token_fields())
