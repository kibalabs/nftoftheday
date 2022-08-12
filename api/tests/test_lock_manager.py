import asyncio
import logging
import os
import sys
import unittest
from unittest import IsolatedAsyncioTestCase

from core.exceptions import NotFoundException
from core.store.database import Database

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.lock_manager import LockManager
from notd.lock_manager import LockTimeoutException
from notd.store.retriever import Retriever
from notd.store.saver import Saver


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


class TestAcquireLock(LockManagerTestCase):

    async def test_acquire_lock(self):
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)

    async def test_acquire_different_locks(self):
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)
        lock2 = await self.lockManager.acquire_lock(name='test2', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock2, None)

    async def test_lock_expires_in_time(self):
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)
        await asyncio.sleep(0.01)
        lock2 = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock2, None)
        await self.lockManager.release_lock(lock=lock2)

    async def test_lock_expires_even_if_unreleased(self):
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)
        await asyncio.sleep(0.011)
        lock2 = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock2, None)
        await self.lockManager.release_lock(lock=lock2)

    async def test_acquire_waits_for_timeout_if_lock_taken(self):
        await self.lockManager.acquire_lock(name='test', expirySeconds=0.5, timeoutSeconds=0, loopDelaySeconds=0.001)
        await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0.51, loopDelaySeconds=0.001)

    async def test_timeout_exception_raised_if_lock_taken(self):
        await self.lockManager.acquire_lock(name='test', expirySeconds=0.5, timeoutSeconds=0, loopDelaySeconds=0.001)
        with self.assertRaises(LockTimeoutException):
            await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0.0001, loopDelaySeconds=0.001)
        await asyncio.sleep(0.5)


class TestReleaseLock(LockManagerTestCase):

    async def test_lock_release(self):
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)
        await self.lockManager.release_lock(lock=lock)

    async def test_lock_release_fails_if_lost(self):
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)
        lock2 = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=1, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)
        with self.assertRaises(NotFoundException):
            await self.lockManager.release_lock(lock=lock)
        await self.lockManager.release_lock(lock=lock2)


class TestWithLock(LockManagerTestCase):

    async def test_acquire_lock(self):
        async with self.lockManager.with_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001):
            await asyncio.sleep(0.01)

    async def test_acquire_and_release_lock(self):
        async with self.lockManager.with_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001):
            await asyncio.sleep(0.01)
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)

    async def test_acquire_different_locks(self):
        async with self.lockManager.with_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001):
            async with self.lockManager.with_lock(name='test2', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001):
                await asyncio.sleep(0.01)
            lock = await self.lockManager.acquire_lock(name='test2', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
            self.assertNotEqual(lock, None)
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)

    async def test_lock_expires_in_time(self):
        async with self.lockManager.with_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001):
            await asyncio.sleep(0.02)
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)

    async def test_lock_expires_even_if_unreleased(self):
        async with self.lockManager.with_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001):
            await asyncio.sleep(0.001)
        lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
        self.assertNotEqual(lock, None)

    async def test_acquire_waits_for_timeout_if_lock_taken(self):
        async with self.lockManager.with_lock(name='test', expirySeconds=0.5, timeoutSeconds=0, loopDelaySeconds=0.001):
            await asyncio.sleep(0.001)
            with self.assertRaises(LockTimeoutException):
                lock = await self.lockManager.acquire_lock(name='test', expirySeconds=0.01, timeoutSeconds=0, loopDelaySeconds=0.001)
                self.assertNotEqual(lock, None)

    async def test_timeout_exception_raised_if_lock_taken(self):
        async with self.lockManager.with_lock(name='test', expirySeconds=0.5, timeoutSeconds=0, loopDelaySeconds=0.001):
            await asyncio.sleep(0.001)
            with self.assertRaises(LockTimeoutException):
                async with self.lockManager.with_lock(name='test', expirySeconds=0.001, timeoutSeconds=0, loopDelaySeconds=0.001):
                    await asyncio.sleep(0.01)



if __name__ == "__main__":
    unittest.main()
