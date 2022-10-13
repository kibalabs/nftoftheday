import abc
from abc import ABC


class BadgeProcessor(ABC):

    @abc.abstractmethod
    async def get_all_badges(self) -> None:
        pass