import logging

from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import list_util

from notd.badge_processor import CollectionBadgeProcessor
from notd.messages import RefreshAllCollectionBadgesMessageContent
from notd.messages import RefreshCollectionBadgeMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import CollectionBadgeHoldersTable


class CollectionBadgeManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: SqsMessageQueue, collectionBadgeProcessor: CollectionBadgeProcessor) -> None:
        self.retriever= retriever
        self.saver= saver
        self.workQueue= workQueue
        self.collectionBadgeProcessor= collectionBadgeProcessor

    async def refresh_all_collection_badges_deferred(self):
        await self.workQueue.send_message(message=RefreshAllCollectionBadgesMessageContent().to_message())

    async def refresh_all_collection_badges(self):
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_collection_badges_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_collection_badges_for_collection_deferred(self, registryAddress: str):
        await self.workQueue.send_message(message=RefreshCollectionBadgeMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_collection_badges_for_collection(self, registryAddress: str):
        registryAddress = chain_util.normalize_address(registryAddress)
        # NOTE(Femi-Ogunkola): Figure out how to map to rudeboy processor and get all the badge holders at once
        # retrievedGalleryBadgeHolder = await self.processor.calculate_collection_overlap(registryAddress=registryAddress)
        retrievedGalleryBadgeHolders = []
        async with self.saver.create_transaction() as connection:
            # TODO(krishan711): this would be more efficient if only changed ones are deleted and re-saved
            currentCollectionBadgeHolders = await self.retriever.list_collection_badge_holders(fieldFilters=[
                StringFieldFilter(fieldName=CollectionBadgeHoldersTable.c.registryAddress.key, eq=registryAddress),
            ], connection=connection)
            galleryBadgesToDelete = {collectionBadgeHolders.collectionBadgeHolderId for collectionBadgeHolders in currentCollectionBadgeHolders}
            logging.info(f'Deleting {len(galleryBadgesToDelete)} existing gallery badges')
            for chunkedIds in list_util.generate_chunks(lst=list(galleryBadgesToDelete), chunkSize=100):
                await self.saver.delete_collection_badge_holders(galleryBadgeHolderIds=chunkedIds, connection=connection)
            logging.info(f'Saving {len(retrievedGalleryBadgeHolders)} gallery badges')
            await self.saver.create_collection_badge_holders(retrievedGalleryBadgeHolders=retrievedGalleryBadgeHolders, connection=connection)
