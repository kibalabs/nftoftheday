import asyncio
import contextlib
from typing import ContextManager, Optional

from core.exceptions import NotFoundException
from core.util import date_util

from notd.model import Lock
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class LockTimeoutException(BaseException):
    pass

class LockManager:
    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever = retriever
        self.saver = saver

    async def _acquire_lock_if_available(self, name: str, expirySeconds: int) -> Optional[Lock]:
        async with self.saver.create_transaction() as connection:
            lock = None
            try:
                lock = await self.retriever.get_lock_by_name(name=name, connection=connection)
            except NotFoundException:
                pass
            if lock and lock.expiryDate < date_util.datetime_from_now():
                await self.saver.delete_lock(lockId=lock.lockId, connection=connection)
                lock = None
            if not lock:
                return await self.saver.create_lock(name=name, expiryDate=date_util.datetime_from_now(seconds=expirySeconds), connection=connection)
        return None

    async def acquire_lock(self, name: str, timeoutSeconds: int, expirySeconds: int) -> Lock:
        endDate = date_util.datetime_from_now(seconds=timeoutSeconds)
        while date_util.datetime_from_now() < endDate:
            lock = await self._acquire_lock_if_available(name=name, expirySeconds=expirySeconds)
            if lock:
                return lock
            await asyncio.sleep(0.1)
        raise LockTimeoutException()

    async def release_lock(self, lock: Lock) -> None:
        try:
            lock = await self.retriever.get_lock(lockId=lock.lockId)
            await self.saver.delete_lock(lockId=lock.lockId)
        except NotFoundException:
            pass

    @contextlib.asynccontextmanager
    async def with_lock(self, name: str, timeoutSeconds: int, expirySeconds: int) -> ContextManager[Lock]:
        lock = await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
        try:
            yield
        finally:
            await self.release_lock(lock=lock)
