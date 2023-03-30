import datetime

from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util

from notd.model import RetrievedCollectionHourlyActivity
from notd.model import RetrievedCollectionTotalActivity
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.store.schema import TokenTransfersTable


class CollectionActivityProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_collection_hourly_activity(self, address: str, startDate: datetime.datetime) -> RetrievedCollectionHourlyActivity:
        address = chain_util.normalize_address(address)
        startDate = date_util.date_hour_from_datetime(startDate)
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(TokenTransfersTable.c.registryAddress.key, eq=address),
                DateFieldFilter(BlocksTable.c.blockDate.key, gte=startDate),
                DateFieldFilter(BlocksTable.c.blockDate.key, lt=date_util.datetime_from_datetime(dt=startDate, hours=1)),
            ],
        )
        saleCount = 0
        transferCount = 0
        totalValue = 0
        averageValue = 0
        minimumValue = 0
        maximumValue = 0
        mintCount = 0
        for tokenTransfer in tokenTransfers:
            if tokenTransfer.value > 0:
                saleCount += tokenTransfer.amount
                totalValue += tokenTransfer.value
                minimumValue = min(minimumValue, tokenTransfer.value) if minimumValue > 0 else tokenTransfer.value
                maximumValue = max(maximumValue, tokenTransfer.value)
            transferCount += tokenTransfer.amount
            mintCount += tokenTransfer.amount if tokenTransfer.fromAddress == chain_util.BURN_ADDRESS else 0
        averageValue = int(totalValue / saleCount) if saleCount > 0 else 0
        return RetrievedCollectionHourlyActivity(address=address, date=startDate, transferCount=transferCount, saleCount=saleCount, mintCount=mintCount, totalValue=totalValue, minimumValue=minimumValue, maximumValue=maximumValue, averageValue=averageValue)

    async def calculate_collection_total_activity(self, address: str) -> RetrievedCollectionTotalActivity:
        address = chain_util.normalize_address(address)
        collectionHourlyActivities = await self.retriever.list_collection_activities(
          fieldFilters=[
                StringFieldFilter(CollectionHourlyActivitiesTable.c.address.key, eq=address),
            ],
        )
        saleCount = 0
        transferCount = 0
        totalValue = 0
        minimumValue = 0
        maximumValue = 0
        mintCount = 0
        for collectionHourlyActivity in collectionHourlyActivities:
            totalValue += collectionHourlyActivity.totalValue
            saleCount += collectionHourlyActivity.saleCount
            transferCount += collectionHourlyActivity.transferCount
            mintCount += collectionHourlyActivity.mintCount or 0
            maximumValue = max(maximumValue, collectionHourlyActivity.maximumValue)
            minimumValue = min(minimumValue, collectionHourlyActivity.minimumValue) if minimumValue > 0 else collectionHourlyActivity.minimumValue
        averageValue = int(totalValue / saleCount) if saleCount > 0 else 0
        return RetrievedCollectionTotalActivity(address=address, totalValue=totalValue, saleCount=saleCount, transferCount=transferCount, mintCount=mintCount, maximumValue=maximumValue, minimumValue=minimumValue, averageValue=averageValue)
