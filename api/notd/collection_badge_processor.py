import abc
from abc import ABC


class CollectionBadgeProcessor(ABC):

    @abc.abstractmethod
    async def get_all_badges(self) -> None:
        pass
