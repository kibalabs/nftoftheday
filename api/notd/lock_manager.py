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
        lock = await self.retriever.get_lock_by_name(name=name)
        if lock:
            if lock.expiryTime < startDate:
                await self.saver.delete_lock(lockId=lock.lockId)
            elif date_util.datetime_from_now() > startDate + timeoutSeconds:
                raise Exception
            else:
                time.sleep(100)
                self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
        else:
            await self.saver.create_lock(name=name, timeoutSeconds=timeoutSeconds, expiryTime=date_util.datetime_from_now()+expirySeconds)

    async def release_lock(self, name: str):
        lock = await self.retriever.get_lock_by_name(name=name)
        if not lock:
            raise NotFoundException
        await self.saver.delete_lock(lockId=lock.lockId)

    @contextlib.contextmanager
    async def with_lock(self, name: str, timeoutSeconds: int, expirySeconds: int):
        await self.acquire_lock(name=name, timeoutSeconds=timeoutSeconds, expirySeconds=expirySeconds)
        try:
            yield
        finally:
            await self.release_lock(name=name)
