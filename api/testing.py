import asyncio
import logging
import os
from typing import Optional

from core import logging
from core.store.database import Database
from notd.lock_manager import LockTimeoutException

from notd.lock_manager import LockManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from core.util.value_holder import RequestIdHolder

openseaApiKey = os.environ['OPENSEA_API_KEY']

async def test_function(lockManager: LockManager, index: int):
    async with lockManager.with_lock(name='testing', timeoutSeconds=3, expirySeconds=1):
        print(f'{index} got lock')
        for i in range(20):
            await asyncio.sleep(0.1)

async def test_acquire_function(lockManager: LockManager, index: int, timeoutSeconds: Optional[int] = 6, expirySeconds: Optional[int] = 1 ):
    print(f'{index} trying to acquire lock')
    await lockManager.acquire_lock(name='testing', timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
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
    lockManager = LockManager(retriever=retriever, saver=saver)

    await database.connect()

    # Test for Expiry
    await asyncio.gather(*[test_acquire_function(lockManager=lockManager, index=i, timeoutSeconds=5, expirySeconds=1) for i in range(1)])
    
    # # Test Release
    lock = await retriever.get_lock_by_name(name='testing')
    await lockManager.release_lock(lock=lock)

    # #Test Functions
    await asyncio.gather(*[test_function(lockManager=lockManager, index=i) for i in range(1)])
    await asyncio.gather(*[test_function(lockManager=lockManager, index=i) for i in range(2)])
    await asyncio.gather(*[test_function(lockManager=lockManager, index=i) for i in range(3)])

    # Test for Timeout
    try:
        await asyncio.gather(*[test_acquire_function(lockManager=lockManager, index=i, timeoutSeconds=1, expirySeconds=1) for i in range(3)])
    except LockTimeoutException:
        logging.info(f"Test for Timeout done")

    await database.disconnect()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_async_opensea())
