
from notd.model import COLLECTION_GOBLINTOWN_ADDRESS
from notd.model import COLLECTION_MDTP_ADDRESS
from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.model import COLLECTION_SPRITE_CLUB_ADDRESS
from notd.rudeboy_badge_processor import RudeboysBadgeProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class CollectionBadgeProcessor:

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever= retriever
        self.saver= saver

    def calculate_badges(self, registryAddress: str) -> None:
        if registryAddress == COLLECTION_RUDEBOYS_ADDRESS:
            processor = RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver)
            retrievedBadges = processor.get_all_badges()
        if registryAddress == COLLECTION_GOBLINTOWN_ADDRESS:
            pass
        if registryAddress == COLLECTION_MDTP_ADDRESS:
            pass
        if registryAddress == COLLECTION_SPRITE_CLUB_ADDRESS:
            pass
        return retrievedBadges
