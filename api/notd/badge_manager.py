import logging

from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import list_util

from notd.badge_processor import BadgeProcessor
from notd.messages import RefreshGalleryBadgeHoldersForAllCollectionsMessageContent
from notd.messages import RefreshGalleryBadgeHoldersForCollectionMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import GalleryBadgeHoldersTable


class BadgeManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: SqsMessageQueue, badgeProcessor: BadgeProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.workQueue = workQueue
        self.badgeProcessor = badgeProcessor

    async def refresh_gallery_badge_holders_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=RefreshGalleryBadgeHoldersForAllCollectionsMessageContent().to_message())

    async def refresh_gallery_badge_holders_for_all_collections(self) -> None:
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_gallery_badge_holders_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_gallery_badge_holders_for_collection_deferred(self, registryAddress: str) -> None:
        await self.workQueue.send_message(message=RefreshGalleryBadgeHoldersForCollectionMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_gallery_badge_holders_for_collection(self, registryAddress: str) -> None:
        registryAddress = chain_util.normalize_address(registryAddress)
        retrievedGalleryBadgeHolders = await self.badgeProcessor.calculate_all_gallery_badge_holders(registryAddress=registryAddress)
        async with self.saver.create_transaction() as connection:
            currentGalleryBadgeHolders = await self.retriever.list_gallery_badge_holders(fieldFilters=[
                StringFieldFilter(fieldName=GalleryBadgeHoldersTable.c.registryAddress.key, eq=registryAddress),
            ], connection=connection)
            galleryBadgeHoldersToDelete = {galleryBadgeHolders.galleryBadgeHolderId for galleryBadgeHolders in currentGalleryBadgeHolders}
            logging.info(f'Deleting {len(galleryBadgeHoldersToDelete)} existing gallery badges')
            for chunkedIds in list_util.generate_chunks(lst=list(galleryBadgeHoldersToDelete), chunkSize=100):
                await self.saver.delete_gallery_badge_holders(galleryBadgeHolderIds=chunkedIds, connection=connection)
            logging.info(f'Saving {len(retrievedGalleryBadgeHolders)} gallery badges')
            await self.saver.create_gallery_badge_holders(retrievedGalleryBadgeHolders=retrievedGalleryBadgeHolders, connection=connection)
