import abc
from abc import ABC
from typing import List

from notd.model import RetrievedGalleryBadgeHolder


class CollectionBadgeProcessor(ABC):

    @abc.abstractmethod
    async def calculate_all_gallery_badge_holders(self) -> List[RetrievedGalleryBadgeHolder]:
        pass
