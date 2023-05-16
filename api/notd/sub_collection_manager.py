import logging
from typing import Optional

from core.exceptions import NotFoundException
from core.queues.message_queue import MessageQueue
from core.queues.model import Message
from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.messages import UpdateSubCollectionMessageContent
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import SubCollectionsTable
from notd.sub_collection_processor import SubCollectionDoesNotExist
from notd.sub_collection_processor import SubCollectionProcessor

_SUB_COLLECTION_UPDATE_MIN_DAYS = 30

class SubCollectionManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: MessageQueue[Message], subCollectionProcessor: SubCollectionProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.workQueue = workQueue
        self.subCollectionProcessor = subCollectionProcessor

    async def update_sub_collection_deferred(self, registryAddress: str, externalId: str, shouldForce: Optional[bool] = False) -> None:
        if not shouldForce:
            recentlyUpdatedCollections = await self.retriever.list_collections(
                fieldFilters=[
                    StringFieldFilter(fieldName=SubCollectionsTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=SubCollectionsTable.c.externalId.key, eq=externalId),
                    DateFieldFilter(fieldName=SubCollectionsTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_SUB_COLLECTION_UPDATE_MIN_DAYS))
                ],
            )
            if len(recentlyUpdatedCollections) > 0:
                logging.info('Skipping collection because it has been updated recently.')
                return
        await self.workQueue.send_message(message=UpdateSubCollectionMessageContent(registryAddress=registryAddress, externalId=externalId).to_message())

    async def update_sub_collection(self, registryAddress: str, externalId: str, shouldForce: Optional[bool] = False) -> None:
        if not shouldForce:
            recentlyUpdatedSubCollections = await self.retriever.list_sub_collections(
                fieldFilters=[
                    StringFieldFilter(fieldName=SubCollectionsTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=SubCollectionsTable.c.externalId.key, eq=externalId),
                    DateFieldFilter(fieldName=SubCollectionsTable.c.updatedDate.key, gt=date_util.datetime_from_now(days=-_SUB_COLLECTION_UPDATE_MIN_DAYS))
                ],
            )
            if len(recentlyUpdatedSubCollections) > 0:
                logging.info('Skipping collection because it has been updated recently.')
                return
        try:
            retrievedSubCollection = await self.subCollectionProcessor.retrieve_sub_collection(registryAddress=registryAddress, externalId=externalId)
        except SubCollectionDoesNotExist:
            logging.info(f'Failed to retrieve non-existent collection: {registryAddress}')
            return
        async with self.saver.create_transaction() as connection:
            try:
                subCollection = await self.retriever.get_sub_collection_by_registry_address_external_id(connection=connection, registryAddress=registryAddress, externalId=externalId)
            except NotFoundException:
                subCollection = None
            if subCollection:
                await self.saver.update_sub_collection(connection=connection, subCollectionId=subCollection.subCollectionId, name=retrievedSubCollection.name, symbol=retrievedSubCollection.symbol, description=retrievedSubCollection.description, imageUrl=retrievedSubCollection.imageUrl, twitterUsername=retrievedSubCollection.twitterUsername, instagramUsername=retrievedSubCollection.instagramUsername, wikiUrl=retrievedSubCollection.wikiUrl, openseaSlug=retrievedSubCollection.openseaSlug, url=retrievedSubCollection.url, discordUrl=retrievedSubCollection.discordUrl, bannerImageUrl=retrievedSubCollection.bannerImageUrl, doesSupportErc721=retrievedSubCollection.doesSupportErc721, doesSupportErc1155=retrievedSubCollection.doesSupportErc1155)
            else:
                await self.saver.create_sub_collection(connection=connection, registryAddress=registryAddress, externalId=externalId, name=retrievedSubCollection.name, symbol=retrievedSubCollection.symbol, description=retrievedSubCollection.description, imageUrl=retrievedSubCollection.imageUrl, twitterUsername=retrievedSubCollection.twitterUsername, instagramUsername=retrievedSubCollection.instagramUsername, wikiUrl=retrievedSubCollection.wikiUrl, openseaSlug=retrievedSubCollection.openseaSlug, url=retrievedSubCollection.url, discordUrl=retrievedSubCollection.discordUrl, bannerImageUrl=retrievedSubCollection.bannerImageUrl, doesSupportErc721=retrievedSubCollection.doesSupportErc721, doesSupportErc1155=retrievedSubCollection.doesSupportErc1155)
