import asyncio
import datetime
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
from notd.messages import UpdateCollectionTokensMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.messages import UpdateTokenOwnershipMessageContent
from notd.model import Collection
from notd.model import RetrievedTokenMetadata
from notd.model import RetrievedTokenMultiOwnership
from notd.model import Token
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.token_metadata_processor import TokenDoesNotExistException
from notd.token_metadata_processor import TokenHasNoMetadataException
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor

_TOKEN_UPDATE_MIN_DAYS = 10
_COLLECTION_UPDATE_MIN_DAYS = 30


class TokenManager:

    def __init__(self, saver: Saver, retriever: Retriever, tokenQueue: SqsMessageQueue, collectionProcessor: CollectionProcessor, tokenMetadataProcessor: TokenMetadataProcessor, tokenOwnershipProcessor: TokenOwnershipProcessor):
        self.saver = saver
        self.retriever = retriever
        self.tokenQueue = tokenQueue
        self.collectionProcessor = collectionProcessor
        self.tokenMetadataProcessor = tokenMetadataProcessor
        self.tokenOwnershipProcessor = tokenOwnershipProcessor

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
            query = (
                TokenMetadataTable.select()
                    .where(TokenMetadataTable.c.updatedDate > date_util.datetime_from_now(days=-_COLLECTION_UPDATE_MIN_DAYS))
                    .where(sqlalchemy.tuple_(TokenMetadataTable.c.registryAddress, TokenMetadataTable.c.tokenId).in_(collectionTokenIds))
            )
            recentlyUpdatedTokenMetadatas = await self.retriever.query_token_metadatas(query=query)
            recentlyUpdatedTokenIds = set((tokenMetadata.registryAddress, tokenMetadata.tokenId) for tokenMetadata in recentlyUpdatedTokenMetadatas)
            logging.info(f'Skipping {len(recentlyUpdatedTokenIds)} collectionTokenIds because they have been updated recently.')
            collectionTokenIds = set(collectionTokenIds) - recentlyUpdatedTokenIds
        messages = [UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce).to_message() for (registryAddress, tokenId) in collectionTokenIds]
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
        collection = await self._get_collection_by_address(address=registryAddress, shouldProcessIfNotFound=True, sleepSecondsBeforeProcess=0.1 * random.randint(1, 10))
        try:
            retrievedTokenMetadata = await self.tokenMetadataProcessor.retrieve_token_metadata(registryAddress=registryAddress, tokenId=tokenId, collection=collection)
        except (TokenDoesNotExistException, TokenHasNoMetadataException):
            logging.info(f'Failed to retrieve metadata for token: {registryAddress}: {tokenId}')
            retrievedTokenMetadata = TokenMetadataProcessor.get_default_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
        await self.save_token_metadata(retrievedTokenMetadata=retrievedTokenMetadata)

    async def save_token_metadata(self, retrievedTokenMetadata: RetrievedTokenMetadata):
        async with self.saver.create_transaction() as connection:
            try:
                tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(connection=connection, registryAddress=retrievedTokenMetadata.registryAddress, tokenId=retrievedTokenMetadata.tokenId)
            except NotFoundException:
                tokenMetadata = None
            if tokenMetadata:
                await self.saver.update_token_metadata(connection=connection, tokenMetadataId=tokenMetadata.tokenMetadataId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)
            else:
                await self.saver.create_token_metadata(connection=connection, registryAddress=retrievedTokenMetadata.registryAddress, tokenId=retrievedTokenMetadata.tokenId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)

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
        async with self.saver.create_transaction() as connection:
            try:
                collection = await self.retriever.get_collection_by_address(connection=connection, address=address)
            except NotFoundException:
                collection = None
            if collection:
                await self.saver.update_collection(connection=connection, collectionId=collection.collectionId, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl, doesSupportErc721=retrievedCollection.doesSupportErc721, doesSupportErc1155=retrievedCollection.doesSupportErc1155)
            else:
                await self.saver.create_collection(connection=connection, address=address, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl, doesSupportErc721=retrievedCollection.doesSupportErc721, doesSupportErc1155=retrievedCollection.doesSupportErc1155)

    async def update_collection_tokens(self, address: str, shouldForce: bool = False) -> None:
        collectionTokenIds = await self.retriever.list_tokens_by_collection(address=address)
        await self.update_collection_deferred(address=address, shouldForce=shouldForce)
        await self.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds, shouldForce=shouldForce)

    async def update_collection_tokens_deferred(self, address: str, shouldForce: bool = False):
        await self.tokenQueue.send_message(message=UpdateCollectionTokensMessageContent(address=address, shouldForce=shouldForce).to_message())

    async def update_token_ownerships_deferred(self, collectionTokenIds: List[Tuple[str, str]]) -> None:
        if len(collectionTokenIds) == 0:
            return
        collectionTokenIds = set(collectionTokenIds)
        messages = [UpdateTokenOwnershipMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message() for (registryAddress, tokenId) in collectionTokenIds]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_token_ownership_deferred(self, registryAddress: str, tokenId: str) -> None:
        await self.tokenQueue.send_message(message=UpdateTokenOwnershipMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_token_ownership(self, registryAddress: str, tokenId: str):
        collection = await self.get_collection_by_address(address=registryAddress)
        if collection.doesSupportErc721:
            await self._update_token_single_ownership(registryAddress=registryAddress, tokenId=tokenId)
        elif collection.doesSupportErc1155:
            await self._update_token_multi_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def _update_token_single_ownership(self, registryAddress: str, tokenId: str) -> None:
        async with self.saver.create_transaction() as connection:
            try:
                tokenOwnership = await self.retriever.get_token_ownership_by_registry_address_token_id(connection=connection, registryAddress=registryAddress, tokenId=tokenId)
            except NotFoundException:
                tokenOwnership = None
            retrievedTokenOwnership = await self.tokenOwnershipProcessor.calculate_token_single_ownership(registryAddress=registryAddress, tokenId=tokenId)
            if tokenOwnership:
                await self.saver.update_token_ownership(connection=connection, tokenOwnershipId=tokenOwnership.tokenOwnershipId, ownerAddress=retrievedTokenOwnership.ownerAddress, transferDate=retrievedTokenOwnership.transferDate, transferValue=retrievedTokenOwnership.transferValue, transferTransactionHash=retrievedTokenOwnership.transferTransactionHash)
            else:
                await self.saver.create_token_ownership(connection=connection, registryAddress=retrievedTokenOwnership.registryAddress, tokenId=retrievedTokenOwnership.tokenId, ownerAddress=retrievedTokenOwnership.ownerAddress, transferDate=retrievedTokenOwnership.transferDate, transferValue=retrievedTokenOwnership.transferValue, transferTransactionHash=retrievedTokenOwnership.transferTransactionHash)

    @staticmethod
    def _uniqueness_tuple_from_token_multi_ownership(retrievedTokenMultiOwnership: RetrievedTokenMultiOwnership) -> Tuple[str, str, str, int, int, datetime.datetime, str]:
        return (retrievedTokenMultiOwnership.registryAddress, retrievedTokenMultiOwnership.tokenId, retrievedTokenMultiOwnership.ownerAddress, retrievedTokenMultiOwnership.quantity, retrievedTokenMultiOwnership.averageTransferValue, retrievedTokenMultiOwnership.latestTransferDate, retrievedTokenMultiOwnership.latestTransferTransactionHash)

    async def _update_token_multi_ownership(self, registryAddress: str, tokenId: str) -> None:
        retrievedTokenMultiOwnerships = await self.tokenOwnershipProcessor.calculate_token_multi_ownership(registryAddress=registryAddress, tokenId=tokenId)
        async with self.saver.create_transaction() as connection:
            currentTokenMultiOwnerships = await self.retriever.list_token_multi_ownerships(connection=connection, fieldFilters=[
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.tokenId.key, eq=tokenId),
            ])
            existingOwnershipTuplesMap = {self._uniqueness_tuple_from_token_multi_ownership(retrievedTokenMultiOwnership=tokenMultiOwnership): tokenMultiOwnership for tokenMultiOwnership in currentTokenMultiOwnerships}
            existingOwnershipTuples = set(existingOwnershipTuplesMap.keys())
            retrievedOwnershipTuplesMaps = {self._uniqueness_tuple_from_token_multi_ownership(retrievedTokenMultiOwnership=retrievedTokenMultiOwnership): retrievedTokenMultiOwnership for retrievedTokenMultiOwnership in retrievedTokenMultiOwnerships}
            retrievedOwnershipTuples = set(retrievedOwnershipTuplesMaps.keys())
            tokenMultiOwnershipIdsToDelete = []
            for existingTuple, existingTokenMultiOwnership in existingOwnershipTuplesMap.items():
                if existingTuple in retrievedOwnershipTuples:
                    continue
                tokenMultiOwnershipIdsToDelete.append(existingTokenMultiOwnership.tokenMultiOwnershipId)
            await self.saver.delete_token_multi_ownerships(connection=connection, tokenMultiOwnershipIds=tokenMultiOwnershipIdsToDelete)
            retrievedTokenMultiOwnershipsToSave = []
            for retrievedTuple, retrievedTokenMultiOwnership in retrievedOwnershipTuplesMaps.items():
                if retrievedTuple in existingOwnershipTuples:
                    continue
                retrievedTokenMultiOwnershipsToSave.append(retrievedTokenMultiOwnership)
            await self.saver.create_token_multi_ownerships(connection=connection, retrievedTokenMultiOwnerships=retrievedTokenMultiOwnershipsToSave)
            logging.info(f'Saving multi ownerships: saved {len(retrievedTokenMultiOwnershipsToSave)}, deleted {len(tokenMultiOwnershipIdsToDelete)}, kept {len(existingOwnershipTuples) - len(retrievedOwnershipTuples)}')

    async def list_collection_tokens_by_owner(self, address: str, ownerAddress: str) -> List[Token]:
        collection = await self.get_collection_by_address(address=address)
        tokens = []
        if collection.doesSupportErc721:
            tokenOwnerships = await self.retriever.list_token_ownerships(fieldFilters=[
                StringFieldFilter(fieldName=TokenOwnershipsTable.c.registryAddress.key, eq=address),
                StringFieldFilter(fieldName=TokenOwnershipsTable.c.ownerAddress.key, eq=ownerAddress),
            ])
            tokens += [Token(registryAddress=tokenOwnership.registryAddress, tokenId=tokenOwnership.tokenId) for tokenOwnership in tokenOwnerships]
        elif collection.doesSupportErc1155:
            tokenMultiOwnerships = await self.retriever.list_token_multi_ownerships(fieldFilters=[
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.registryAddress.key, eq=address),
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.ownerAddress.key, eq=ownerAddress),
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.quantity.key, eq=0),
            ])
            tokens += [Token(registryAddress=tokenMultiOwnership.registryAddress, tokenId=tokenMultiOwnership.tokenId) for tokenMultiOwnership in tokenMultiOwnerships]
        return tokens
