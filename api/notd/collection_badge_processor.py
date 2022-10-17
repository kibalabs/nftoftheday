import abc
from abc import ABC


class CollectionBadgeProcessor(ABC):

    @abc.abstractmethod
    async def calculate_all_badges(self) -> None:
        pass
