from core.util import date_util
from notd.store.retriever import Retriever
class LockManager:
    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever
        pass
    

    async def acquire_lock(self, name: str, timeoutSeconds: str, expirySeconds: str):
        startDate = date_util.datetime_from_now()

        pass