from core.exceptions import NotFoundException
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.sub_collection_token_processor import SubCollectionTokenProcessor

class SubCollectionTokenManager:

    def __init__(self, retriever: Retriever, saver: Saver, subCollectionTokenProcessor: SubCollectionTokenProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.subCollectionTokenProcessor = subCollectionTokenProcessor

    async def update_sub_collection_token(self,registryAddress: str, tokenId: str) -> None:
        collectionName = await self.subCollectionTokenProcessor.retrieve_collection_name(registryAddress=registryAddress, tokenId=tokenId)
        if collectionName:
            try:
                subCollectionToken = await self.retriever.get_sub_collection_token_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
            except NotFoundException:
                subCollectionToken = None
            if subCollectionToken:
                await self.saver.update_sub_collection_token(subCollectionTokenId=subCollectionToken.subCollectionTokenId, collectionName=collectionName)
            else:
                await self.saver.create_sub_collection_token(registryAddress=registryAddress, tokenId=tokenId, collectionName=collectionName)
