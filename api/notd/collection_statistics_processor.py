import datetime

from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.model import RetrievedCollectionStatistics
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable


class CollectionStatisticsProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_statistics(self, registryAddress: str, date: datetime.datetime) -> RetrievedCollectionStatistics:
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                DateFieldFilter(BlocksTable.c.blockDate.key, gte=date_util.datetime_from_datetime(dt=date, hours=-1)),
                DateFieldFilter(BlocksTable.c.blockDate.key, lt=date),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
        )
        transferCount = totalVolume = averageValue = minimumValue = 0
        if len(tokenTransfers) > 0:
            for tokenTransfer in tokenTransfers:
                if tokenTransfer.value != 0:
                    minimumValue = min(float('inf'),tokenTransfer.value)
                transferCount += tokenTransfer.amount
                totalVolume += tokenTransfer.value
                averageValue += totalVolume/transferCount

            maximumValue = tokenTransfers[0].value
        else:
            maximumValue = 0
        return RetrievedCollectionStatistics(address=registryAddress, date=date, transferCount=transferCount, totalVolume=totalVolume, minimumValue=minimumValue, maximumValue=maximumValue, averageValue=averageValue)
