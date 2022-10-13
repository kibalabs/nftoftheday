import logging
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter
from core.util import chain_util, list_util
from api.notd.messages import RefreshAllGalleryBadgesMessageContent, RefreshGalleryBadgeMessageContent
from api.notd.model import GALLERY_COLLECTIONS
from api.notd.store.schema import GalleryBadgeHoldersTable

from notd.gallery_badge_processor import GalleryBadgeProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class GalleryBadgeManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: SqsMessageQueue, galleryBadgeProcessor: GalleryBadgeProcessor) -> None:
        self.retriever= retriever
        self.saver= saver
        self.workQueue= workQueue
        self.galleryBadgeProcessor= galleryBadgeProcessor

    async def refresh_all_gallery_badges_deferred(self):
        await self.workQueue.send_message(message=RefreshAllGalleryBadgesMessageContent().to_message())

    async def refresh_all_gallery_badges(self):
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_gallery_badges_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_gallery_badges_for_collection_deferred(self, registryAddress: str):
        await self.workQueue.send_message(message=RefreshGalleryBadgeMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_gallery_badges_for_collection(self, registryAddress: str):
        registryAddress = chain_util.normalize_address(registryAddress)
        # NOTE(Femi-Ogunkola): Figure out how to map to rudeboy processor and get all the badge holders at once
        # retrievedGalleryBadgeHolder = await self.processor.calculate_collection_overlap(registryAddress=registryAddress)
        retrievedGalleryBadgeHolders = []
        async with self.saver.create_transaction() as connection:
            # TODO(krishan711): this would be more efficient if only changed ones are deleted and re-saved
            currentGalleryBadgeHolders = await self.retriever.list_gallery_badge_holders(fieldFilters=[
                StringFieldFilter(fieldName=GalleryBadgeHoldersTable.c.registryAddress.key, eq=registryAddress),
            ], connection=connection)
            galleryBadgesToDelete = {galleryBadgeHolders.galleryBadgeHolderId for galleryBadgeHolders in currentGalleryBadgeHolders}
            logging.info(f'Deleting {len(galleryBadgesToDelete)} existing gallery badges')
            for chunkedIds in list_util.generate_chunks(lst=list(galleryBadgesToDelete), chunkSize=100):
                await self.saver.delete_gallery_badge_holders(galleryBadgeHolderIds=chunkedIds, connection=connection)
            logging.info(f'Saving {len(retrievedGalleryBadgeHolders)} gallery badges')
            await self.saver.create_gallery_badge_holders(retrievedGalleryBadgeHolders=retrievedGalleryBadgeHolders, connection=connection)
