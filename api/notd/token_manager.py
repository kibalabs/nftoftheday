import asyncio
from typing import List, Optional
from typing import Tuple

import sqlalchemy
from core import logging
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from core.util import list_util

from notd.collection_manager import CollectionManager
from notd.messages import UpdateCollectionTokensMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.model import TokenMetadata
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMetadatasTable
from notd.token_metadata_processor import TokenDoesNotExistException
from notd.token_metadata_processor import TokenHasNoMetadataException
from notd.token_metadata_processor import TokenMetadataProcessor

_TOKEN_UPDATE_MIN_DAYS = 7


class TokenManager:

    def __init__(self, saver: Saver, retriever: Retriever, tokenQueue: SqsMessageQueue, tokenMetadataProcessor: TokenMetadataProcessor, collectionManager: CollectionManager, ownershipManager: OwnershipManager):
        self.saver = saver
        self.retriever = retriever
        self.tokenQueue = tokenQueue
        self.tokenMetadataProcessor = tokenMetadataProcessor
        self.collectionManager = collectionManager
        self.ownershipManager = ownershipManager

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str) -> TokenMetadata:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        return await self._get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId, shouldProcessIfNotFound=True)

    async def _get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str, shouldProcessIfNotFound: bool = True, sleepSecondsBeforeProcess: float = 0) -> TokenMetadata:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        try:
            tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        except NotFoundException:
            if not shouldProcessIfNotFound:
                raise
            await asyncio.sleep(sleepSecondsBeforeProcess)
            await self.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=True)
            tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return tokenMetadata

    async def update_token_metadatas_deferred(self, collectionTokenIds: List[Tuple[str, str]], shouldForce: Optional[bool] = False) -> None:
        if len(collectionTokenIds) == 0:
            return
        collectionTokenIdsToProcess = set()
        if shouldForce:
            collectionTokenIdsToProcess = set(collectionTokenIds)
        else:
            for chunkedCollectionTokenIds in list_util.generate_chunks(lst=list(collectionTokenIds), chunkSize=1000):
                query = (
                    TokenMetadatasTable.select()
                        .where(TokenMetadatasTable.c.updatedDate > date_util.datetime_from_now(days=-_TOKEN_UPDATE_MIN_DAYS))
                        .where(sqlalchemy.tuple_(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId).in_(chunkedCollectionTokenIds))
                )
                recentlyUpdatedTokenMetadatas = await self.retriever.query_token_metadatas(query=query)
                recentlyUpdatedTokenIds = set((tokenMetadata.registryAddress, tokenMetadata.tokenId) for tokenMetadata in recentlyUpdatedTokenMetadatas)
                logging.info(f'Skipping {len(recentlyUpdatedTokenIds)} collectionTokenIds because they have been updated recently.')
                collectionTokenIdsToProcess.update(set(chunkedCollectionTokenIds) - recentlyUpdatedTokenIds)
        messages = [UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce).to_message() for (registryAddress, tokenId) in collectionTokenIdsToProcess]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: Optional[bool] = False) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        if not shouldForce:
            recentlyUpdatedTokens = await self.retriever.list_token_metadatas(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenMetadatasTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=TokenMetadatasTable.c.tokenId.key, eq=tokenId),
                    DateFieldFilter(fieldName=TokenMetadatasTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_TOKEN_UPDATE_MIN_DAYS))
                ],
            )
            if len(recentlyUpdatedTokens) > 0:
                logging.info('Skipping token because it has been updated recently.')
                return
        await self.tokenQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: Optional[bool] = False) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        if not shouldForce:
            recentlyUpdatedTokens = await self.retriever.list_token_metadatas(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenMetadatasTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=TokenMetadatasTable.c.tokenId.key, eq=tokenId),
                    DateFieldFilter(fieldName=TokenMetadatasTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_TOKEN_UPDATE_MIN_DAYS))
                ],
            )
            if len(recentlyUpdatedTokens) > 0:
                logging.info('Skipping token because it has been updated recently.')
                return
        collection = await self.collectionManager.get_collection_by_address(address=registryAddress)
        try:
            retrievedTokenMetadata = await self.tokenMetadataProcessor.retrieve_token_metadata(registryAddress=registryAddress, tokenId=tokenId, collection=collection)
        except (TokenDoesNotExistException, TokenHasNoMetadataException) as exception:
            logging.info(f'Failed to retrieve metadata for token: {registryAddress}/{tokenId}: {exception}')
            retrievedTokenMetadata = None
        async with self.saver.create_transaction() as connection:
            try:
                tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(connection=connection, registryAddress=registryAddress, tokenId=tokenId)
            except NotFoundException:
                tokenMetadata = None
            if tokenMetadata:
                if not retrievedTokenMetadata:
                    logging.info(f'Skipped updating token metadata because it failed to retrieve.')
                    return
                hasTokenChanged = (
                    tokenMetadata.metadataUrl != retrievedTokenMetadata.metadataUrl or \
                    tokenMetadata.name != retrievedTokenMetadata.name  or \
                    tokenMetadata.description != retrievedTokenMetadata.description or \
                    tokenMetadata.imageUrl != retrievedTokenMetadata.imageUrl or \
                    tokenMetadata.resizableImageUrl != retrievedTokenMetadata.resizableImageUrl or \
                    tokenMetadata.animationUrl != retrievedTokenMetadata.animationUrl or \
                    tokenMetadata.youtubeUrl != retrievedTokenMetadata.youtubeUrl or \
                    tokenMetadata.backgroundColor != retrievedTokenMetadata.backgroundColor or \
                    tokenMetadata.frameImageUrl != retrievedTokenMetadata.frameImageUrl or \
                    tokenMetadata.attributes != retrievedTokenMetadata.attributes
                )
                if not hasTokenChanged:
                    logging.info(f'Skipped updating token metadata because it has not changed.')
                    return
                await self.saver.update_token_metadata(connection=connection, tokenMetadataId=tokenMetadata.tokenMetadataId, metadataUrl=retrievedTokenMetadata.metadataUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, imageUrl=retrievedTokenMetadata.imageUrl, resizableImageUrl=retrievedTokenMetadata.resizableImageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, frameImageUrl=retrievedTokenMetadata.frameImageUrl, attributes=retrievedTokenMetadata.attributes)
            else:
                if retrievedTokenMetadata is None:
                    retrievedTokenMetadata = TokenMetadataProcessor.get_default_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
                await self.saver.create_token_metadata(connection=connection, registryAddress=retrievedTokenMetadata.registryAddress, tokenId=retrievedTokenMetadata.tokenId, metadataUrl=retrievedTokenMetadata.metadataUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, imageUrl=retrievedTokenMetadata.imageUrl, resizableImageUrl=retrievedTokenMetadata.resizableImageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, frameImageUrl=retrievedTokenMetadata.frameImageUrl, attributes=retrievedTokenMetadata.attributes)

    async def update_collection_tokens(self, address: str, shouldForce: Optional[bool] = False) -> None:
        address = chain_util.normalize_address(value=address)
        tokenMetadatas = await self.retriever.list_token_metadatas(fieldFilters=[
            StringFieldFilter(fieldName=TokenMetadatasTable.c.registryAddress.key, eq=address),
        ])
        collectionTokenIds = list(set((tokenMetadata.registryAddress, tokenMetadata.tokenId) for tokenMetadata in tokenMetadatas))
        await self.collectionManager.update_collection_deferred(address=address, shouldForce=shouldForce)
        await self.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds, shouldForce=shouldForce)
        await self.ownershipManager.update_token_ownerships_deferred(collectionTokenIds=collectionTokenIds)

    async def update_collection_tokens_deferred(self, address: str, shouldForce: Optional[bool] = False):
        address = chain_util.normalize_address(value=address)
        await self.tokenQueue.send_message(message=UpdateCollectionTokensMessageContent(address=address, shouldForce=shouldForce).to_message())

    async def list_collection_tokens(self, address: str) -> List[TokenMetadata]:
        address = chain_util.normalize_address(value=address)
        tokens = await self.retriever.list_token_metadatas(fieldFilters=[StringFieldFilter(fieldName=TokenMetadatasTable.c.registryAddress.key, eq=address)])
        return tokens
