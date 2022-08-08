from datetime import datetime
import time
import contextlib
from core.util import date_util
from core.exceptions import NotFoundException

from notd.store.retriever import Retriever
from notd.store.saver import Saver


class LockManager:
    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever = retriever
        self.saver = saver

    async def acquire_lock(self, name: str, timeoutSeconds: int, expirySeconds: int):
        startDate = date_util.datetime_from_now()
        lock = None
        try:
            lock = await self.retriever.get_lock_by_name(name=name)
        except NotFoundException:
            pass
        if lock:
            if datetime.fromtimestamp(lock.expiryTime) < startDate:
                await self.saver.delete_lock(lockId=lock.lockId)
            elif date_util.datetime_from_now() > date_util.datetime_from_datetime(dt=startDate, seconds=timeoutSeconds):
                raise Exception
            else:
                time.sleep(100)
                await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
        else:
            await self.saver.create_lock(name=name, timeoutSeconds=timeoutSeconds, expiryTime= datetime.timestamp(date_util.datetime_from_now())+expirySeconds)

    async def release_lock(self, name: str):
        try:
            lock = await self.retriever.get_lock_by_name(name=name)
        except NotFoundException:
            lock = None
        if lock:
            await self.saver.delete_lock(lockId=lock.lockId)

    @contextlib.asynccontextmanager
    async def with_lock(self, name: str, timeoutSeconds: int, expirySeconds: int):
        await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
        try:
            yield
        finally:
            await self.release_lock(name=name)
