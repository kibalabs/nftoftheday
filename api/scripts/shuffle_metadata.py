import asyncio
from collections import defaultdict
import datetime
import json
import os
import random
import sys
from typing import Optional
import uuid

import asyncclick as click
from core import logging
from core.store.database import Database
from core.store.retriever import StringFieldFilter
from core.util import file_util
from core.s3_manager import S3Manager

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import Collection, CollectionAttribute
from notd.store.retriever import Retriever
from notd.store.schema import TokenMetadatasTable


_CACHE_CONTROL_FINAL_FILE = f'public max-age={60 * 60 * 24 * 365}'

@click.command()
@click.option('-d', '--directory', 'directory', required=True, type=str)
@click.option('-o', '--output-directory', 'outputDirectory', required=False, type=str)
async def shuffle_metadata(directory: str, outputDirectory: Optional[str]):
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    await s3Manager.connect()

    metadatasDirectory = os.path.join(directory, 'metadata')
    imagesDirectory = os.path.join(directory, 'image')
    outputDirectory = outputDirectory or os.path.join(directory, 'shuffled')
    outputMetadatasDirectory = os.path.join(outputDirectory, 'metadata')
    await file_util.create_directory(directory=outputMetadatasDirectory)
    outputImagesDirectory = os.path.join(outputDirectory, 'image')
    await file_util.create_directory(directory=outputImagesDirectory)

    imageFileNames = [name.replace('.png', '') for name in os.listdir(imagesDirectory) if '.png' in name]
    random.shuffle(imageFileNames)
    for index, imageFileName in enumerate(imageFileNames):
        with open(os.path.join(imagesDirectory, f'{imageFileName}.png'), 'rb') as imageFile:
            with open(os.path.join(outputImagesDirectory, f'{index}.png'), 'wb') as outputImageFile:
                outputImageFile.write(imageFile.read())
        with open(os.path.join(metadatasDirectory, f'{imageFileName}.json'), 'r') as metadataFile:
            with open(os.path.join(outputMetadatasDirectory, f'{index}.json'), 'w') as outputMetadataFile:
                content = json.load(metadataFile)
                nameParts = content['name'].split('#')
                nameParts[-1] = f'{index}'
                content['name'] = '#'.join(nameParts)
                content['image'] = f'{index}.png'
                outputMetadataFile.write(json.dumps(content))


    # collectionTokens = []
    # for file in os.listdir(metadatasDirectory):
    #     if not file.endswith('.json'):
    #         continue
    #     if not os.path.isfile(os.path.join(metadatasDirectory, file)):
    #         continue
    #     with open(os.path.join(metadatasDirectory, file), 'r') as metadataFile:
    #         tokenData = json.loads(metadataFile.read())
    #     tokenData['attributes'] = [attribute for attribute in tokenData['attributes'] if attribute['trait_type'] not in {'attribute_count'}]
    #     tokenData['description'] = ''
    #     tokenData['imageUrl'] = f'{target}/{tokenData["image"]}'
    #     tokenData['frameImageUrl'] = None
    #     tokenData['registryAddress'] = ''
    #     tokenData['tokenId'] = file.replace('.json', '')
    #     collectionTokens.append(tokenData)
    #     for attribute in tokenData['attributes']:
    #         collectionAttributes[attribute['trait_type']].add(attribute['value'])
    # with open(outputDirectory, 'w') as outputFile:
    #     outputFile.write(json.dumps({
    #         "collection": collection,
    #         "collectionAttributes": [{'name': name, 'values': list(values)} for name, values in collectionAttributes.items()],
    #         "collectionTokens": sorted(collectionTokens, key=lambda token: int(token['tokenId'])),
    #     }))

    await s3Manager.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(shuffle_metadata())
