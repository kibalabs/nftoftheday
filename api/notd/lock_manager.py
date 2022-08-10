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
        lock = None
        try:
            lock = await self.retriever.get_lock_by_name(name=name)
        except NotFoundException:
            pass
        if lock and lock.expiryDate < date_util.datetime_from_now():
            await self.saver.delete_lock(lockId=lock.lockId)
            lock = None
        if not lock:
            return await self.saver.create_lock(name=name, expiryDate=date_util.datetime_from_now(seconds=expirySeconds))
        return None

    async def acquire_lock(self, name: str, timeoutSeconds: int, expirySeconds: int) -> Lock:
        endDate = date_util.datetime_from_now(seconds=timeoutSeconds)
        while date_util.datetime_from_now() < endDate:
            lock = await self._acquire_lock_if_available(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
            if lock:
                return lock
            await asyncio.sleep(0.1)
        raise LockTimeoutException()

    async def release_lock(self, name: str) -> None:
        lock = await self.retriever.get_lock_by_name(name=name)
        await self.saver.delete_lock(lockId=lock.lockId)

    @contextlib.asynccontextmanager
    async def with_lock(self, name: str, timeoutSeconds: int, expirySeconds: int) -> ContextManager[Lock]:
        await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
        try:
            yield
        finally:
            await self.release_lock(name=name)
