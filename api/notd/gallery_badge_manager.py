from core.queues.sqs_message_queue import SqsMessageQueue

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
        pass

    async def refresh_all_gallery_badges(self):
        pass

    async def refresh_gallery_badges_for_collection_deferred(self, registryAddress: str):
        pass

    async def refresh_gallery_badges_for_collection(self, registryAddress: str):
        pass
