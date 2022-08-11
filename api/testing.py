import asyncio
import logging
import os

from core import logging
from core.requester import Requester
from core.store.database import Database
from core.util import date_util

from notd.lock_manager import LockManager
from notd.model import COLLECTION_MDTP_ADDRESS, COLLECTION_SPRITE_CLUB_ADDRESS, COLLECTION_GOBLINTOWN_ADDRESS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.token_listing_processor import TokenListingProcessor
from core.util.value_holder import RequestIdHolder

openseaApiKey = os.environ['OPENSEA_API_KEY']

async def test_function(lockManager: LockManager, index: int):
    async with lockManager.with_lock(name='testing', timeoutSeconds=3, expirySeconds=1):
        print(f'{index} got lock')
        for i in range(20):
            await asyncio.sleep(0.1)


async def run_async_opensea():
    requestIdHolder = RequestIdHolder()
    name = os.environ.get('NAME', 'notd-api')
    version = os.environ.get('VERSION', 'local')
    environment = os.environ.get('ENV', 'dev')
    isRunningDebugMode = environment == 'dev'

    if isRunningDebugMode:
        logging.init_basic_logging()
    else:
        logging.init_json_logging(name=name, version=version, environment=environment, requestIdHolder=requestIdHolder)

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
    async with lockManager.with_lock(name='test-opensea', timeoutSeconds=1, expirySeconds=1):
        await asyncio.sleep(0.5)

    # Test for Expiry
    async with lockManager.with_lock(name='test-opensea', timeoutSeconds=0.1, expirySeconds=1):
        await asyncio.sleep(0.5)

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

    await asyncio.gather(*[test_function(lockManager=lockManager, index=i) for i in range(3)])

    await database.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_async_opensea())
