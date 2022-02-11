import asyncio
import logging
import random

import async_lru
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.collection_processor import CollectionDoesNotExist
from notd.collection_processor import CollectionProcessor
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.model import Collection
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadataTable
from notd.token_metadata_processor import TokenDoesNotExistException
from notd.token_metadata_processor import TokenHasNoMetadataException
from notd.token_metadata_processor import TokenMetadataProcessor

_TOKEN_UPDATE_MIN_DAYS = 30
_COLLECTION_UPDATE_MIN_DAYS = 90


class TokenManager:

    def __init__(self, saver: Saver, retriever: Retriever, tokenQueue: SqsMessageQueue, collectionProcessor: CollectionProcessor, tokenMetadataProcessor: TokenMetadataProcessor):
        self.saver = saver
        self.retriever = retriever
        self.tokenQueue = tokenQueue
        self.collectionProcessor = collectionProcessor
        self.tokenMetadataProcessor = tokenMetadataProcessor

    async def get_collection_by_address(self, address: str) -> Collection:
        return await self._get_collection_by_address(address=address, shouldProcessIfNotFound=True)

    async def _get_collection_by_address(self, address: str, shouldProcessIfNotFound: bool = True, sleepSecondsBeforeProcess: float = 0) -> Collection:
        try:
            collection = await self.retriever.get_collection_by_address(address=address)
        except NotFoundException:
            if shouldProcessIfNotFound:
                await asyncio.sleep(sleepSecondsBeforeProcess)
                await self.update_collection(address=address, shouldForce=True)
            else:
                raise
            collection = await self.retriever.get_collection_by_address(address=address)
        return collection

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str) -> TokenMetadata:
        return await self._get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId, shouldProcessIfNotFound=True)

    async def _get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str, shouldProcessIfNotFound: bool = True, sleepSecondsBeforeProcess: float = 0) -> TokenMetadata:
        try:
            tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        except NotFoundException:
            if shouldProcessIfNotFound:
                await asyncio.sleep(sleepSecondsBeforeProcess)
                await self.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=True)
            else:
                raise
            tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return tokenMetadata

    @async_lru.alru_cache(maxsize=100000)
    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        savedTokenMetadatas = await self.retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenMetadataTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenMetadataTable.c.tokenId.key, eq=tokenId),
            ], limit=1,
        )
        savedTokenMetadata = savedTokenMetadatas[0] if len(savedTokenMetadatas) > 0 else None
        if not shouldForce and savedTokenMetadata and savedTokenMetadata.updatedDate >= date_util.datetime_from_now(days=-3):
            logging.info('Skipping token because it has been updated recently.')
            return
        await self.tokenQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        savedTokenMetadatas = await self.retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenMetadataTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenMetadataTable.c.tokenId.key, eq=tokenId),
            ], limit=1,
        )
        savedTokenMetadata = savedTokenMetadatas[0] if len(savedTokenMetadatas) > 0 else None
        if not shouldForce and savedTokenMetadata and savedTokenMetadata.updatedDate >= date_util.datetime_from_now(days=-_TOKEN_UPDATE_MIN_DAYS):
            logging.info('Skipping token because it has been updated recently.')
            return
        collection = await self._get_collection_by_address(address=registryAddress, shouldProcessIfNotFound=True, sleepSecondsBeforeProcess=0.1 * random.randint(1, 10))
        try:
            retrievedTokenMetadata = await self.tokenMetadataProcessor.retrieve_token_metadata(registryAddress=registryAddress, tokenId=tokenId, collection=collection)
        except TokenDoesNotExistException:
            logging.info(f'Failed to retrieve non-existant token: {registryAddress}: {tokenId}')
            retrievedTokenMetadata = TokenMetadataProcessor.get_default_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
        except TokenHasNoMetadataException:
            logging.info(f'Failed to retrieve metadata for token: {registryAddress}: {tokenId}')
            retrievedTokenMetadata = TokenMetadataProcessor.get_default_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
        if savedTokenMetadata:
            await self.saver.update_token_metadata(tokenMetadataId=savedTokenMetadata.tokenMetadataId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)
        else:
            await self.saver.create_token_metadata(registryAddress=registryAddress, tokenId=tokenId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)

    @async_lru.alru_cache(maxsize=10000)
    async def update_collection_deferred(self, address: str, shouldForce: bool = False) -> None:
        collections = await self.retriever.list_collections(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, eq=address),
            ], limit=1,
        )
        collection = collections[0] if len(collections) > 0 else None
        if not shouldForce and collection and collection.updatedDate >= date_util.datetime_from_now(days=-_COLLECTION_UPDATE_MIN_DAYS):
            logging.info('Skipping collection because it has been updated recently.')
            return
        await self.tokenQueue.send_message(message=UpdateCollectionMessageContent(address=address).to_message())

    async def update_collection(self, address: str, shouldForce: bool = False) -> None:
        collections = await self.retriever.list_collections(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, eq=address),
            ], limit=1,
        )
        collection = collections[0] if len(collections) > 0 else None
        if not shouldForce and collection and collection.updatedDate >= date_util.datetime_from_now(days=-7):
            logging.info('Skipping collection because it has been updated recently.')
            return
        try:
            retrievedCollection = await self.collectionProcessor.retrieve_collection(address=address)
        except CollectionDoesNotExist:
            logging.info(f'Failed to retrieve non-existant collection: {address}')
            return
        if collection:
            await self.saver.update_collection(collectionId=collection.collectionId, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl, doesSupportErc721=retrievedCollection.doesSupportErc721, doesSupportErc1155=retrievedCollection.doesSupportErc1155)
        else:
            await self.saver.create_collection(address=address, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl, doesSupportErc721=retrievedCollection.doesSupportErc721, doesSupportErc1155=retrievedCollection.doesSupportErc1155)
