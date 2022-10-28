import asyncio
import contextlib
from typing import AsyncIterator
from typing import Optional

from core.exceptions import KibaException
from core.exceptions import NotFoundException
from core.store.saver import SavingException
from core.util import date_util

from notd.model import Lock
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class LockTimeoutException(KibaException):

    def __init__(self, message: Optional[str] = None) -> None:
        message = message if message else 'Lock Timeout'
        super().__init__(message=message)



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
            try:
                return await self.saver.create_lock(name=name, expiryDate=date_util.datetime_from_now(seconds=expirySeconds))
            except SavingException:
                pass
        return None

    async def acquire_lock(self, name: str, timeoutSeconds: int, expirySeconds: int, loopDelaySeconds: float = 0.05) -> Lock:
        currentDate = date_util.datetime_from_now()
        endDate = date_util.datetime_from_now(seconds=timeoutSeconds)
        while currentDate < endDate:
            lock = await self._acquire_lock_if_available(name=name, expirySeconds=expirySeconds)
            if lock:
                return lock
            await asyncio.sleep(loopDelaySeconds)
            currentDate = date_util.datetime_from_now()
        raise LockTimeoutException(f'Failed to acquire lock:{name} after waiting:{timeoutSeconds}s')

    async def release_lock(self, lock: Lock) -> None:
        lock = await self.retriever.get_lock(lockId=lock.lockId)
        await self.saver.delete_lock(lockId=lock.lockId)

    @contextlib.asynccontextmanager
    async def with_lock(self, name: str, timeoutSeconds: int, expirySeconds: int, loopDelaySeconds: float = 0.05) -> AsyncIterator[Lock]:
        lock = await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds, loopDelaySeconds=loopDelaySeconds)
        try:
            yield lock
        finally:
            await self.release_lock(lock=lock)
