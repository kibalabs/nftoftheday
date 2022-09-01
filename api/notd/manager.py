import datetime
import json
import random
from typing import List
from typing import Optional
from typing import Sequence


import sqlalchemy

from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util

from notd.activity_manager import ActivityManager
from notd.attribute_manager import AttributeManager
from notd.block_manager import BlockManager
from notd.collection_manager import CollectionManager
from notd.listing_manager import ListingManager
from notd.messages import RefreshViewsMessageContent
from notd.model import BaseSponsoredToken
from notd.model import Collection
from notd.model import CollectionDailyActivity
from notd.model import CollectionStatistics
from notd.model import SponsoredToken
from notd.model import Token
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.model import TradedToken
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row
from notd.token_manager import TokenManager

_REGISTRY_BLACKLIST = set([
    '0x58A3c68e2D3aAf316239c003779F71aCb870Ee47', # Curve SynthSwap
    '0xFf488FD296c38a24CCcC60B43DD7254810dAb64e', # zed.run
    '0xC36442b4a4522E871399CD717aBDD847Ab11FE88', # uniswap-v3-positions
    '0xb9ed94c6d594b2517c4296e24a8c517ff133fb6d', # hegic-eth-atm-calls-pool
])


class NotdManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, blockManager: BlockManager, tokenManager: TokenManager, listingManager: ListingManager,  attributeManager: AttributeManager, activityManager: ActivityManager, collectionManager: CollectionManager, ownershipManager: OwnershipManager, requester: Requester, revueApiKey: str):
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenManager = tokenManager
        self.collectionManager = collectionManager
        self.ownershipManager = ownershipManager
        self.listingManager = listingManager
        self.attributeManager = attributeManager
        self.activityManager = activityManager
        self.blockManager = blockManager
        self.requester = requester
        self._tokenCache = {}
        with open("notd/sponsored_tokens.json", "r") as sponsoredTokensFile:
            sponsoredTokensDicts = json.loads(sponsoredTokensFile.read())
        self.revueApiKey = revueApiKey
        self.sponsoredTokens = [BaseSponsoredToken.from_dict(sponsoredTokenDict) for sponsoredTokenDict in sponsoredTokensDicts]

    async def get_sponsored_token(self) -> SponsoredToken:
        baseSponsoredToken = self.sponsoredTokens[0]
        currentDate = date_util.datetime_from_now()
        allPastTokens = [sponsoredToken for sponsoredToken in self.sponsoredTokens if sponsoredToken.date < currentDate]
        if allPastTokens:
            baseSponsoredToken = max(allPastTokens, key=lambda sponsoredToken: sponsoredToken.date)
        latestTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=baseSponsoredToken.token.registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=baseSponsoredToken.token.tokenId),
            ],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.DESCENDING)],
            limit=1
        )
        return SponsoredToken(date=baseSponsoredToken.date, token=baseSponsoredToken.token, latestTransfer=latestTransfers[0] if len(latestTransfers) > 0 else None)

    async def retrieve_highest_priced_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        highestPricedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(fieldName=BlocksTable.c.blockDate.key, gte=startDate, lt=endDate),
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, notContainedIn=_REGISTRY_BLACKLIST),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        return highestPricedTokenTransfers[0]

    async def retrieve_random_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        # NOTE(krishan711): this is no longer actually random, it's just the latest (random is too slow)
        randomTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=BlocksTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.DESCENDING)],
            offset=random.randint(1000, 10000),
            limit=1,
        )
        return randomTokenTransfers[0]

    async def get_transfer_count(self, startDate: datetime.datetime, endDate: datetime.datetime) ->int:
        query = (
            TokenTransfersTable.select()
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .with_only_columns([sqlalchemy.func.count()])
            .where(BlocksTable.c.blockDate >= startDate)
            .where(BlocksTable.c.blockDate < endDate)
        )
        result = await self.retriever.database.execute(query=query)
        count = result.scalar()
        return count

    async def retrieve_most_traded_token_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        query = (
            TokenTransfersTable.select()
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .with_only_columns([TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId, sqlalchemy.func.count()])
            .where(BlocksTable.c.blockDate >= startDate)
            .where(BlocksTable.c.blockDate < endDate)
            .where(TokenTransfersTable.c.registryAddress.notin_(_REGISTRY_BLACKLIST))
            .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
            .order_by(sqlalchemy.func.count().desc())
            .limit(1)
        )
        result = await self.retriever.database.execute(query=query)
        (registryAddress, tokenId, transferCount) = result.first()
        query = (
            sqlalchemy.select([TokenTransfersTable, BlocksTable])
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(BlocksTable.c.blockDate >= startDate)
            .where(BlocksTable.c.blockDate < endDate)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .where(TokenTransfersTable.c.tokenId == tokenId)
            .order_by(TokenTransfersTable.c.value.desc())
            .limit(1)
        )
        result = await self.retriever.database.execute(query=query)
        latestTransferRow = result.first()
        return TradedToken(
            latestTransfer=token_transfer_from_row(latestTransferRow),
            transferCount=transferCount,
        )

    async def get_collection_recent_sales(self, registryAddress: str, limit: int, offset: int) -> List[TokenTransfer]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                IntegerFieldFilter(fieldName=TokenTransfersTable.c.value.key, gt=0),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

    async def get_collection_recent_transfers(self, registryAddress: str, limit: int, offset: int, userAddress: Optional[str] = None) -> List[TokenTransfer]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        tokenTransfersQuery = (
            sqlalchemy.select(TokenTransfersTable, BlocksTable)
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .order_by(TokenTransfersTable.c.blockNumber.desc())
            .limit(limit)
            .offset(offset)
        )
        if userAddress:
            tokenTransfersQuery = tokenTransfersQuery.where(sqlalchemy.or_(TokenTransfersTable.c.toAddress == userAddress, TokenTransfersTable.c.fromAddress == userAddress))
        result = await self.retriever.database.execute(query=tokenTransfersQuery)
        tokenTransfers = [token_transfer_from_row(row) for row in result]
        return tokenTransfers

    async def get_collection_statistics(self, address: str) -> CollectionStatistics:
        address = chain_util.normalize_address(value=address)
        startDate = date_util.start_of_day()
        endDate = date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        holderCountQuery = (
            TokenOwnershipsTable.select()
            .with_only_columns([
                sqlalchemy.func.count(sqlalchemy.distinct(TokenOwnershipsTable.c.tokenId)),
                sqlalchemy.func.count(sqlalchemy.distinct(TokenOwnershipsTable.c.ownerAddress)),
            ])
            .where(TokenOwnershipsTable.c.registryAddress == address)
        )
        holderCountResult = await self.retriever.database.execute(query=holderCountQuery)
        (itemCount, holderCount) = holderCountResult.first()
        allActivityQuery = (
            CollectionHourlyActivityTable.select()
            .with_only_columns([
                sqlalchemy.func.sum(CollectionHourlyActivityTable.c.saleCount),
                sqlalchemy.func.sum(CollectionHourlyActivityTable.c.transferCount),
                sqlalchemy.func.sum(CollectionHourlyActivityTable.c.totalValue),
            ])
            .where(CollectionHourlyActivityTable.c.address == address)
        )
        allActivityResult = await self.retriever.database.execute(query=allActivityQuery)
        (saleCount, transferCount, totalTradeVolume) = allActivityResult.first()
        dayActivityQuery = (
            CollectionHourlyActivityTable.select()
            .with_only_columns([
                sqlalchemy.func.sum(CollectionHourlyActivityTable.c.totalValue),
                sqlalchemy.func.min(CollectionHourlyActivityTable.c.minimumValue),
                sqlalchemy.func.max(CollectionHourlyActivityTable.c.maximumValue),
            ])
            .where(CollectionHourlyActivityTable.c.address == address)
            .where(CollectionHourlyActivityTable.c.date >= startDate)
            .where(CollectionHourlyActivityTable.c.date < endDate)
        )
        dayActivityResult = await self.retriever.database.execute(query=dayActivityQuery)
        (tradeVolume24Hours, lowestSaleLast24Hours, highestSaleLast24Hours) = dayActivityResult.first()
        return CollectionStatistics(
            itemCount=itemCount,
            holderCount=holderCount,
            saleCount=saleCount or 0,
            transferCount=transferCount or 0,
            totalTradeVolume=totalTradeVolume or 0,
            lowestSaleLast24Hours=lowestSaleLast24Hours or 0,
            highestSaleLast24Hours=highestSaleLast24Hours or 0,
            tradeVolume24Hours=tradeVolume24Hours or 0,
        )

    async def get_collection_daily_activities(self, address: str) -> List[CollectionDailyActivity]:
        address = chain_util.normalize_address(address)
        endDate = date_util.datetime_from_now()
        startDate = date_util.datetime_from_datetime(dt=endDate, days=-90)
        collectionActivities = await self.retriever.list_collection_activities(fieldFilters=[
            StringFieldFilter(fieldName=CollectionHourlyActivityTable.c.address.key, eq=address),
            DateFieldFilter(fieldName=CollectionHourlyActivityTable.c.date.key, gte=startDate),
            DateFieldFilter(fieldName=CollectionHourlyActivityTable.c.date.key, lt=endDate),
        ])
        delta = datetime.timedelta(days=1)
        collectionActivitiesPerDay = []
        currentDate = startDate
        while date_util.start_of_day(currentDate) <= date_util.start_of_day(endDate):
            saleCount = 0
            totalValue = 0
            transferCount = 0
            minimumValue = 0
            maximumValue = 0
            for collectionActivity in collectionActivities:
                if date_util.start_of_day(currentDate) == date_util.start_of_day(collectionActivity.date):
                    if collectionActivity.saleCount > 0:
                        saleCount += collectionActivity.saleCount
                        totalValue += collectionActivity.totalValue
                        minimumValue = min(minimumValue, collectionActivity.minimumValue) if minimumValue > 0 else collectionActivity.minimumValue
                        maximumValue = max(maximumValue, collectionActivity.maximumValue)
                    transferCount += collectionActivity.transferCount
            averageValue = totalValue / saleCount if saleCount > 0 else 0
            collectionActivitiesPerDay.append(CollectionDailyActivity(date=currentDate, transferCount=transferCount, saleCount=saleCount, totalValue=totalValue, minimumValue=minimumValue, maximumValue=maximumValue, averageValue=averageValue))
            currentDate += delta
        return collectionActivitiesPerDay

    async def get_collection_token_recent_sales(self, registryAddress: str, tokenId: str, limit: int, offset: int) -> List[TokenTransfer]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
                IntegerFieldFilter(fieldName=TokenTransfersTable.c.value.key, gt=0),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

    async def get_collection_token_recent_transfers(self, registryAddress: str, tokenId: str, limit: int, offset: int) -> List[TokenTransfer]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

    async def list_account_tokens(self, accountAddress: str, limit: int, offset: int) -> List[Token]:
        tokenSingleOwnerships = await self.retriever.list_token_ownerships(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenOwnershipsTable.c.ownerAddress.key, eq=accountAddress),
            ],
            orders=[Order(fieldName=TokenOwnershipsTable.c.transferDate.key, direction=Direction.DESCENDING)],
            limit=limit+offset,
        )
        tokenMultiOwnerships = await self.retriever.list_token_multi_ownerships(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.ownerAddress.key, eq=accountAddress),
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.quantity.key, ne=0),
            ],
            orders=[Order(fieldName=TokenMultiOwnershipsTable.c.latestTransferDate.key, direction=Direction.DESCENDING)],
            limit=limit+offset,
        )
        tokenOwnershipTuples = [(ownership.registryAddress, ownership.tokenId, ownership.transferDate) for ownership in tokenSingleOwnerships]
        tokenOwnershipTuples += [(ownership.registryAddress, ownership.tokenId, ownership.latestTransferDate) for ownership in tokenMultiOwnerships]
        sortedTokenOwnershipTuples = sorted(tokenOwnershipTuples, key=lambda tuple: tuple[2], reverse=True)
        return [Token(registryAddress=registryAddress, tokenId=tokenId) for (registryAddress, tokenId, _) in sortedTokenOwnershipTuples]

    async def subscribe_email(self, email: str) -> None:
        await self.requester.post_json(url='https://www.getrevue.co/api/v2/subscribers', dataDict={'email': email.lower(), 'double_opt_in': False}, headers={'Authorization': f'Token {self.revueApiKey}'})

    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_ownership_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.ownershipManager.update_token_ownership_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_ownership(self, registryAddress: str, tokenId: str) -> None:
        await self.ownershipManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)
        await self.ownershipManager.update_token_ownership_deferred(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)
        await self.ownershipManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def update_collection_deferred(self, address: str, shouldForce: bool = False) -> None:
        await self.collectionManager.update_collection_deferred(address=address, shouldForce=shouldForce)

    async def update_collection(self, address: str, shouldForce: bool = False) -> None:
        await self.collectionManager.update_collection(address=address, shouldForce=shouldForce)

    async def update_collection_tokens_deferred(self, address: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_collection_tokens_deferred(address=address, shouldForce=shouldForce)

    async def update_collection_tokens(self, address: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_collection_tokens(address=address, shouldForce=shouldForce)

    async def update_activity_for_all_collections_deferred(self) -> None:
        await self.activityManager.update_activity_for_all_collections_deferred()

    async def update_activity_for_all_collections(self) -> None:
        await self.activityManager.update_activity_for_all_collections()

    async def update_activity_for_collection_deferred(self, registryAddress: str, startDate: datetime.datetime) -> None:
        await self.activityManager.update_activity_for_collection_deferred(registryAddress=registryAddress, startDate=startDate)

    async def update_activity_for_collection(self, address: str, startDate: datetime.datetime) -> None:
        await self.activityManager.update_activity_for_collection(address=address, startDate=startDate)

    async def update_token_attributes_for_all_collections_deferred(self) -> None:
        await self.attributeManager.update_token_attributes_for_all_collections_deferred()

    async def update_token_attributes_for_all_collections(self) -> None:
        await self.attributeManager.update_token_attributes_for_all_collections()

    async def update_collection_token_attributes_deferred(self, registryAddress: str, tokenId: str) -> None:
        await self.attributeManager.update_collection_token_attributes_deferred(registryAddress=registryAddress, tokenId=tokenId)

    async def update_collection_token_attributes(self, registryAddress: str, tokenId: str) -> None:
        await self.attributeManager.update_collection_token_attributes(registryAddress=registryAddress, tokenId=tokenId)

    async def update_latest_listings_for_all_collections_deferred(self, delaySeconds: int = 0) -> None:
        await self.listingManager.update_latest_listings_for_all_collections_deferred(delaySeconds=delaySeconds)

    async def update_latest_listings_for_all_collections(self) -> None:
        await self.listingManager.update_latest_listings_for_all_collections()

    async def update_latest_listings_for_collection_deferred(self, address: str, delaySeconds: int = 0) -> None:
        await self.listingManager.update_latest_listings_for_collection_deferred(address=address, delaySeconds=delaySeconds)

    async def update_latest_listings_for_collection(self, address: str) -> None:
        await self.listingManager.update_latest_listings_for_collection(address=address)

    async def get_collection_by_address(self, address: str) -> Collection:
        return await self.collectionManager.get_collection_by_address(address=address)

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str) -> TokenMetadata:
        return await self.tokenManager.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)

    async def list_collection_tokens(self, address: str) -> List[TokenMetadata]:
        return await self.tokenManager.list_collection_tokens(address=address)

    async def list_collection_tokens_by_owner(self, address: str, ownerAddress: str) -> List[Token]:
        address = chain_util.normalize_address(value=address)
        collection = await self.collectionManager.get_collection_by_address(address=address)
        return await self.ownershipManager.list_collection_tokens_by_owner(address=address, ownerAddress=ownerAddress, collection=collection)

    async def reprocess_owner_token_ownerships(self, accountAddress: str) -> None:
        collectionTokenIds = await self.ownershipManager.reprocess_owner_token_ownerships(ownerAddress=accountAddress)
        await self.tokenManager.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds)

    async def refresh_views_deferred(self) -> None:
        await self.workQueue.send_message(message=RefreshViewsMessageContent().to_message())

    async def refresh_views(self) -> None:
        async with self.saver.create_transaction() as connection:
            await connection.execute(sqlalchemy.text('REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_user_registry_first_ownerships;'))
        async with self.saver.create_transaction() as connection:
            await connection.execute(sqlalchemy.text('REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_user_registry_ordered_ownerships;'))

    async def receive_new_blocks_deferred(self) -> None:
        await self.blockManager.receive_new_blocks_deferred()

    async def receive_new_blocks(self) -> None:
        await self.blockManager.receive_new_blocks()

    async def reprocess_old_blocks_deferred(self) -> None:
        await self.blockManager.reprocess_old_blocks_deferred()

    async def reprocess_old_blocks(self) -> None:
        await self.blockManager.reprocess_old_blocks()

    async def process_blocks_deferred(self, blockNumbers: Sequence[int], shouldSkipProcessingTokens: Optional[bool] = None, delaySeconds: int = 0) -> None:
        await self.blockManager.process_blocks_deferred(blockNumbers=blockNumbers, shouldSkipProcessingTokens=shouldSkipProcessingTokens, delaySeconds=delaySeconds)

    async def process_block_deferred(self, blockNumber: int, shouldSkipProcessingTokens: Optional[bool] = None, delaySeconds: int = 0) -> None:
        await self.blockManager.process_block_deferred(blockNumber=blockNumber, shouldSkipProcessingTokens=shouldSkipProcessingTokens, delaySeconds=delaySeconds)

    async def process_block(self, blockNumber: int, shouldSkipProcessingTokens: Optional[bool] = None, shouldSkipUpdatingOwnerships: Optional[bool] = None) -> None:
        await self.blockManager.process_block(blockNumber=blockNumber, shouldSkipProcessingTokens=shouldSkipProcessingTokens, shouldSkipUpdatingOwnerships=shouldSkipUpdatingOwnerships)
