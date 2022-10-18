from typing import List

from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.model import RetrievedGalleryBadgeHolder
from notd.rudeboy_badge_processor import RudeboysBadgeProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class BadgeProcessor:

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever = retriever
        self.saver = saver

    async def calculate_all_gallery_badge_holders(self, registryAddress: str) -> List[RetrievedGalleryBadgeHolder]:
        if registryAddress == COLLECTION_RUDEBOYS_ADDRESS:
            processor = RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver)
            retrievedBadges = await processor.calculate_all_gallery_badge_holders()
            return retrievedBadges
        return []
