import asyncio
import random
from typing import Optional
from typing import Sequence

from core import logging
from core.exceptions import NotFoundException
from core.queues.message_queue import MessageQueue
from core.queues.model import Message
from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util

from notd.collection_processor import CollectionDoesNotExist
from notd.collection_processor import CollectionProcessor
from notd.messages import UpdateCollectionMessageContent
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionsTable

from .model import Collection

_COLLECTION_UPDATE_MIN_DAYS = 30


class CollectionManager:

    def __init__(self, saver: Saver, retriever: Retriever, tokenQueue: MessageQueue[Message], collectionProcessor: CollectionProcessor) -> None:
        self.saver = saver
        self.retriever = retriever
        self.tokenQueue = tokenQueue
        self.collectionProcessor = collectionProcessor

    async def get_collection_by_address(self, address: str) -> Collection:
        address = chain_util.normalize_address(value=address)
        return await self._get_collection_by_address(address=address, shouldProcessIfNotFound=True)

    async def _get_collection_by_address(self, address: str, shouldProcessIfNotFound: bool = True, sleepSecondsBeforeProcess: Optional[float] = None) -> Collection:
        if sleepSecondsBeforeProcess is None:
            sleepSecondsBeforeProcess = 0.1 * random.randint(1, 10)
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

    async def update_collections_deferred(self, addresses: Sequence[str], shouldForce: Optional[bool] = False) -> None:
        if len(addresses) == 0:
            return
        if not shouldForce:
            recentlyUpdatedCollections = await self.retriever.list_collections(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, containedIn=addresses),
                    DateFieldFilter(fieldName=TokenCollectionsTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_COLLECTION_UPDATE_MIN_DAYS))
                ],
            )
            recentlyUpdatedAddresses = {collection.address for collection in recentlyUpdatedCollections}
            logging.info(f'Skipping {len(recentlyUpdatedAddresses)} collections because they have been updated recently.')
            addresses = list(set(addresses) - recentlyUpdatedAddresses)
        messages = [UpdateCollectionMessageContent(address=address).to_message() for address in addresses]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_collection_deferred(self, address: str, shouldForce: Optional[bool] = False) -> None:
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

    async def update_collection(self, address: str, shouldForce: Optional[bool] = False) -> None:
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
