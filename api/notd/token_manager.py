import asyncio
import datetime
import random
from typing import List
from typing import Set
from typing import Tuple

import sqlalchemy
from core import logging
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from core.util import list_util

from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_processor import CollectionDoesNotExist
from notd.collection_processor import CollectionProcessor
from notd.date_util import date_hour_from_datetime
from notd.date_util import generate_clock_hour_intervals
from notd.messages import UpdateActivityForAllCollectionsMessageContent
from notd.messages import UpdateActivityForCollectionMessageContent
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateCollectionTokenAttributesMessageContent
from notd.messages import UpdateCollectionTokensMessageContent
from notd.messages import UpdateListingsForAllCollections
from notd.messages import UpdateListingsForCollection
from notd.messages import UpdateTokenAttributesForAllCollectionsMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.messages import UpdateTokenOwnershipMessageContent
from notd.model import Collection
from notd.model import RetrievedTokenMultiOwnership
from notd.model import Token
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.token_attributes_processor import TokenAttributeProcessor
from notd.token_listing_processor import TokenListingProcessor
from notd.token_metadata_processor import TokenDoesNotExistException
from notd.token_metadata_processor import TokenHasNoMetadataException
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import NoOwnershipException
from notd.token_ownership_processor import TokenOwnershipProcessor

_TOKEN_UPDATE_MIN_DAYS = 7
_COLLECTION_UPDATE_MIN_DAYS = 30


GALLERY_COLLECTIONS = {
    # Sprite Club
    chain_util.normalize_address(value='0x2744fe5e7776bca0af1cdeaf3ba3d1f5cae515d3'),
    # Goblin Town
    chain_util.normalize_address(value='0xbce3781ae7ca1a5e050bd9c4c77369867ebc307e'),
    # MDTP
    chain_util.normalize_address(value='0x8e720f90014fa4de02627f4a4e217b7e3942d5e8'),
}


class TokenManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, tokenQueue: SqsMessageQueue, collectionProcessor: CollectionProcessor, tokenMetadataProcessor: TokenMetadataProcessor, tokenOwnershipProcessor: TokenOwnershipProcessor, collectionActivityProcessor: CollectionActivityProcessor, tokenAttributeProcessor: TokenAttributeProcessor, tokenListingProcessor: TokenListingProcessor):
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenQueue = tokenQueue
        self.collectionProcessor = collectionProcessor
        self.tokenMetadataProcessor = tokenMetadataProcessor
        self.tokenOwnershipProcessor = tokenOwnershipProcessor
        self.collectionActivityProcessor = collectionActivityProcessor
        self.tokenAttributeProcessor = tokenAttributeProcessor
        self.tokenListingProcessor = tokenListingProcessor

    async def get_collection_by_address(self, address: str) -> Collection:
        address = chain_util.normalize_address(value=address)
        return await self._get_collection_by_address(address=address, shouldProcessIfNotFound=True)

    async def _get_collection_by_address(self, address: str, shouldProcessIfNotFound: bool = True, sleepSecondsBeforeProcess: float = 0) -> Collection:
        address = chain_util.normalize_address(value=address)
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

    async def update_token_metadatas_deferred(self, collectionTokenIds: List[Tuple[str, str]], shouldForce: bool = False) -> None:
        if len(collectionTokenIds) == 0:
            return
        if not shouldForce:
            query = (
                TokenMetadatasTable.select()
                    .where(TokenMetadatasTable.c.updatedDate > date_util.datetime_from_now(days=-_TOKEN_UPDATE_MIN_DAYS))
                    .where(sqlalchemy.tuple_(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId).in_(collectionTokenIds))
            )
            recentlyUpdatedTokenMetadatas = await self.retriever.query_token_metadatas(query=query)
            recentlyUpdatedTokenIds = set((tokenMetadata.registryAddress, tokenMetadata.tokenId) for tokenMetadata in recentlyUpdatedTokenMetadatas)
            logging.info(f'Skipping {len(recentlyUpdatedTokenIds)} collectionTokenIds because they have been updated recently.')
            collectionTokenIds = set(collectionTokenIds) - recentlyUpdatedTokenIds
        messages = [UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce).to_message() for (registryAddress, tokenId) in collectionTokenIds]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
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

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
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
        collection = await self._get_collection_by_address(address=registryAddress, shouldProcessIfNotFound=True, sleepSecondsBeforeProcess=0.1 * random.randint(1, 10))
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
                    tokenMetadata.animationUrl != retrievedTokenMetadata.animationUrl or \
                    tokenMetadata.youtubeUrl != retrievedTokenMetadata.youtubeUrl or \
                    tokenMetadata.backgroundColor != retrievedTokenMetadata.backgroundColor or \
                    tokenMetadata.frameImageUrl != retrievedTokenMetadata.frameImageUrl or \
                    tokenMetadata.attributes != retrievedTokenMetadata.attributes
                )
                if not hasTokenChanged:
                    logging.info(f'Skipped updating token metadata because it has not changed.')
                    return
                await self.saver.update_token_metadata(connection=connection, tokenMetadataId=tokenMetadata.tokenMetadataId, metadataUrl=retrievedTokenMetadata.metadataUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, frameImageUrl=retrievedTokenMetadata.frameImageUrl, attributes=retrievedTokenMetadata.attributes)
            else:
                if retrievedTokenMetadata is None:
                    retrievedTokenMetadata = TokenMetadataProcessor.get_default_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
                await self.saver.create_token_metadata(connection=connection, registryAddress=retrievedTokenMetadata.registryAddress, tokenId=retrievedTokenMetadata.tokenId, metadataUrl=retrievedTokenMetadata.metadataUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, imageUrl=retrievedTokenMetadata.imageUrl, animationUrl=retrievedTokenMetadata.animationUrl, youtubeUrl=retrievedTokenMetadata.youtubeUrl, backgroundColor=retrievedTokenMetadata.backgroundColor, frameImageUrl=retrievedTokenMetadata.frameImageUrl, attributes=retrievedTokenMetadata.attributes)

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
        address = chain_util.normalize_address(value=address)
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
        address = chain_util.normalize_address(value=address)
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
        address = chain_util.normalize_address(value=address)
        tokenMetadatas = await self.retriever.list_token_metadatas(fieldFilters=[
            StringFieldFilter(fieldName=TokenMetadatasTable.c.registryAddress.key, eq=address),
        ])
        collectionTokenIds = list(set((tokenMetadata.registryAddress, tokenMetadata.tokenId) for tokenMetadata in tokenMetadatas))
        await self.update_collection_deferred(address=address, shouldForce=shouldForce)
        await self.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds, shouldForce=shouldForce)
        await self.update_token_ownerships_deferred(collectionTokenIds=collectionTokenIds)

    async def update_collection_tokens_deferred(self, address: str, shouldForce: bool = False):
        address = chain_util.normalize_address(value=address)
        await self.tokenQueue.send_message(message=UpdateCollectionTokensMessageContent(address=address, shouldForce=shouldForce).to_message())

    async def update_token_ownerships_deferred(self, collectionTokenIds: List[Tuple[str, str]]) -> None:
        if len(collectionTokenIds) == 0:
            return
        collectionTokenIds = set(collectionTokenIds)
        messages = [UpdateTokenOwnershipMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message() for (registryAddress, tokenId) in collectionTokenIds]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_token_ownership_deferred(self, registryAddress: str, tokenId: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        await self.tokenQueue.send_message(message=UpdateTokenOwnershipMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_token_ownership(self, registryAddress: str, tokenId: str):
        registryAddress = chain_util.normalize_address(value=registryAddress)
        collection = await self.get_collection_by_address(address=registryAddress)
        if collection.doesSupportErc721:
            await self._update_token_single_ownership(registryAddress=registryAddress, tokenId=tokenId)
        elif collection.doesSupportErc1155:
            await self._update_token_multi_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def _update_token_single_ownership(self, registryAddress: str, tokenId: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        async with self.saver.create_transaction() as connection:
            try:
                tokenOwnership = await self.retriever.get_token_ownership_by_registry_address_token_id(connection=connection, registryAddress=registryAddress, tokenId=tokenId)
            except NotFoundException:
                tokenOwnership = None
            try:
                retrievedTokenOwnership = await self.tokenOwnershipProcessor.calculate_token_single_ownership(registryAddress=registryAddress, tokenId=tokenId)
            except NoOwnershipException:
                logging.error(f'No ownership found for {registryAddress}:{tokenId}')
                return
            if tokenOwnership:
                await self.saver.update_token_ownership(connection=connection, tokenOwnershipId=tokenOwnership.tokenOwnershipId, ownerAddress=retrievedTokenOwnership.ownerAddress, transferDate=retrievedTokenOwnership.transferDate, transferValue=retrievedTokenOwnership.transferValue, transferTransactionHash=retrievedTokenOwnership.transferTransactionHash)
            else:
                await self.saver.create_token_ownership(connection=connection, registryAddress=retrievedTokenOwnership.registryAddress, tokenId=retrievedTokenOwnership.tokenId, ownerAddress=retrievedTokenOwnership.ownerAddress, transferDate=retrievedTokenOwnership.transferDate, transferValue=retrievedTokenOwnership.transferValue, transferTransactionHash=retrievedTokenOwnership.transferTransactionHash)

    @staticmethod
    def _uniqueness_tuple_from_token_multi_ownership(retrievedTokenMultiOwnership: RetrievedTokenMultiOwnership) -> Tuple[str, str, str, int, int, datetime.datetime, str]:
        return (retrievedTokenMultiOwnership.registryAddress, retrievedTokenMultiOwnership.tokenId, retrievedTokenMultiOwnership.ownerAddress, retrievedTokenMultiOwnership.quantity, retrievedTokenMultiOwnership.averageTransferValue, retrievedTokenMultiOwnership.latestTransferDate, retrievedTokenMultiOwnership.latestTransferTransactionHash)

    async def _update_token_multi_ownership(self, registryAddress: str, tokenId: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        latestTransfers = await self.retriever.list_token_transfers(fieldFilters=[
            StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
            StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
        ], orders=[Order(fieldName=BlocksTable.c.updatedDate.key, direction=Direction.DESCENDING)], limit=1)
        if len(latestTransfers) == 0:
            return
        latestTransfer = latestTransfers[0]
        latestOwnerships = await self.retriever.list_token_multi_ownerships(fieldFilters=[
            StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.registryAddress.key, eq=registryAddress),
            StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.tokenId.key, eq=tokenId),
        ], orders=[Order(fieldName=TokenMultiOwnershipsTable.c.updatedDate.key, direction=Direction.DESCENDING)], limit=1)
        latestOwnership = latestOwnerships[0] if len(latestOwnerships) > 0 else None
        if latestOwnership is not None and latestOwnership.updatedDate > latestTransfer.updatedDate:
            logging.info(f'Skipping updating token_multi_ownership because last record ({latestOwnership.updatedDate}) is newer that last transfer update ({latestTransfer.updatedDate})')
            return
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
            logging.info(f'Saving multi ownerships: saved {len(retrievedTokenMultiOwnershipsToSave)}, deleted {len(tokenMultiOwnershipIdsToDelete)}, kept {len(existingOwnershipTuples - retrievedOwnershipTuples) - len(tokenMultiOwnershipIdsToDelete)}')
            # NOTE(krishan711): if nothing changed, force update one so that it doesn't update again
            if len(existingOwnershipTuplesMap) > 0 and len(retrievedTokenMultiOwnershipsToSave) == 0 and len(tokenMultiOwnershipIdsToDelete) == 0:
                firstOwnership = list(existingOwnershipTuplesMap.values())[0]
                await self.saver.update_token_multi_ownership(connection=connection, tokenMultiOwnershipId=firstOwnership.tokenMultiOwnershipId, ownerAddress=firstOwnership.ownerAddress)

    async def list_collection_tokens(self, address: str) -> List[TokenMetadata]:
        address = chain_util.normalize_address(value=address)
        tokens = await self.retriever.list_token_metadatas(fieldFilters=[StringFieldFilter(fieldName=TokenMetadatasTable.c.registryAddress.key, eq=address)])
        return tokens

    async def list_collection_tokens_by_owner(self, address: str, ownerAddress: str) -> List[Token]:
        address = chain_util.normalize_address(value=address)
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

    async def reprocess_owner_token_ownerships(self, ownerAddress: str) -> None:
        tokenTransfers = await self.retriever.list_token_transfers(fieldFilters=[StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=ownerAddress)])
        collectionTokenIds = list({(transfer.registryAddress, transfer.tokenId) for transfer in tokenTransfers})
        logging.info(f'Refreshing {len(collectionTokenIds)} ownerships')
        for collectionTokenIdChunk in list_util.generate_chunks(lst=collectionTokenIds, chunkSize=10):
            await asyncio.gather(*[self.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId) for (registryAddress, tokenId) in collectionTokenIdChunk])
        await self.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds)

    async def update_activity_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=UpdateActivityForAllCollectionsMessageContent().to_message())

    async def _get_transferred_collections_in_period(self, startDate: datetime.datetime, endDate: datetime.datetime) -> Set[Tuple[str, datetime.datetime]]:
        updatedBlocksQuery = (
            BlocksTable.select()
                .with_only_columns([BlocksTable.c.blockNumber])
                .where(BlocksTable.c.updatedDate >= startDate)
                .where(BlocksTable.c.updatedDate <= endDate)
        )
        updatedBlocksResult = await self.retriever.database.execute(query=updatedBlocksQuery)
        updatedBlocks = sorted([blockNumber for (blockNumber, ) in updatedBlocksResult])
        registryDatePairs: Set[Tuple[str, datetime.datetime]] = set()
        for blockNumbers in list_util.generate_chunks(lst=updatedBlocks, chunkSize=100):
            updatedTransfersQuery = (
                TokenTransfersTable.select()
                    .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                    .with_only_columns([TokenTransfersTable.c.registryAddress, BlocksTable.c.blockDate])
                    .where(TokenTransfersTable.c.blockNumber.in_(blockNumbers))
            )
            updatedTransfersResult = await self.retriever.database.execute(query=updatedTransfersQuery)
            newRegistryDatePairs = {(registryAddress, date_hour_from_datetime(dt=date)) for (registryAddress, date) in updatedTransfersResult}
            registryDatePairs.update(newRegistryDatePairs)
        return registryDatePairs

    async def update_activity_for_all_collections(self) -> None:
        processStartDate = date_util.datetime_from_now()
        latestUpdate = await self.retriever.get_latest_update_by_key_name(key='hourly_collection_activities')
        for periodStartDate, periodEndDate in generate_clock_hour_intervals(startDate=latestUpdate.date, endDate=processStartDate):
            logging.info(f'Finding transferred collections between {periodStartDate} and {periodEndDate}')
            registryDatePairs = await self._get_transferred_collections_in_period(startDate=periodStartDate, endDate=periodEndDate)
            logging.info(f'Scheduling processing for {len(registryDatePairs)} registryDatePairs')
            messages = [UpdateActivityForCollectionMessageContent(address=address, startDate=date).to_message() for (address, date) in registryDatePairs]
            await self.tokenQueue.send_messages(messages=messages)
            await self.saver.update_latest_update(latestUpdateId=latestUpdate.latestUpdateId, date=periodEndDate)

    async def update_activity_for_collection_deferred(self, address: str, startDate: datetime.datetime) -> None:
        address = chain_util.normalize_address(address)
        startDate = date_hour_from_datetime(startDate)
        await self.tokenQueue.send_message(message=UpdateActivityForCollectionMessageContent(address=address, startDate=startDate).to_message())

    async def update_activity_for_collection(self, address: str, startDate: datetime.datetime) -> None:
        address = chain_util.normalize_address(address)
        startDate = date_hour_from_datetime(startDate)
        retrievedCollectionActivity = await self.collectionActivityProcessor.calculate_collection_hourly_activity(address=address, startDate=startDate)
        async with self.saver.create_transaction() as connection:
            collectionActivity = await self.retriever.list_collection_activities(
                connection=connection,
                fieldFilters=[
                    StringFieldFilter(fieldName=CollectionHourlyActivityTable.c.address.key, eq=address),
                    DateFieldFilter(fieldName=CollectionHourlyActivityTable.c.date.key, eq=startDate)
                ]
            )
            if len(collectionActivity) > 0:
                await self.saver.update_collection_hourly_activity(connection=connection, collectionActivityId=collectionActivity[0].collectionActivityId, address=address, date=retrievedCollectionActivity.date, transferCount=retrievedCollectionActivity.transferCount, saleCount=retrievedCollectionActivity.saleCount, totalValue=retrievedCollectionActivity.totalValue, minimumValue=retrievedCollectionActivity.minimumValue, maximumValue=retrievedCollectionActivity.maximumValue, averageValue=retrievedCollectionActivity.averageValue,)
            else:
                if retrievedCollectionActivity.transferCount == 0:
                    logging.info(f'Not creating activity with transferCount==0')
                else:
                    await self.saver.create_collection_hourly_activity(connection=connection, address=retrievedCollectionActivity.address, date=retrievedCollectionActivity.date, transferCount=retrievedCollectionActivity.transferCount, saleCount=retrievedCollectionActivity.saleCount, totalValue=retrievedCollectionActivity.totalValue, minimumValue=retrievedCollectionActivity.minimumValue, maximumValue=retrievedCollectionActivity.maximumValue, averageValue=retrievedCollectionActivity.averageValue,)

    async def update_token_attributes_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=UpdateTokenAttributesForAllCollectionsMessageContent().to_message())

    async def update_token_attributes_for_all_collections(self) -> None:
        startDate = date_util.datetime_from_now()
        latestUpdate = await self.retriever.get_latest_update_by_key_name(key='token_attributes')
        latestProcessedDate = latestUpdate.date
        logging.info(f'Finding changed tokens since {latestProcessedDate}')
        updatedTokenMetadatasQuery = (
            TokenMetadatasTable.select()
            .with_only_columns([TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId])
            .where(TokenMetadatasTable.c.registryAddress.in_(GALLERY_COLLECTIONS))
            .where(TokenMetadatasTable.c.updatedDate >= latestProcessedDate)
        )
        updatedTokenMetadatasQueryResult = await self.retriever.database.execute(query=updatedTokenMetadatasQuery)
        updatedTokenMetadatas = set(updatedTokenMetadatasQueryResult)
        logging.info(f'Scheduling processing for {len(updatedTokenMetadatas)} changed tokens')
        messages = [UpdateCollectionTokenAttributesMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message() for (registryAddress, tokenId) in updatedTokenMetadatas]
        await self.tokenQueue.send_messages(messages=messages)
        await self.saver.update_latest_update(latestUpdateId=latestUpdate.latestUpdateId, date=startDate)

    async def update_collection_token_attributes_deferred(self, registryAddress: str, tokenId: str) -> None:
        await self.tokenQueue.send_message(message=UpdateCollectionTokenAttributesMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_collection_token_attributes(self, registryAddress: str, tokenId: str) -> None:
        tokenAttributes = await self.tokenAttributeProcessor.get_token_attributes(registryAddress=registryAddress, tokenId=tokenId)
        logging.info(f'Retrieved {len(tokenAttributes)} attributes')
        # TODO(krishan711): change this to not delete existing. should add / remove / update changed only
        async with self.saver.create_transaction() as connection:
            currentTokenAttributes = await self.retriever.list_token_attributes(fieldFilters=[
                StringFieldFilter(fieldName=TokenAttributesTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenAttributesTable.c.tokenId.key, eq=tokenId)
            ], connection=connection)
            currentTokenAttributeIds = [tokenAttributes.tokenAttributeId for tokenAttributes in currentTokenAttributes]
            logging.info(f'Deleting {len(currentTokenAttributeIds)} existing attributes')
            await self.saver.delete_token_attributes(tokenAttributeIds=currentTokenAttributeIds, connection=connection)
            logging.info(f'Saving {len(tokenAttributes)} attributes')
            await self.saver.create_token_attributes(retrievedTokenAttributes=tokenAttributes, connection=connection)

    async def update_latest_listings_for_all_collections_deferred(self, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=UpdateListingsForAllCollections().to_message(), delaySeconds=delaySeconds)

    async def update_latest_listings_for_all_collections(self) -> None:
        # NOTE(krishan711): delay because of opensea limits, find a nicer way to do this
        for index, registryAddress in enumerate(GALLERY_COLLECTIONS):
            await self.update_latest_listings_for_collection_deferred(address=registryAddress, delaySeconds=(60 * 5 * index))

    async def update_latest_listings_for_collection_deferred(self, address: str, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=UpdateListingsForCollection(address=address).to_message(), delaySeconds=delaySeconds)

    async def update_latest_listings_for_collection(self, address: str) -> None:
        tokenIdsQuery = (
            TokenMetadatasTable.select()
            .with_only_columns([TokenMetadatasTable.c.tokenId])
            .where(TokenMetadatasTable.c.registryAddress == address)
            .order_by(TokenMetadatasTable.c.tokenId.asc())
        )
        tokenIdsQueryResult = await self.retriever.database.execute(query=tokenIdsQuery)
        tokenIds = [tokenId for (tokenId, ) in tokenIdsQueryResult]
        openseaListings = await self.tokenListingProcessor.get_opensea_listings_for_tokens(registryAddress=address, tokenIds=tokenIds)
        logging.info(f'Retrieved {len(openseaListings)} opensea listings')
        allListings = openseaListings
        # TODO(krishan711): change this to not delete existing. should add / remove / update changed only
        async with self.saver.create_transaction() as connection:
            currentLatestTokenListings = await self.retriever.list_latest_token_listings(fieldFilters=[
                StringFieldFilter(fieldName=LatestTokenListingsTable.c.registryAddress.key, eq=address)
            ], connection=connection)
            currentLatestTokenListingIds = [latestTokenListing.tokenListingId for latestTokenListing in currentLatestTokenListings]
            logging.info(f'Deleting {len(currentLatestTokenListingIds)} existing listings')
            await self.saver.delete_latest_token_listings(latestTokenListingIds=currentLatestTokenListingIds, connection=connection)
            logging.info(f'Saving {len(allListings)} listings')
            await self.saver.create_latest_token_listings(retrievedTokenListings=allListings, connection=connection)
