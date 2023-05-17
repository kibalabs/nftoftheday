import tqdm
import asyncio
import logging
import os
import sys
# import 
import asyncclick as click
import sqlalchemy

from core.store.database import Database
from core.requester import Requester

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from notd.store.schema import TokenMetadatasTable
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.model import OPENSEA_SHARED_STOREFRONT_ADDRESS
from notd.collection_manager import CollectionManager
from notd.sub_collection_manager import SubCollectionManager
from notd.sub_collection_processor import SubCollectionProcessor
from notd.sub_collection_token_manager import SubCollectionTokenManager
from notd.sub_collection_token_processor import SubCollectionTokenProcessor

openseaApiKey = os.environ['OPENSEA_API_KEY']


@click.command()
async def backfill_sub_collection_tokens():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    collectionManager = CollectionManager(saver=saver, retriever=retriever, tokenQueue=None, collectionProcessor=None)
    subCollectionProcessor = SubCollectionProcessor(openseaRequester=openseaRequester, collectionManager=collectionManager)
    subCollectionManager = SubCollectionManager(retriever=retriever, saver=saver, workQueue=None, subCollectionProcessor=subCollectionProcessor)
    subCollectionTokenProcessor = SubCollectionTokenProcessor(openseaRequester=openseaRequester)
    subCollectionTokenManager = SubCollectionTokenManager(retriever=retriever, saver=saver, subCollectionTokenProcessor=subCollectionTokenProcessor, subCollectionManager=subCollectionManager)

    await database.connect()
    query = (
        sqlalchemy.select(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId)
        .where(TokenMetadatasTable.c.registryAddress == OPENSEA_SHARED_STOREFRONT_ADDRESS)
    )
    tokenKeyResult = await retriever.database.execute(query=query)
    tokenKeyRows = list(tokenKeyResult.mappings())

    for row in tqdm.tqdm(tokenKeyRows):
        try:
            await subCollectionTokenManager.update_sub_collection_token(registryAddress=row['registryAddress'], tokenId=row['tokenId'])
        except Exception:
            await asyncio.sleep(1)
    await database.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_sub_collection_tokens())
