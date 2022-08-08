import asyncio
import os
from core.requester import Requester
from notd.store.saver import Saver
from notd.store.retriever import Retriever
from core.store.database import Database
from core.util import date_util
from notd.model import COLLECTION_GOBLINTOWN_ADDRESS, COLLECTION_MDTP_ADDRESS, COLLECTION_SPRITE_CLUB_ADDRESS
from notd.token_listing_processor import TokenListingProcessor
from notd.lock_manager import LockManager
openseaApiKey = os.environ['OPENSEA_API_KEY']


async def run_async_goblin():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester, lockManger = LockManager(retriever=retriever, saver=saver))

    await database.connect()
    g = await tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_GOBLINTOWN_ADDRESS, startDate=date_util.datetime_from_now())
    print(g)
    await database.disconnect()

async def run_async_sprite():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester, lockManger = LockManager(retriever=retriever, saver=saver))

    await database.connect()
    s = await tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_SPRITE_CLUB_ADDRESS, startDate=date_util.datetime_from_now())
    print(s)
    await database.disconnect()

async def run_async_mdtp():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester, lockManger = LockManager(retriever=retriever, saver=saver))

    await database.connect()
    m = await tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_MDTP_ADDRESS, startDate=date_util.datetime_from_now())
    print(m)
    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(run_async_goblin())
    asyncio.run(run_async_sprite())
    asyncio.run(run_async_mdtp())
