import asyncio
import contextlib
from typing import ContextManager

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

    async def acquire_lock(self, name: str, timeoutSeconds: int, expirySeconds: int) -> Lock:
        startDate = date_util.datetime_from_now()
        lock = None
        try:
            lock = await self.retriever.get_lock_by_name(name=name)
        except NotFoundException:
            pass
        if lock:
            if lock.expiryDate < startDate:
                await self.saver.delete_lock(lockId=lock.lockId)
            elif date_util.datetime_from_now() > date_util.datetime_from_datetime(dt=startDate, seconds=timeoutSeconds):
                raise LockTimeoutException
            else:
                await asyncio.sleep(1)
                await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
        else:
            await self.saver.create_lock(name=name, expiryDate= date_util.datetime_from_now(seconds=expirySeconds))
        return lock

    async def release_lock(self, name: str) -> None:
        try:
            lock = await self.retriever.get_lock_by_name(name=name)
        except NotFoundException:
            lock = None
        if lock:
            await self.saver.delete_lock(lockId=lock.lockId)

    @contextlib.asynccontextmanager
    async def with_lock(self, name: str, timeoutSeconds: int, expirySeconds: int) -> ContextManager[Lock]:
        try:
            await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
            yield
        finally:
            await self.release_lock(name=name)
