from core.exceptions import NotFoundException
from core.util import chain_util

from notd.model import SUB_COLLECTION_PARENT_ADDRESSES
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.sub_collection_token_processor import SubCollectionTokenProcessor


class SubCollectionTokenManager:

    def __init__(self, retriever: Retriever, saver: Saver, subCollectionTokenProcessor: SubCollectionTokenProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.subCollectionTokenProcessor = subCollectionTokenProcessor

    async def has_sub_collections(self, registryAddress: str) -> bool:
        return registryAddress in SUB_COLLECTION_PARENT_ADDRESSES

    async def update_sub_collection_token(self, registryAddress: str, tokenId: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        hasSubCollections = await self.has_sub_collections(registryAddress=registryAddress)
        if not hasSubCollections:
            return
        collectionName = await self.subCollectionTokenProcessor.retrieve_sub_collection_name(registryAddress=registryAddress, tokenId=tokenId)
        if collectionName:
            try:
                subCollectionToken = await self.retriever.get_sub_collection_token_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
            except NotFoundException:
                subCollectionToken = None
            if subCollectionToken:
                await self.saver.update_sub_collection_token(subCollectionTokenId=subCollectionToken.subCollectionTokenId, collectionName=collectionName)
            else:
                await self.saver.create_sub_collection_token(registryAddress=registryAddress, tokenId=tokenId, collectionName=collectionName)
