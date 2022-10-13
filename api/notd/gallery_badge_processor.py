
from notd.model import COLLECTION_GOBLINTOWN_ADDRESS
from notd.model import COLLECTION_MDTP_ADDRESS
from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.model import COLLECTION_SPRITE_CLUB_ADDRESS
from notd.rudeboy_badge_processor import RudeboysBadgeProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class GalleryBadgeProcessor:

    def __init__(self, retriever: Retriever, saver: Saver, registryAddress: str) -> None:
        self.retriever= retriever
        self.saver= saver
        self.registryAddress = registryAddress
        self.processor = {
            self.registryAddress == COLLECTION_RUDEBOYS_ADDRESS : RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
            self.registryAddress == COLLECTION_GOBLINTOWN_ADDRESS : None, # RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
            self.registryAddress == COLLECTION_MDTP_ADDRESS : None, # RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
            self.registryAddress == COLLECTION_SPRITE_CLUB_ADDRESS : None,# RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
        }.get(True)


    def route_processor(self, registryAddress: str) -> None:
        processor = {
            registryAddress == COLLECTION_RUDEBOYS_ADDRESS : RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
            registryAddress == COLLECTION_GOBLINTOWN_ADDRESS : None, # RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
            registryAddress == COLLECTION_MDTP_ADDRESS : None, # RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
            registryAddress == COLLECTION_SPRITE_CLUB_ADDRESS : None,# RudeboysBadgeProcessor(retriever=self.retriever, saver=self.saver),
        }.get(True)

        return processor
