import asyncio
import datetime
import json
import os
import sys
import uuid
from collections import defaultdict
from typing import Optional

import asyncclick as click
from core import logging
from core.s3_manager import S3Manager
from core.store.database import Database
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.requester import Requester

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import Collection
from notd.model import CollectionAttribute
from notd.store.retriever import Retriever
from notd.store.schema import TokenMetadatasTable

_CACHE_CONTROL_FINAL_FILE = f'public max-age={60 * 60 * 24 * 365}'

@click.command()
@click.option('-d', '--directory', 'directory', required=True, type=str)
@click.option('-n', '--name', 'name', required=True, type=str)
@click.option('-u', '--upload-id', 'uploadId', required=False, type=str)
@click.option('-o', '--output-filename', 'outputFilename', required=False, type=str)
@click.option('-s', '--start-index', 'startIndex', required=False, type=int, default=0)
@click.option('-i', '--replace-images', 'shouldReplaceImages', default=False, is_flag=True)
async def create_consolidated_metadata(directory: str, name: str, shouldReplaceImages: bool, uploadId: Optional[str], outputFilename: Optional[str], startIndex: int):
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    await s3Manager.connect()
    requester = Requester()

    metadatasDirectory = os.path.join(directory, 'metadata')
    if shouldReplaceImages:
        imagesDirectory = os.path.join(directory, 'image')
        if not uploadId:
            target = f's3://wml-images/nft-gallery-images/{name.replace(" ", "_")}/{uuid.uuid4()}'
            await s3Manager.upload_directory(sourceDirectory=imagesDirectory, target=target, accessControl='public-read', cacheControl=_CACHE_CONTROL_FINAL_FILE)
        else:
            target = f's3://wml-images/nft-gallery-images/{name.replace(" ", "_")}/{uploadId}'
        target = target.replace("s3://wml-images", "https://wml-images.s3.amazonaws.com")

    tokenFiles = []
    for file in os.listdir(metadatasDirectory):
        if not os.path.isfile(os.path.join(metadatasDirectory, file)):
            continue
        # if not file.endswith('.json'):
        #     continue
        if '.' in file:
            continue
        tokenFiles.append(file)
    print(f'Size: {len(tokenFiles)}')

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
    for file in sorted(tokenFiles):
        with open(os.path.join(metadatasDirectory, file), 'r') as metadataFile:
            tokenData = json.loads(metadataFile.read())
        tokenIndex = (int(file.replace('.json', '')) - startIndex) % len(tokenFiles)
        print(file, tokenIndex)
        tokenData['attributes'] = [attribute for attribute in tokenData['attributes'] if attribute['trait_type'] not in {'attribute_count'}]
        tokenData['description'] = ''
        if shouldReplaceImages:
            tokenData['imageUrl'] = f'{target}/{tokenData["image"]}'
        tokenData['imageUrl'] = tokenData["image"]
        tokenData['name'] = tokenData.get('name') or f"PEPE #{tokenIndex}"
        tokenData['frameImageUrl'] = None
        tokenData['registryAddress'] = ''
        tokenData['tokenId'] = tokenIndex
        collectionTokens.append(tokenData)
        for attribute in tokenData['attributes']:
            collectionAttributes[attribute['trait_type']].add(attribute['value'])
        await requester.get(url=tokenData['imageUrl'].replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/'), timeout=60)
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
