from notd.store.retriever import Retriever
from notd.store.saver import Saver


class SubCollectionManager:

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever = retriever
        self.saver = saver

    async def update_sub_collection_deferred(self, collectionName: str) -> None:
        pass

    async def update_sub_collection(self, collectionName: str) -> None:
        pass
