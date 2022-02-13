import asyncio
import logging
import random
from typing import List
from typing import Tuple

import sqlalchemy
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import DateFieldFilter
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
_COLLECTION_UPDATE_MIN_DAYS = 30


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
            if not shouldProcessIfNotFound:
                raise
            await asyncio.sleep(sleepSecondsBeforeProcess)
            await self.update_collection(address=address, shouldForce=True)
            collection = await self.retriever.get_collection_by_address(address=address)
        return collection

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str) -> TokenMetadata:
        return await self._get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId, shouldProcessIfNotFound=True)

    async def _get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str, shouldProcessIfNotFound: bool = True, sleepSecondsBeforeProcess: float = 0) -> TokenMetadata:
        try:
            tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        except NotFoundException:
            if not shouldProcessIfNotFound:
                raise
            await asyncio.sleep(sleepSecondsBeforeProcess)
            await self.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=True)
            tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return tokenMetadata

    async def update_token_metadatas_deferred(self, collectionTokenIds: List[Tuple[str, str]], shouldForce: bool = False) -> None:
        if len(collectionTokenIds) == 0:
            return
        if not shouldForce:
            tokenStatements = []
            for (registryAddress, tokenId) in collectionTokenIds:
                tokenStatements.append(sqlalchemy.and_(TokenMetadataTable.c.registryAddress == registryAddress, TokenMetadataTable.c.tokenId == tokenId))
            # TODO(krishan711): this should be able to us in_ as shown below but it doesn't work (probably something in encode/databases)
            query = (
                TokenMetadataTable.select()
                    .where(TokenMetadataTable.c.updatedDate > date_util.datetime_from_now(days=-_COLLECTION_UPDATE_MIN_DAYS))
                    # .where(sqlalchemy.tuple_(TokenMetadataTable.c.registryAddress, TokenMetadataTable.c.tokenId).in_(collectionTokenIds))
                    .where(sqlalchemy.or_(*tokenStatements))
            )
            recentlyUpdatedTokenMetadatas = await self.retriever.query_token_metadatas(query=query)
            recentlyUpdatedTokenIds = set((tokenMetadata.registryAddress, tokenMetadata.tokenId) for tokenMetadata in recentlyUpdatedTokenMetadatas)
            logging.info(f'Skipping {len(recentlyUpdatedTokenIds)} collectionTokenIds because they have been updated recently.')
            collectionTokenIds = set(collectionTokenIds) - recentlyUpdatedTokenIds
        messages = [UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message() for (registryAddress, tokenId) in collectionTokenIds]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        if not shouldForce:
            recentlyUpdatedTokens = await self.retriever.list_token_metadatas(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenMetadataTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=TokenMetadataTable.c.tokenId.key, eq=tokenId),
                    DateFieldFilter(fieldName=TokenMetadataTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_TOKEN_UPDATE_MIN_DAYS))
                ],
            )
            if len(recentlyUpdatedTokens) > 0:
                logging.info('Skipping token because it has been updated recently.')
                return
        await self.tokenQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        if not shouldForce:
            print('update_token_metadata', registryAddress, tokenId, 1)
            recentlyUpdatedTokens = await self.retriever.list_token_metadatas(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenMetadataTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=TokenMetadataTable.c.tokenId.key, eq=tokenId),
                    DateFieldFilter(fieldName=TokenMetadataTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_TOKEN_UPDATE_MIN_DAYS))
                ],
            )
            print('update_token_metadata', registryAddress, tokenId, 2)
            if len(recentlyUpdatedTokens) > 0:
                logging.info('Skipping token because it has been updated recently.')
                return
        print('update_token_metadata', registryAddress, tokenId, 3)
        collection = await self._get_collection_by_address(address=registryAddress, shouldProcessIfNotFound=True, sleepSecondsBeforeProcess=0.1 * random.randint(1, 10))
        print('update_token_metadata', registryAddress, tokenId, 4)
        try:
            retrievedTokenMetadata = await self.tokenMetadataProcessor.retrieve_token_metadata(registryAddress=registryAddress, tokenId=tokenId, collection=collection)
        except (TokenDoesNotExistException, TokenHasNoMetadataException):
            logging.info(f'Failed to retrieve metadata for token: {registryAddress}: {tokenId}')
            retrievedTokenMetadata = TokenMetadataProcessor.get_default_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
        print('update_token_metadata', registryAddress, tokenId, 5)
        async with self.saver.create_transaction():
            print('update_token_metadata', registryAddress, tokenId, 6)
            try:
                tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
            except NotFoundException:
                tokenMetadata = None
            if tokenMetadata:
                print('update_token_metadata', registryAddress, tokenId, 8)
                await self.saver.update_token_metadata(tokenMetadataId=tokenMetadata.tokenMetadataId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)
            else:
                print('update_token_metadata', registryAddress, tokenId, 9)
                await self.saver.create_token_metadata(registryAddress=registryAddress, tokenId=tokenId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)
            print('update_token_metadata', registryAddress, tokenId, 10)

    async def update_collections_deferred(self, addresses: List[str], shouldForce: bool = False) -> None:
        if len(addresses) == 0:
            return
        if not shouldForce:
            recentlyUpdatedCollections = await self.retriever.list_collections(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, containedIn=addresses),
                    DateFieldFilter(fieldName=TokenCollectionsTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_COLLECTION_UPDATE_MIN_DAYS))
                ],
            )
            recentlyUpdatedAddresses = set(collection.address for collection in recentlyUpdatedCollections)
            logging.info(f'Skipping {len(recentlyUpdatedAddresses)} collections because they have been updated recently.')
            addresses = set(addresses) - recentlyUpdatedAddresses
        messages = [UpdateCollectionMessageContent(address=address).to_message() for address in addresses]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_collection_deferred(self, address: str, shouldForce: bool = False) -> None:
        if not shouldForce:
            recentlyUpdatedCollections = await self.retriever.list_collections(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, eq=address),
                    DateFieldFilter(fieldName=TokenCollectionsTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_COLLECTION_UPDATE_MIN_DAYS))
                ],
            )
            if len(recentlyUpdatedCollections) > 0:
                logging.info('Skipping collection because it has been updated recently.')
                return
        await self.tokenQueue.send_message(message=UpdateCollectionMessageContent(address=address).to_message())

    async def update_collection(self, address: str, shouldForce: bool = False) -> None:
        if not shouldForce:
            recentlyUpdatedCollections = await self.retriever.list_collections(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, eq=address),
                    DateFieldFilter(fieldName=TokenCollectionsTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_COLLECTION_UPDATE_MIN_DAYS))
                ],
            )
            if len(recentlyUpdatedCollections) > 0:
                logging.info('Skipping collection because it has been updated recently.')
                return
        try:
            retrievedCollection = await self.collectionProcessor.retrieve_collection(address=address)
        except CollectionDoesNotExist:
            logging.info(f'Failed to retrieve non-existant collection: {address}')
            return
        async with self.saver.create_transaction():
            try:
                collection = await self.retriever.get_collection_by_address(address=address)
            except NotFoundException:
                collection = None
            if collection:
                await self.saver.update_collection(collectionId=collection.collectionId, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl, doesSupportErc721=retrievedCollection.doesSupportErc721, doesSupportErc1155=retrievedCollection.doesSupportErc1155)
            else:
                await self.saver.create_collection(address=address, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl, doesSupportErc721=retrievedCollection.doesSupportErc721, doesSupportErc1155=retrievedCollection.doesSupportErc1155)
