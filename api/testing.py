import asyncio
import logging
import os

from core.requester import Requester
from core.store.database import Database
from core.util import date_util
from api.notd.model import COLLECTION_MDTP_ADDRESS, COLLECTION_SPRITE_CLUB_ADDRESS

from notd.lock_manager import LockManager
from notd.model import COLLECTION_GOBLINTOWN_ADDRESS
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_listing_processor import TokenListingProcessor

openseaApiKey = os.environ['OPENSEA_API_KEY']

async def run_async_opensea():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    lockManager = LockManager(retriever=retriever, saver=saver)
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester, lockManager = LockManager(retriever=retriever, saver=saver))

    await database.connect()

    # Test for Timeout
    async with lockManager.with_lock(name='test-opensea', timeoutSeconds=10, expirySeconds=1):
        await asyncio.sleep(20)

    # Test for Expiry
    async with lockManager.with_lock(name='test-opensea', timeoutSeconds=10, expirySeconds=1):
        await asyncio.sleep(1)

    #Test for One function at a time
    async with lockManager.with_lock(name='test-opensea', timeoutSeconds=3*10, expirySeconds=10*60):
        await tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_GOBLINTOWN_ADDRESS, startDate=date_util.start_of_day())

    #Test for Two functions at a time
    async with lockManager.with_lock(name='test-opensea', timeoutSeconds=3*10, expirySeconds=10*60):
        await asyncio.gather(
            tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_GOBLINTOWN_ADDRESS, startDate=date_util.start_of_day()),
            tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_SPRITE_CLUB_ADDRESS, startDate=date_util.start_of_day()),
        )

    #Test for Three functions at a time
    # await asyncio.gather(*[tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=address, startDate=date_util.datetime_from_now()) for address in GALLERY_COLLECTIONS])
    async with lockManager.with_lock(name='test-opensea', timeoutSeconds=3*10, expirySeconds=10*60):
        await asyncio.gather(
            tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_GOBLINTOWN_ADDRESS, startDate=date_util.start_of_day()),
            tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_SPRITE_CLUB_ADDRESS, startDate=date_util.start_of_day()),
            tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=COLLECTION_MDTP_ADDRESS, startDate=date_util.start_of_day()),
        )

    #Test Acquire Lock
    await asyncio.gather(
        lockManager.acquire_lock(name='test-opensea', timeoutSeconds=10, expirySeconds=10),
        lockManager.acquire_lock(name='test-opensea', timeoutSeconds=10, expirySeconds=10),
    )

    #Test Acquire Lock if Available
    lock = await lockManager.acquire_lock(name='test-opensea', timeoutSeconds=10, expirySeconds=(10 * 60))
    print(lock)
    lock1 = await lockManager._acquire_lock_if_available(name='test-opensea', expirySeconds=10)
    print(lock1)
    

    await database.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_async_opensea())
