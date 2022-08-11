import asyncio
from dataclasses import dataclass
import logging
import os
import sys
from typing import Optional
import unittest

from core import logging
from core.store.database import Database
from core.util.value_holder import RequestIdHolder
from core.exceptions import NotFoundException
from unittest import IsolatedAsyncioTestCase


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.lock_manager import LockManager
from notd.lock_manager import LockTimeoutException
from notd.store.retriever import Retriever
from notd.store.saver import Saver

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

class KibaAsyncTestCase(IsolatedAsyncioTestCase):

    def __init__(self, methodName: str = 'runTest') -> None:
        super().__init__(methodName=methodName)


class LockTestCase(KibaAsyncTestCase):

    async def asyncSetUp(self) -> None:
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
        self.database = Database(connectionString=databaseConnectionString)
        self.saver = Saver(database=self.database)
        self.retriever = Retriever(database=self.database)
        self.lockManager = LockManager(retriever=self.retriever, saver=self.saver)
        await self.database.connect()

    async def asyncTearDown(self) -> None:
        await self.database.disconnect()
        await super().asyncTearDown()

class LockManagerTestCase(LockTestCase):

    # Test for Expiry
    async def test_expiry(self):
        await asyncio.gather(*[test_acquire_function(lockManager=self.lockManager, index=i, timeoutSeconds=5, expirySeconds=1) for i in range(1)])

    # #Test Functions
    async def test_functions(self):
        await asyncio.gather(*[test_function(lockManager=self.lockManager, index=i) for i in range(1)])
        await asyncio.gather(*[test_function(lockManager=self.lockManager, index=i) for i in range(2)])
        await asyncio.gather(*[test_function(lockManager=self.lockManager, index=i) for i in range(3)])

    # Test for Timeout
    async def test_timeout(self):
        try:
            await asyncio.gather(*[test_acquire_function(lockManager=self.lockManager, index=i, timeoutSeconds=1, expirySeconds=1) for i in range(3)])
        except LockTimeoutException:
            logging.info(f"Test for Timeout done")

    # Test Release
    async def test_release(self):
        lock = await self.lockManager.acquire_lock(name='testing', timeoutSeconds=2, expirySeconds=1)
        try:
            lock = await self.retriever.get_lock(lockId=lock.lockId)
            await self.saver.delete_lock(lockId=lock.lockId)
        except NotFoundException:
            pass


if __name__ == "__main__":
    unittest.main()
