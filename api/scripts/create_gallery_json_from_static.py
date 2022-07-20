import asyncio
from collections import defaultdict
import datetime
import json
import os
import sys
from typing import Optional
import uuid

import asyncclick as click
from core import logging
from core.store.database import Database
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.s3_manager import S3Manager

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import Collection, CollectionAttribute
from notd.store.retriever import Retriever
from notd.store.schema import TokenMetadatasTable


_CACHE_CONTROL_FINAL_FILE = f'public max-age={60 * 60 * 24 * 365}'

@click.command()
@click.option('-d', '--directory', 'directory', required=True, type=str)
@click.option('-n', '--name', 'name', required=True, type=str)
@click.option('-u', '--upload-id', 'uploadId', required=True, type=str)
@click.option('-o', '--output-filename', 'outputFilename', required=False, type=str)
async def create_consolidated_metadata(directory: str, name: str, uploadId: str, outputFilename: Optional[str]):
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    await s3Manager.connect()

    metadatasDirectory = os.path.join(directory, 'metadata')
    imagesDirectory = os.path.join(directory, 'image')
    if not uploadId:
        target = f's3://wml-images/nft-gallery-images/{name.replace(" ", "_")}/{uuid.uuid4()}'
        await s3Manager.upload_directory(sourceDirectory=imagesDirectory, target=target, accessControl='public-read', cacheControl=_CACHE_CONTROL_FINAL_FILE)
    else:
        target = f's3://wml-images/nft-gallery-images/{name.replace(" ", "_")}/{uploadId}'
    target = target.replace("s3://wml-images", "https://wml-images.s3.amazonaws.com")

    outputFilename = outputFilename or 'metadata_consolidated.json'
    collection = {
        "address": '',
        "name": name,
        "symbol": None,
        "description": None,
        "imageUrl": None,
        "twitterUsername": None,
        "instagramUsername": None,
        "wikiUrl": None,
        "openseaSlug": None,
        "url": None,
        "discordUrl": None,
        "bannerImageUrl": None,
        "doesSupportErc721": True,
        "doesSupportErc1155": False,
    }
    collectionAttributes = defaultdict(set)
    collectionTokens = []
    for file in os.listdir(metadatasDirectory):
        if not file.endswith('.json'):
            continue
        if not os.path.isfile(os.path.join(metadatasDirectory, file)):
            continue
        with open(os.path.join(metadatasDirectory, file), 'r') as metadataFile:
            tokenData = json.loads(metadataFile.read())
        tokenData['attributes'] = [attribute for attribute in tokenData['attributes'] if attribute['trait_type'] not in {'attribute_count'}]
        tokenData['description'] = ''
        tokenData['imageUrl'] = f'{target}/{tokenData["image"]}'
        tokenData['frameImageUrl'] = None
        tokenData['registryAddress'] = ''
        tokenData['tokenId'] = file.replace('.json', '')
        collectionTokens.append(tokenData)
        for attribute in tokenData['attributes']:
            collectionAttributes[attribute['trait_type']].add(attribute['value'])
    with open(outputFilename, 'w') as outputFile:
        outputFile.write(json.dumps({
            "collection": collection,
            "collectionAttributes": [{'name': name, 'values': list(values)} for name, values in collectionAttributes.items()],
            "collectionTokens": sorted(collectionTokens, key=lambda token: int(token['tokenId'])),
        }))

    await s3Manager.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_consolidated_metadata())
