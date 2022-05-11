import asyncio
import json
import os
import sys

import asyncclick as click
from core import logging
from core.store.database import Database
from core.store.retriever import StringFieldFilter
from core.util import chain_util

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.retriever import Retriever
from notd.store.schema import TokenMetadatasTable


@click.command()
@click.option('-c', '--collection-address', 'address', required=True, type=str)
@click.option('-o', '--output-filename', 'outputFilename', required=False, type=str)
async def create_consolidated_metadata(address: str, outputFilename: str):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)

    await database.connect()
    address = chain_util.normalize_address(value=address)
    collection = await retriever.get_collection_by_address(address=address)
    tokens = await retriever.list_token_metadatas(fieldFilters=[StringFieldFilter(fieldName=TokenMetadatasTable.c.registryAddress.key, eq=address)])
    with open(outputFilename, 'w') as outputFile:
        outputFile.write(json.dumps({
            'address': collection.address,
            'name': collection.name,
            'symbol': collection.symbol,
            'description': collection.description,
            'imageUrl': collection.imageUrl,
            'twitterUsername': collection.twitterUsername,
            'instagramUsername': collection.instagramUsername,
            'wikiUrl': collection.wikiUrl,
            'openseaSlug': collection.openseaSlug,
            'url': collection.url,
            'discordUrl': collection.discordUrl,
            'bannerImageUrl': collection.bannerImageUrl,
            'doesSupportErc721': collection.doesSupportErc721,
            'doesSupportErc1155': collection.doesSupportErc1155,
            'tokens': [{
                'registryAddress': token.registryAddress,
                'tokenId': token.tokenId,
                'metadataUrl': token.metadataUrl,
                'name': token.name,
                'description': token.description,
                'imageUrl': token.imageUrl,
                'animationUrl': token.animationUrl,
                'youtubeUrl': token.youtubeUrl,
                'backgroundColor': token.backgroundColor,
                'frameImageUrl': token.frameImageUrl,
                'attributes': token.attributes,
            } for token in tokens],
        }))
    await database.disconnect()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(create_consolidated_metadata())
