import datetime
from typing import Set
from typing import Tuple

from core import logging
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from core.util import list_util

from notd.collection_activity_processor import CollectionActivityProcessor
from notd.date_util import date_hour_from_datetime
from notd.date_util import generate_clock_hour_intervals
from notd.messages import UpdateActivityForAllCollectionsMessageContent
from notd.messages import UpdateActivityForCollectionMessageContent
from notd.messages import UpdateTotalActivityForAllCollectionsMessageContent
from notd.messages import UpdateTotalActivityForCollectionMessageContent
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema import TokenTransfersTable


class ActivityManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, tokenQueue: SqsMessageQueue, collectionActivityProcessor: CollectionActivityProcessor) -> None:
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenQueue = tokenQueue
        self.collectionActivityProcessor = collectionActivityProcessor

    async def update_activity_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=UpdateActivityForAllCollectionsMessageContent().to_message())

    async def _get_transferred_collections_in_period(self, startDate: datetime.datetime, endDate: datetime.datetime) -> Set[Tuple[str, datetime.datetime]]:
        updatedBlocksQuery = (
            BlocksTable.select()
                .with_only_columns([BlocksTable.c.blockNumber])
                .where(BlocksTable.c.updatedDate >= startDate)
                .where(BlocksTable.c.updatedDate <= endDate)
        )
        updatedBlocksResult = await self.retriever.database.execute(query=updatedBlocksQuery)
        updatedBlocks = sorted([blockNumber for (blockNumber, ) in updatedBlocksResult])
        registryDatePairs: Set[Tuple[str, datetime.datetime]] = set()
        for blockNumbers in list_util.generate_chunks(lst=updatedBlocks, chunkSize=100):
            updatedTransfersQuery = (
                TokenTransfersTable.select()
                    .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                    .with_only_columns([TokenTransfersTable.c.registryAddress, BlocksTable.c.blockDate])
                    .where(TokenTransfersTable.c.blockNumber.in_(blockNumbers))
            )
            updatedTransfersResult = await self.retriever.database.execute(query=updatedTransfersQuery)
            newRegistryDatePairs = {(registryAddress, date_hour_from_datetime(dt=date)) for (registryAddress, date) in updatedTransfersResult}
            registryDatePairs.update(newRegistryDatePairs)
        return registryDatePairs

    async def update_activity_for_all_collections(self) -> None:
        processStartDate = date_util.datetime_from_now()
        latestUpdate = await self.retriever.get_latest_update_by_key_name(key='hourly_collection_activities')
        for periodStartDate, periodEndDate in generate_clock_hour_intervals(startDate=latestUpdate.date, endDate=processStartDate):
            logging.info(f'Finding transferred collections between {periodStartDate} and {periodEndDate}')
            registryDatePairs = await self._get_transferred_collections_in_period(startDate=periodStartDate, endDate=periodEndDate)
            logging.info(f'Scheduling processing for {len(registryDatePairs)} registryDatePairs')
            messages = [UpdateActivityForCollectionMessageContent(address=address, startDate=date).to_message() for (address, date) in registryDatePairs]
            await self.tokenQueue.send_messages(messages=messages)
            await self.saver.update_latest_update(latestUpdateId=latestUpdate.latestUpdateId, date=periodEndDate)

    async def update_activity_for_collection_deferred(self, address: str, startDate: datetime.datetime) -> None:
        address = chain_util.normalize_address(address)
        startDate = date_hour_from_datetime(startDate)
        await self.tokenQueue.send_message(message=UpdateActivityForCollectionMessageContent(address=address, startDate=startDate).to_message())

    async def update_activity_for_collection(self, address: str, startDate: datetime.datetime) -> None:
        address = chain_util.normalize_address(address)
        startDate = date_hour_from_datetime(startDate)
        retrievedCollectionActivity = await self.collectionActivityProcessor.calculate_collection_hourly_activity(address=address, startDate=startDate)
        async with self.saver.create_transaction() as connection:
            collectionActivity = await self.retriever.list_collection_activities(
                connection=connection,
                fieldFilters=[
                    StringFieldFilter(fieldName=CollectionHourlyActivityTable.c.address.key, eq=address),
                    DateFieldFilter(fieldName=CollectionHourlyActivityTable.c.date.key, eq=startDate)
                ]
            )
            if len(collectionActivity) > 0:
                await self.saver.update_collection_hourly_activity(connection=connection, collectionActivityId=collectionActivity[0].collectionActivityId, address=address, date=retrievedCollectionActivity.date, transferCount=retrievedCollectionActivity.transferCount, saleCount=retrievedCollectionActivity.saleCount, totalValue=retrievedCollectionActivity.totalValue, minimumValue=retrievedCollectionActivity.minimumValue, maximumValue=retrievedCollectionActivity.maximumValue, averageValue=retrievedCollectionActivity.averageValue,)
            else:
                if retrievedCollectionActivity.transferCount == 0:
                    logging.info(f'Not creating activity with transferCount==0')
                else:
                    await self.saver.create_collection_hourly_activity(connection=connection, address=retrievedCollectionActivity.address, date=retrievedCollectionActivity.date, transferCount=retrievedCollectionActivity.transferCount, saleCount=retrievedCollectionActivity.saleCount, totalValue=retrievedCollectionActivity.totalValue, minimumValue=retrievedCollectionActivity.minimumValue, maximumValue=retrievedCollectionActivity.maximumValue, averageValue=retrievedCollectionActivity.averageValue,)

    async def update_total_activity_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=UpdateTotalActivityForAllCollectionsMessageContent().to_message())

    async def update_total_activity_for_all_collections(self) -> None:
        processStartDate = date_util.datetime_from_now()
        latestUpdate = await self.retriever.get_latest_update_by_key_name(key='total_collection_activities')
        query = (
            CollectionHourlyActivityTable.select()
            .with_only_columns([CollectionHourlyActivityTable.c.address])
            .filter(CollectionHourlyActivityTable.c.date >= latestUpdate.date)
        )
        result = await self.retriever.database.execute(query=query)
        changedAddresses = {row[0] for row in result}
        messages = [UpdateTotalActivityForCollectionMessageContent(address=address).to_message() for address in changedAddresses]
        await self.tokenQueue.send_messages(messages=messages)
        await self.saver.update_latest_update(latestUpdateId=latestUpdate.latestUpdateId, date=processStartDate)

    async def update_total_activity_for_collection(self, address: str) -> None:
        address = chain_util.normalize_address(address)
        retrievedCollectionTotalActivity = await self.collectionActivityProcessor.calculate_collection_total_activity(address=address)
        async with self.saver.create_transaction() as connection:
            collectionTotalActivity = None
            try:
                collectionTotalActivity = await self.retriever.get_collection_total_activity_by_address(address=address, connection=connection)
            except NotFoundException:
                pass
            if collectionTotalActivity:
                await self.saver.update_collection_total_activity(connection=connection, collectionActivityId=collectionTotalActivity.collectionTotalActivityId, address=address, transferCount=retrievedCollectionTotalActivity.transferCount, saleCount=retrievedCollectionTotalActivity.saleCount, totalValue=retrievedCollectionTotalActivity.totalValue, minimumValue=retrievedCollectionTotalActivity.minimumValue, maximumValue=retrievedCollectionTotalActivity.maximumValue, averageValue=retrievedCollectionTotalActivity.averageValue,)
            else:
                await self.saver.create_collection_total_activity(connection=connection, address=retrievedCollectionTotalActivity.address, transferCount=retrievedCollectionTotalActivity.transferCount, saleCount=retrievedCollectionTotalActivity.saleCount, totalValue=retrievedCollectionTotalActivity.totalValue, minimumValue=retrievedCollectionTotalActivity.minimumValue, maximumValue=retrievedCollectionTotalActivity.maximumValue, averageValue=retrievedCollectionTotalActivity.averageValue,)
