from core.exceptions import NotFoundException
from notd.model import SubCollection

class SubCollectionDoesNotExist(NotFoundException):
    pass

class SubCollectionProcessor:

    def __init__(self) -> None:
        pass

    async def retrieve_sub_collection(self, collectionName: str) -> SubCollection:
        pass
