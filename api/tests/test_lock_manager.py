import asyncio
import logging
import os
import sys
import unittest

from unittest import IsolatedAsyncioTestCase

from core import logging
from core.exceptions import NotFoundException
from core.store.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.lock_manager import LockManager
from notd.lock_manager import LockTimeoutException
from notd.store.retriever import Retriever
from notd.store.saver import Saver

openseaApiKey = os.environ['OPENSEA_API_KEY']

class KibaAsyncTestCase(IsolatedAsyncioTestCase):

    def __init__(self, methodName: str = 'runTest') -> None:
        super().__init__(methodName=methodName)


class LockManagerTestCase(KibaAsyncTestCase):

    async def asyncSetUp(self) -> None:
        databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
        self.database = Database(connectionString=databaseConnectionString)
        self.saver = Saver(database=self.database)
        self.retriever = Retriever(database=self.database)
        self.lockManager = LockManager(retriever=self.retriever, saver=self.saver)
        await self.database.connect()

    async def asyncTearDown(self) -> None:
        await self.database.disconnect()
        await super().asyncTearDown()


class TestLockExpiry(LockManagerTestCase):

    async def test_expiry(self):
        pass


class TestWithLock(LockManagerTestCase):

    async def test_current_lock_releases_before_new_one_acquired (self):
        pass


class TestLockTimeout(LockManagerTestCase):

    async def test_lock_will_timeout(self):
        with self.assertRaises(LockTimeoutException) as lockTimeOut:
            await asyncio.gather(
                self.lockManager.acquire_lock(name='testing', timeoutSeconds=1, expirySeconds=1),
                self.lockManager.acquire_lock(name='testing', timeoutSeconds=0.1, expirySeconds=1)
            )



class TestReleaseLock(LockManagerTestCase):

    async def test_lock_release(self):
        lock = await self.lockManager.acquire_lock(name='testing', timeoutSeconds=2, expirySeconds=1)
        try:
            lock = await self.retriever.get_lock(lockId=lock.lockId)
            await self.saver.delete_lock(lockId=lock.lockId)
        except NotFoundException:
            pass


if __name__ == "__main__":
    unittest.main()
