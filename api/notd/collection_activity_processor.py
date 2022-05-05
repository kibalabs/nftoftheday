import datetime

from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util

from notd.date_util import date_hour_from_datetime
from notd.model import RetrievedCollectionHourlyActivity
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable


class CollectionActivityProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_hourly_activity(self, address: str, startDate: datetime.datetime) -> RetrievedCollectionHourlyActivity:
        address = chain_util.normalize_address(address)
        startDate = date_hour_from_datetime(startDate)
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(TokenTransfersTable.c.registryAddress.key, eq=address),
                DateFieldFilter(BlocksTable.c.blockDate.key, gte=startDate),
                DateFieldFilter(BlocksTable.c.blockDate.key, lt=date_util.datetime_from_datetime(dt=startDate, hours=1)),
            ],
        )
        #TODO INVESTIGATE VOLUME AND VALUE
        saleCount = 0
        transferCount = 0
        totalVolume = 0
        averageValue = 0
        minimumValue = 0
        maximumValue = 0
        for tokenTransfer in tokenTransfers:
            if tokenTransfer.value > 0:
                saleCount += tokenTransfer.amount
                totalVolume += tokenTransfer.value
                minimumValue = min(minimumValue, tokenTransfer.value) if minimumValue > 0 else tokenTransfer.value
                maximumValue = max(maximumValue, tokenTransfer.value)
            transferCount += tokenTransfer.amount
        averageValue = totalVolume / saleCount
        return RetrievedCollectionHourlyActivity(address=address, date=startDate, transferCount=transferCount, saleCount=saleCount, totalVolume=totalVolume, minimumValue=minimumValue, maximumValue=maximumValue, averageValue=averageValue)
