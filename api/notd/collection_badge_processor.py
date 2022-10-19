import abc
from abc import ABC


class CollectionBadgeProcessor(ABC):

    @abc.abstractmethod
    async def calculate_all_gallery_badge_holders(self) -> None:
        pass
