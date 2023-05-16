import datetime
import random
from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

import sqlalchemy
from core.exceptions import BadRequestException
from core.exceptions import InternalServerErrorException
from core.exceptions import NotFoundException
from core.queues.message_queue import MessageQueue
from core.queues.model import Message
from core.requester import Requester
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import FieldFilter
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from core.util import list_util
from sqlalchemy import Select
from sqlalchemy.sql import functions as sqlalchemyfunc

from notd.activity_manager import ActivityManager
from notd.attribute_manager import AttributeManager
from notd.badge_manager import BadgeManager
from notd.block_manager import BlockManager
from notd.collection_manager import CollectionManager
from notd.collection_overlap_manager import CollectionOverlapManager
from notd.delegation_manager import DelegationManager
from notd.listing_manager import ListingManager
from notd.messages import RefreshViewsMessageContent
from notd.model import BLUE_CHIP_COLLECTIONS
from notd.model import AccountToken
from notd.model import Collection
from notd.model import CollectionDailyActivity
from notd.model import CollectionStatistics
from notd.model import MintedTokenCount
from notd.model import OwnedCollection
from notd.model import Token
from notd.model import TokenListing
from notd.model import TokenMetadata
from notd.model import TokenMultiOwnership
from notd.model import TokenTransfer
from notd.model import TokenTransferValue
from notd.model import TradingHistory
from notd.model import TrendingCollection
from notd.model import UserTradingOverview
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenOwnershipsView
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_multi_ownership_from_row
from notd.store.schema_conversions import token_transfer_from_row
from notd.sub_collection_manager import SubCollectionManager
from notd.sub_collection_token_manager import SubCollectionTokenManager
from notd.token_manager import TokenManager
from notd.token_staking_manager import TokenStakingManager
from notd.twitter_manager import TwitterManager

_REGISTRY_BLACKLIST = {
    '0x58A3c68e2D3aAf316239c003779F71aCb870Ee47',  # Curve SynthSwap
    '0xFf488FD296c38a24CCcC60B43DD7254810dAb64e',  # zed.run
    '0xC36442b4a4522E871399CD717aBDD847Ab11FE88',  # uniswap-v3-positions
    '0xb9ed94c6d594b2517c4296e24a8c517ff133fb6d',  # hegic-eth-atm-calls-pool
    '0x1dfe7Ca09e99d10835Bf73044a23B73Fc20623DF',  # more loot
    '0x595A8974C1473717c4B5D456350Cd594d9bdA687',  # mineable punks
    '0x81Ae0bE3A8044772D04F32398bac1E1B4B215aa8',  # dreadfulz
    '0x46A15B0b27311cedF172AB29E4f4766fbE7F4364',  # pancake-v3-positions
}


class NotdManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: MessageQueue[Message], blockManager: BlockManager, tokenManager: TokenManager, listingManager: ListingManager, attributeManager: AttributeManager, activityManager: ActivityManager, collectionManager: CollectionManager, ownershipManager: OwnershipManager, collectionOverlapManager: CollectionOverlapManager, twitterManager: TwitterManager, badgeManager: BadgeManager, delegationManager: DelegationManager, tokenStakingManager: TokenStakingManager, requester: Requester, subCollectionTokenManager: SubCollectionTokenManager, subCollectionManager: SubCollectionManager, revueApiKey: str):
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenManager = tokenManager
        self.collectionManager = collectionManager
        self.ownershipManager = ownershipManager
        self.listingManager = listingManager
        self.tokenStakingManager = tokenStakingManager
        self.attributeManager = attributeManager
        self.activityManager = activityManager
        self.blockManager = blockManager
        self.badgeManager = badgeManager
        self.twitterManager = twitterManager
        self.delegationManager = delegationManager
        self.collectionOverlapManager = collectionOverlapManager
        self.subCollectionTokenManager = subCollectionTokenManager
        self.subCollectionManager = subCollectionManager
        self.requester = requester
        self.revueApiKey = revueApiKey

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
        tokenTransfers = [token_transfer_from_row(row) for row in result.mappings()]
        return tokenTransfers

    async def get_collection_transfers(self, registryAddress: str, minDate: Optional[datetime.datetime] = None, maxDate: Optional[datetime.datetime] = None, minValue: Optional[int] = None) -> List[TokenTransfer]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        tokenTransfersQuery = (
            sqlalchemy.select(TokenTransfersTable, BlocksTable)
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .order_by(TokenTransfersTable.c.blockNumber.desc())
        )
        if minDate:
            tokenTransfersQuery = tokenTransfersQuery.where(BlocksTable.c.blockDate >= minDate)
        if maxDate:
            tokenTransfersQuery = tokenTransfersQuery.where(BlocksTable.c.blockDate < maxDate)
        if minValue:
            tokenTransfersQuery = tokenTransfersQuery.where(TokenTransfersTable.c.value > 0)
        result = await self.retriever.database.execute(query=tokenTransfersQuery)
        tokenTransfers = [token_transfer_from_row(row) for row in result.mappings()]
        return tokenTransfers

    async def get_collection_token_transfer_values(self, registryAddress: str, minDate: Optional[datetime.datetime] = None, maxDate: Optional[datetime.datetime] = None, minValue: Optional[int] = None) -> List[TokenTransferValue]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        tokenTransfersQuery = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId, TokenTransfersTable.c.value, BlocksTable.c.blockDate)
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .order_by(TokenTransfersTable.c.blockNumber.desc())
        )
        if minDate:
            tokenTransfersQuery = tokenTransfersQuery.where(BlocksTable.c.blockDate >= minDate)
        if maxDate:
            tokenTransfersQuery = tokenTransfersQuery.where(BlocksTable.c.blockDate < maxDate)
        if minValue:
            tokenTransfersQuery = tokenTransfersQuery.where(TokenTransfersTable.c.value > 0)
        result = await self.retriever.database.execute(query=tokenTransfersQuery)
        tokenTransferValues = [TokenTransferValue(
            registryAddress=rowMapping[TokenTransfersTable.c.registryAddress],
            tokenId=rowMapping[TokenTransfersTable.c.tokenId],
            value=int(rowMapping[TokenTransfersTable.c.value]),
            blockDate=rowMapping[BlocksTable.c.blockDate],
        ) for rowMapping in result.mappings()]
        return tokenTransferValues

    async def get_collection_statistics(self, address: str) -> CollectionStatistics:
        address = chain_util.normalize_address(value=address)
        startDate = date_util.start_of_day()
        endDate = date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        holderCountQuery = (
            TokenOwnershipsTable.select()
            .with_only_columns(
                sqlalchemyfunc.count(sqlalchemy.distinct(TokenOwnershipsTable.c.tokenId)),  # type: ignore[no-untyped-call]
                sqlalchemyfunc.count(sqlalchemy.distinct(TokenOwnershipsTable.c.ownerAddress)),  # type: ignore[no-untyped-call]
            )
            .where(TokenOwnershipsTable.c.registryAddress == address)
        )
        holderCountResult = await self.retriever.database.execute(query=holderCountQuery)
        holderCountRow = holderCountResult.first()
        if not holderCountRow:
            raise NotFoundException()
        (itemCount, holderCount) = holderCountRow
        allActivityQuery: Select[Any] = (  # type: ignore[misc]
            CollectionHourlyActivitiesTable.select()
            .with_only_columns(
                sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.saleCount),  # type: ignore[no-untyped-call]
                sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.transferCount),  # type: ignore[no-untyped-call]
                sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.totalValue),  # type: ignore[no-untyped-call]
            )
            .where(CollectionHourlyActivitiesTable.c.address == address)
        )
        allActivityResult = await self.retriever.database.execute(query=allActivityQuery)
        allActivityRow = allActivityResult.first()
        if not allActivityRow:
            raise NotFoundException()
        (saleCount, transferCount, totalTradeVolume) = allActivityRow
        dayActivityQuery: Select[Any] = (  # type: ignore[misc]
            CollectionHourlyActivitiesTable.select()
            .with_only_columns(
                sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.totalValue),  # type: ignore[no-untyped-call]
                sqlalchemyfunc.min(CollectionHourlyActivitiesTable.c.minimumValue),  # type: ignore[no-untyped-call]
                sqlalchemyfunc.max(CollectionHourlyActivitiesTable.c.maximumValue),  # type: ignore[no-untyped-call]
            )
            .where(CollectionHourlyActivitiesTable.c.address == address)
            .where(CollectionHourlyActivitiesTable.c.date >= startDate)
            .where(CollectionHourlyActivitiesTable.c.date < endDate)
        )
        dayActivityResult = await self.retriever.database.execute(query=dayActivityQuery)
        dayActivityRow = dayActivityResult.first()
        if not dayActivityRow:
            raise NotFoundException()
        (tradeVolume24Hours, lowestSaleLast24Hours, highestSaleLast24Hours) = dayActivityRow
        return CollectionStatistics(
            itemCount=int(itemCount),
            holderCount=int(holderCount),
            saleCount=int(saleCount or 0),
            transferCount=int(transferCount or 0),
            totalTradeVolume=int(totalTradeVolume or 0),
            lowestSaleLast24Hours=int(lowestSaleLast24Hours or 0),
            highestSaleLast24Hours=int(highestSaleLast24Hours or 0),
            tradeVolume24Hours=int(tradeVolume24Hours or 0),
        )

    async def get_collection_daily_activities(self, address: str) -> List[CollectionDailyActivity]:
        address = chain_util.normalize_address(address)
        endDate = date_util.datetime_from_now()
        startDate = date_util.datetime_from_datetime(dt=endDate, days=-90)
        collectionActivities = await self.retriever.list_collection_activities(fieldFilters=[
            StringFieldFilter(fieldName=CollectionHourlyActivitiesTable.c.address.key, eq=address),
            DateFieldFilter(fieldName=CollectionHourlyActivitiesTable.c.date.key, gte=startDate),
            DateFieldFilter(fieldName=CollectionHourlyActivitiesTable.c.date.key, lt=endDate),
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
            averageValue = int(totalValue / saleCount) if saleCount > 0 else 0
            collectionActivitiesPerDay.append(CollectionDailyActivity(date=currentDate, transferCount=transferCount, saleCount=saleCount, totalValue=totalValue, minimumValue=minimumValue, maximumValue=maximumValue, averageValue=averageValue))
            currentDate += delta
        return collectionActivitiesPerDay

    async def get_collection_token_recent_sales(self, registryAddress: str, tokenId: str, limit: int, offset: int) -> List[TokenTransfer]:
        return await self.get_collection_token_recent_transfers(registryAddress=registryAddress, tokenId=tokenId, limit=limit, offset=offset, shouldIncludeSalesOnly=True)

    async def get_collection_token_recent_transfers(self, registryAddress: str, tokenId: str, limit: int, offset: int, shouldIncludeSalesOnly: bool = False) -> List[TokenTransfer]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        filters: List[FieldFilter] = [
            StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
            StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
        ]
        if shouldIncludeSalesOnly:
            filters.append(IntegerFieldFilter(fieldName=TokenTransfersTable.c.value.key, gt=0))
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=filters,
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

    async def get_collection_token_owners(self, registryAddress: str, tokenId: str) -> List[TokenMultiOwnership]:
        query = (
            TokenOwnershipsView.select()
            .where(TokenOwnershipsView.c.registryAddress == registryAddress)
            .where(TokenOwnershipsView.c.tokenId == tokenId)
            .where(TokenOwnershipsView.c.quantity > 0)
            .order_by(TokenOwnershipsView.c.quantity.desc())
        )
        result = await self.retriever.database.execute(query=query)
        tokenOwnerships = [token_multi_ownership_from_row(row) for row in result.mappings()]
        return tokenOwnerships

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
                IntegerFieldFilter(fieldName=TokenMultiOwnershipsTable.c.quantity.key, ne=0),
            ],
            orders=[Order(fieldName=TokenMultiOwnershipsTable.c.latestTransferDate.key, direction=Direction.DESCENDING)],
            limit=limit+offset,
        )
        tokenOwnershipTuples = [(ownership.registryAddress, ownership.tokenId, ownership.transferDate) for ownership in tokenSingleOwnerships]
        tokenOwnershipTuples += [(ownership.registryAddress, ownership.tokenId, ownership.latestTransferDate) for ownership in tokenMultiOwnerships]
        sortedTokenOwnershipTuples = sorted(tokenOwnershipTuples, key=lambda tuple: tuple[2], reverse=True)
        return [Token(registryAddress=registryAddress, tokenId=tokenId) for (registryAddress, tokenId, _) in sortedTokenOwnershipTuples]

    async def list_account_delegated_tokens(self, accountAddress: str, limit: int, offset: int) -> List[AccountToken]:
        delegations = await self.delegationManager.get_delegations(delegateAddress=accountAddress)
        accountTokens = []
        for delegation in delegations:
            tokens = await self.list_account_tokens(accountAddress=delegation.vaultAddress, limit=limit, offset=offset)
            if delegation.delegationType == "ALL":
                accountTokens += [AccountToken(registryAddress=token.registryAddress, tokenId=token.tokenId, ownerAddress=delegation.vaultAddress) for token in tokens]
            if delegation.delegationType == "CONTRACT":
                accountTokens += [AccountToken(registryAddress=token.registryAddress, tokenId=token.tokenId, ownerAddress=delegation.vaultAddress) for token in tokens if delegation.contractAddress == token.registryAddress]
            if delegation.delegationType == "TOKEN":
                #NOTE(Femi-Ogunkola): registryAddress=delegation.contractAddress, tokenId=delegation.tokenId but typing error with Optional[str]
                accountTokens += [AccountToken(registryAddress=token.registryAddress, tokenId=token.tokenId, ownerAddress=delegation.vaultAddress) for token in tokens if delegation.contractAddress == token.registryAddress and delegation.tokenId == token.tokenId]
        query = (
            TokenOwnershipsView.select()
            .where(TokenOwnershipsView.c.ownerAddress == accountAddress)
            .where(TokenOwnershipsView.c.quantity > 0)
            .order_by(TokenOwnershipsView.c.latestTransferDate.desc())
            .offset(offset=offset)
            .limit(limit=limit+offset)
        )
        result = await self.retriever.database.execute(query=query)
        tokenOwnerships = [token_multi_ownership_from_row(row) for row in result.mappings()]
        tokenOwnershipTuples = [(ownership.registryAddress, ownership.tokenId, ownership.ownerAddress, ownership.latestTransferDate) for ownership in tokenOwnerships]
        sortedTokenOwnershipTuples = sorted(tokenOwnershipTuples, key=lambda tuple: tuple[3], reverse=True)
        accountTokens += [AccountToken(registryAddress=registryAddress, tokenId=tokenId, ownerAddress=ownerAddress) for (registryAddress, tokenId, ownerAddress, _) in sortedTokenOwnershipTuples]
        return accountTokens

    async def calculate_common_owners(self, registryAddresses: List[str], tokenIds: List[str], date: Optional[datetime.datetime] = None) -> List[str]:
        ownershipCountsMap: Dict[str, List[int]] = defaultdict(lambda: [0] * (len(registryAddresses)))
        for index, _ in enumerate(registryAddresses):
            collection = await self.collectionManager.get_collection_by_address(address=registryAddresses[index])
            if collection.doesSupportErc721:
                singleOwnership = await self.ownershipManager.tokenOwnershipProcessor.calculate_token_single_ownership(registryAddress=registryAddresses[index], tokenId=tokenIds[index], date=date)
                ownershipCountsMap[singleOwnership.ownerAddress][index] = 1
            elif collection.doesSupportErc1155:
                ownerships = await self.ownershipManager.tokenOwnershipProcessor.calculate_token_multi_ownership(registryAddress=registryAddresses[index], tokenId=tokenIds[index], date=date)
                for multiOwnership in ownerships:
                    if multiOwnership.quantity > 0:
                        ownershipCountsMap[multiOwnership.ownerAddress][index] = multiOwnership.quantity
            else:
                raise InternalServerErrorException('Failed to calculate ownership for non-ERC721/ERC1155 collection')
        ownershipMinimumsMap = {ownerAddress: min(ownershipCounts) for ownerAddress, ownershipCounts in ownershipCountsMap.items()}
        filteredOwnershipMinimumsMap = {ownerAddress: ownershipMinimum for ownerAddress, ownershipMinimum in ownershipMinimumsMap.items() if ownershipMinimum > 0}
        return list(filteredOwnershipMinimumsMap.keys())

    async def list_all_listings_for_collection_token(self, registryAddress: str, tokenId: str) -> List[TokenListing]:
        return await self.listingManager.list_all_listings_for_collection_token(registryAddress=registryAddress, tokenId=tokenId)

    async def subscribe_email(self, email: str) -> None:
        await self.requester.post_json(url='https://www.getrevue.co/api/v2/subscribers', dataDict={'email': email.lower(), 'double_opt_in': False}, headers={'Authorization': f'Token {self.revueApiKey}'})

    async def retrieve_trending_collections(self, currentDate: Optional[datetime.datetime], duration: Optional[str] = None, limit: Optional[int] = None, order: Optional[str] = None) -> List[TrendingCollection]:
        currentDate = currentDate or date_util.datetime_from_now()
        limit = limit or 9
        if duration == '12_HOURS' or duration is None:
            startDate = date_util.datetime_from_datetime(dt=currentDate, hours=-12)
            previousPeriodStartDate = date_util.datetime_from_datetime(dt=startDate, hours=-12)
        elif duration == '24_HOURS':
            startDate = date_util.datetime_from_datetime(dt=currentDate, hours=-24)
            previousPeriodStartDate = date_util.datetime_from_datetime(dt=startDate, hours=-24)
        elif duration == "7_DAYS":
            startDate = date_util.datetime_from_datetime(dt=currentDate, days=-7)
            previousPeriodStartDate = date_util.datetime_from_datetime(dt=startDate, days=-7)
        elif duration == '30_DAYS':
            startDate = date_util.datetime_from_datetime(dt=currentDate, days=-30)
            previousPeriodStartDate = date_util.datetime_from_datetime(dt=startDate, days=-30)
        else:
            raise BadRequestException('Unknown duration')
        query = (
            sqlalchemy.select(CollectionHourlyActivitiesTable.c.address, sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.saleCount).label('totalSalesCount'), sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.totalValue).label('totalTransferCount')) # type: ignore[no-untyped-call, var-annotated]
            .where(CollectionHourlyActivitiesTable.c.date >= startDate)
            .where(CollectionHourlyActivitiesTable.c.date < currentDate)
            .where(CollectionHourlyActivitiesTable.c.address.not_in(list(_REGISTRY_BLACKLIST)))
            .group_by(CollectionHourlyActivitiesTable.c.address)
        )
        if order is None or order == "TOTAL_VALUE":
            query = query.order_by(sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.totalValue).desc()) # type: ignore[no-untyped-call]
        elif order == "TOTAL_SALES":
            query = query.order_by(sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.saleCount).desc()) # type: ignore[no-untyped-call]
        query = query.limit(limit)
        result = await self.retriever.database.execute(query=query)
        trendingCollectionRows = list(result.mappings())
        currentTrendingCollections = {trendingCollectionRow['address']: (int(trendingCollectionRow['totalSalesCount']), int(trendingCollectionRow['totalTransferCount'])) for trendingCollectionRow in trendingCollectionRows}
        addresses = list(currentTrendingCollections.keys())
        previousPeriodQuery = (
            sqlalchemy.select(CollectionHourlyActivitiesTable.c.address, sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.saleCount).label('totalSalesCount'), sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.totalValue).label('totalTransferCount')) # type: ignore[no-untyped-call, var-annotated]
            .where(CollectionHourlyActivitiesTable.c.date >= previousPeriodStartDate)
            .where(CollectionHourlyActivitiesTable.c.date < startDate)
            .where(CollectionHourlyActivitiesTable.c.address.in_(addresses))
            .group_by(CollectionHourlyActivitiesTable.c.address)
        )
        previousPeriodResult = await self.retriever.database.execute(query=previousPeriodQuery)
        previousPeriod = list(previousPeriodResult.mappings())
        previousPeriodValues = {previousPeriodRow['address']: (int(previousPeriodRow['totalSalesCount']), int(previousPeriodRow['totalTransferCount'])) for previousPeriodRow in previousPeriod}
        #NOTE(Femi-Ogunkola): Find better way to handle non-existent previousSaleCount and previousTotalCount
        trendingCollections = [
            TrendingCollection(
                registryAddress=address,
                totalSaleCount=totalSaleCount,
                totalVolume=totalVolume,
                previousSaleCount=previousPeriodValues[address][0] if previousPeriodValues.get(address) else 0,
                previousTotalVolume=previousPeriodValues[address][1] if previousPeriodValues.get(address) else 0,
            ) for address, (totalSaleCount, totalVolume) in currentTrendingCollections.items()
        ]
        return trendingCollections

    async def retrieve_minted_token_counts(self, currentDate: Optional[datetime.datetime] = None, duration: Optional[str] = None) -> List[MintedTokenCount]:
        currentDate = currentDate or date_util.datetime_from_now()
        currentDate = date_util.date_hour_from_datetime(dt=currentDate)
        validDates: List[Union[datetime.datetime, datetime.date]]
        if duration == '12_HOURS':
            date = CollectionHourlyActivitiesTable.c.date.label('date')
            startDate = date_util.datetime_from_datetime(dt=currentDate, hours=-12)
            dateIntervals = list(date_util.generate_hourly_intervals(startDate=startDate, endDate=currentDate))
            validDates = [time for time, _ in dateIntervals]
        elif duration == '24_HOURS':
            date = CollectionHourlyActivitiesTable.c.date.label('date')
            startDate = date_util.datetime_from_datetime(dt=currentDate, hours=-24)
            dateIntervals = list(date_util.generate_hourly_intervals(startDate=startDate, endDate=currentDate))
            validDates = [time for time, _ in dateIntervals]
        elif duration is None or duration == "7_DAYS":
            date = sqlalchemy.cast(CollectionHourlyActivitiesTable.c.date, sqlalchemy.DATE).label('date')
            startDate = date_util.datetime_from_datetime(dt=currentDate, days=-7)
            validDates = list(date_util.generate_dates_in_range(startDate=startDate, endDate=currentDate, days=1, shouldIncludeEndDate=True))
        elif duration == '30_DAYS':
            date = sqlalchemy.cast(CollectionHourlyActivitiesTable.c.date, sqlalchemy.DATE).label('date')
            startDate = date_util.datetime_from_datetime(dt=currentDate, days=-30)
            validDates = list(date_util.generate_dates_in_range(startDate=startDate, endDate=currentDate, days=1, shouldIncludeEndDate=True))
        elif duration == '90_DAYS':
            date = sqlalchemy.cast(CollectionHourlyActivitiesTable.c.date, sqlalchemy.DATE).label('date')
            startDate = date_util.datetime_from_datetime(dt=currentDate, days=-90)
            validDates = list(date_util.generate_dates_in_range(startDate=startDate, endDate=currentDate, days=1, shouldIncludeEndDate=True))
        elif duration == '180_DAYS':
            date = sqlalchemy.cast(CollectionHourlyActivitiesTable.c.date, sqlalchemy.DATE).label('date')
            startDate = date_util.datetime_from_datetime(dt=currentDate, days=-180)
            validDates = list(date_util.generate_dates_in_range(startDate=startDate, endDate=currentDate, days=1, shouldIncludeEndDate=True))
        else:
            raise BadRequestException('Unknown duration')
        query = (
            sqlalchemy.select(date, sqlalchemyfunc.count(CollectionHourlyActivitiesTable.c.address.distinct()).label('mintedTokenCount'), sqlalchemyfunc.count(CollectionHourlyActivitiesTable.c.address.distinct()).label('newRegistryCount')) # type: ignore[no-untyped-call]
            .where(CollectionHourlyActivitiesTable.c.date <= currentDate)
            .where(CollectionHourlyActivitiesTable.c.date >= startDate)
            .group_by(date)
            .order_by(date.desc())
        )
        result = await self.retriever.database.execute(query=query)
        dateCountDict = {dateCount['date']: (dateCount['mintedTokenCount'], dateCount['newRegistryCount']) for dateCount in result.mappings()}
        mintedTokenCounts: List[MintedTokenCount] = []
        for validDate in validDates:
            validDatetime = datetime.datetime.combine(validDate, datetime.datetime.min.time()) if not isinstance(validDate, datetime.datetime) else validDate
            if validDate in dateCountDict.keys():
                mintedTokenCounts += [MintedTokenCount(date=validDatetime, mintedTokenCount=dateCountDict[validDate][0], newRegistryCount=dateCountDict[validDate][1])]
            else:
                mintedTokenCounts += [MintedTokenCount(date=validDatetime, mintedTokenCount=0, newRegistryCount=0)]
        return mintedTokenCounts

    async def retrieve_hero_tokens(self, currentDate: Optional[datetime.datetime] = None, limit: Optional[int] = None) -> List[Token]:
        currentDate = currentDate.replace(tzinfo=None) if currentDate else None
        currentDate = date_util.start_of_day(dt=currentDate)
        limit = limit if limit else 10
        highestValueAddressesQuery = (
            sqlalchemy.select(CollectionHourlyActivitiesTable.c.address)
            .where(CollectionHourlyActivitiesTable.c.date >= date_util.datetime_from_datetime(dt=currentDate, days=-1))
            .where(CollectionHourlyActivitiesTable.c.date <= currentDate)
            .where(CollectionHourlyActivitiesTable.c.address.not_in(list(_REGISTRY_BLACKLIST)))
            .group_by(CollectionHourlyActivitiesTable.c.address)
            .order_by(sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.totalValue).desc()) # type: ignore[no-untyped-call]
            .limit(int(limit / 2))
        )
        highestValueAddressesResult = await self.retriever.database.execute(query=highestValueAddressesQuery)
        heroAddresses = [row['address'] for row in list(highestValueAddressesResult.mappings())]
        newlyMintedAddressSubQuery = (
            sqlalchemy.select(CollectionHourlyActivitiesTable.c.address)
            .where(CollectionHourlyActivitiesTable.c.date >= date_util.datetime_from_datetime(dt=currentDate, days=-1))
            .where(CollectionHourlyActivitiesTable.c.date <= currentDate)
            .where(CollectionHourlyActivitiesTable.c.address.not_in(list(_REGISTRY_BLACKLIST)))
            .where(CollectionHourlyActivitiesTable.c.mintCount > 0)
            .group_by(CollectionHourlyActivitiesTable.c.address)
            .order_by(sqlalchemyfunc.sum(CollectionHourlyActivitiesTable.c.totalValue).desc()) # type: ignore[no-untyped-call]
            .limit(int(limit / 2))
        )
        newlyMintedAddressResult = await self.retriever.database.execute(query=newlyMintedAddressSubQuery)
        heroAddresses += [row['address'] for row in list(newlyMintedAddressResult.mappings())]
        query = (
            sqlalchemy.select(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId)
            .where(TokenMetadatasTable.c.registryAddress == heroAddresses[0])
            .offset(random.randint(1, 15))
            .limit(1)
        )
        for heroAddress in heroAddresses[1:]:
            randomTokenQuery = (
                sqlalchemy.select(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId)
                .where(TokenMetadatasTable.c.registryAddress == heroAddress)
                .offset(random.randint(1, 15))
                .limit(1)
            )
            query = randomTokenQuery.union(query) # type: ignore[assignment]
        result = await self.retriever.database.execute(query=query)
        tokens = [Token(registryAddress=row['registryAddress'], tokenId=row['tokenId']) for row in result.mappings()]
        return tokens

    async def list_user_owned_collections(self, userAddress: str) -> List[OwnedCollection]:
        collectionsQuery = (
            sqlalchemy.select(TokenOwnershipsView)
                .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenOwnershipsView.c.registryAddress)
                .where(TokenOwnershipsView.c.ownerAddress == userAddress)
                .where(TokenOwnershipsView.c.quantity > 0)
                .order_by(CollectionTotalActivitiesTable.c.totalValue.desc(), TokenOwnershipsView.c.latestTransferDate.asc())
        )
        collectionsResult = await self.retriever.database.execute(query=collectionsQuery)
        collectionTokenIds = [(row[TokenOwnershipsView.c.registryAddress], row[TokenOwnershipsView.c.tokenId]) for row in collectionsResult.mappings()]
        registryAddresses = list(dict.fromkeys([collectionTokenId[0] for collectionTokenId in collectionTokenIds]))
        collections = await self.retriever.list_collections(fieldFilters=[StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, containedIn=registryAddresses)])
        collectionMap = {collection.address: collection for collection in collections}
        collectionTokenMap: Dict[str, List[TokenMetadata]] = defaultdict(list)
        for chunkedCollectionTokenIds in list_util.generate_chunks(lst=list(collectionTokenIds), chunkSize=1000):
            tokensQuery = (
                TokenMetadatasTable.select()
                    .where(sqlalchemy.tuple_(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId).in_(chunkedCollectionTokenIds))
            )
            tokens = await self.retriever.query_token_metadatas(query=tokensQuery)
            for token in tokens:
                collectionTokenMap[token.registryAddress].append(token)
        return [
            OwnedCollection(
                collection=collectionMap[registryAddress],
                tokenMetadatas=collectionTokenMap[registryAddress],
            ) for registryAddress in registryAddresses
        ]

    async def list_user_recent_transfers(self, userAddress: str, limit: int, offset: int) -> List[TokenTransfer]:
        userAddress = chain_util.normalize_address(value=userAddress)
        tokenTransfersQuery = (
            sqlalchemy.select(TokenTransfersTable, BlocksTable)
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(sqlalchemy.or_(TokenTransfersTable.c.toAddress == userAddress, TokenTransfersTable.c.fromAddress == userAddress))
            .order_by(TokenTransfersTable.c.blockNumber.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.retriever.database.execute(query=tokenTransfersQuery)
        tokenTransfers = [token_transfer_from_row(row) for row in result.mappings()]
        return tokenTransfers

    async def list_user_trading_histories(self, userAddress: str, offset: int) -> List[TradingHistory]:
        currentDate = date_util.datetime_from_now()
        userAddress = chain_util.normalize_address(value=userAddress)
        tokenTransfersQuery = (
            sqlalchemy.select(sqlalchemy.cast(BlocksTable.c.blockDate, sqlalchemy.DATE).label('date'), TokenTransfersTable,)
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(sqlalchemy.or_(TokenTransfersTable.c.toAddress == userAddress, TokenTransfersTable.c.fromAddress == userAddress))
            .where(BlocksTable.c.blockDate <= currentDate)
            .where(BlocksTable.c.blockDate >= date_util.datetime_from_datetime(dt=currentDate, weeks=-52))
            .group_by(sqlalchemy.cast(BlocksTable.c.blockDate, sqlalchemy.DATE).label('date'), TokenTransfersTable.c)
            .order_by(sqlalchemy.cast(BlocksTable.c.blockDate, sqlalchemy.DATE).label('date').desc())
            .offset(offset)
        )
        result = await self.retriever.database.execute(query=tokenTransfersQuery)
        transferRow = (list(result.mappings()))
        dateBuyCountDict: Dict[datetime.date, int] = defaultdict(int)
        dateSellCountDict: Dict[datetime.date, int] = defaultdict(int)
        dateMintCountDict: Dict[datetime.date, int] = defaultdict(int)
        dateTransferCountDict: Dict[datetime.date, int] = defaultdict(int)
        for row in transferRow:
            dateBuyCountDict[row['date']] += 1 if (row['toAddress'] == userAddress and row['value'] > 0) else 0
            dateSellCountDict[row['date']] += 1 if (row['fromAddress'] == userAddress and row['value'] > 0) else 0
            dateMintCountDict[row['date']] += 1 if row['fromAddress'] == chain_util.BURN_ADDRESS else 0
            dateTransferCountDict[row['date']] += 1 if (userAddress in (row['fromAddress'], row['toAddress']) and row['value'] == 0) else 0
        tradingHistories = [
            TradingHistory(
                date=date,
                buyCount=buyCount,
                transferCount=dateTransferCountDict[date],
                sellCount=dateSellCountDict[date],
                mintCount=dateMintCountDict[date],
            ) for date, buyCount in dateBuyCountDict.items()]
        return tradingHistories

    async def list_user_blue_chip_owned_collections(self, userAddress: str) -> List[OwnedCollection]:
        collectionsQuery = (
            sqlalchemy.select(TokenOwnershipsView)
                .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenOwnershipsView.c.registryAddress)
                .where(TokenOwnershipsView.c.ownerAddress == userAddress)
                .where(TokenOwnershipsView.c.quantity > 0)
                .where(TokenOwnershipsView.c.registryAddress.in_(BLUE_CHIP_COLLECTIONS))
                .order_by(CollectionTotalActivitiesTable.c.totalValue.desc(), TokenOwnershipsView.c.latestTransferDate.asc())
        )
        collectionsResult = await self.retriever.database.execute(query=collectionsQuery)
        collectionTokenIds = [(row[TokenOwnershipsView.c.registryAddress], row[TokenOwnershipsView.c.tokenId]) for row in collectionsResult.mappings()]
        registryAddresses = list(dict.fromkeys([collectionTokenId[0] for collectionTokenId in collectionTokenIds]))
        collections = await self.retriever.list_collections(fieldFilters=[StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, containedIn=registryAddresses)])
        collectionMap = {collection.address: collection for collection in collections}
        collectionTokenMap: Dict[str, List[TokenMetadata]] = defaultdict(list)
        for chunkedCollectionTokenIds in list_util.generate_chunks(lst=list(collectionTokenIds), chunkSize=1000):
            tokensQuery = (
                TokenMetadatasTable.select()
                    .where(sqlalchemy.tuple_(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId).in_(chunkedCollectionTokenIds))
            )
            tokens = await self.retriever.query_token_metadatas(query=tokensQuery)
            for token in tokens:
                collectionTokenMap[token.registryAddress].append(token)
        return [
            OwnedCollection(
                collection=collectionMap[registryAddress],
                tokenMetadatas=collectionTokenMap[registryAddress],
            ) for registryAddress in registryAddresses
        ]

    async def get_user_trading_overview(self, userAddress: str) -> UserTradingOverview:
        #NOTE(Femi-Ogunkola): Please confirm if using one query is the better option
        mostTradedQuery = (
            sqlalchemy.select(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
            .where(sqlalchemy.or_(TokenTransfersTable.c.toAddress == userAddress, TokenTransfersTable.c.fromAddress == userAddress))
            .group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
            .order_by(sqlalchemyfunc.count(TokenTransfersTable.c.tokenId).desc()) # type: ignore[no-untyped-call]
            .limit(1)
        )
        mostTradedResult = await self.retriever.database.execute(query=mostTradedQuery)
        mostTradedTokens = [Token(registryAddress=row['registryAddress'], tokenId=row['tokenId']) for row in mostTradedResult.mappings()]
        mostTradedToken = mostTradedTokens[0] if len(mostTradedTokens) > 0 else None
        highestSoldTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.fromAddress.key, eq=userAddress)
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        highestSoldTokenTransfer = highestSoldTokenTransfers[0] if len(highestSoldTokenTransfers) else None
        highestBoughtTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=userAddress)
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        highestBoughtTokenTransfer = highestBoughtTokenTransfers[0] if len(highestBoughtTokenTransfers) else None
        mostRecentlyMintedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=userAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.fromAddress.key, eq=chain_util.BURN_ADDRESS),
            ],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.DESCENDING)],
            limit=1
        )
        mostRecentlyMintedTokenTransfer = mostRecentlyMintedTokenTransfers[0] if len(mostRecentlyMintedTokenTransfers) else None
        userTradingOverview = UserTradingOverview(mostTradedToken=mostTradedToken, highestSoldTokenTransfer=highestSoldTokenTransfer, highestBoughtTokenTransfer=highestBoughtTokenTransfer, mostRecentlyMintedTokenTransfer=mostRecentlyMintedTokenTransfer)
        return userTradingOverview

    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: Optional[bool] = False) -> None:
        await self.tokenManager.update_token_metadata_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: Optional[bool] = False) -> None:
        # await self.tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)
        await self.subCollectionTokenManager.update_sub_collection_token(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token_ownership_deferred(self, registryAddress: str, tokenId: str) -> None:
        await self.ownershipManager.update_token_ownership_deferred(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token_ownership(self, registryAddress: str, tokenId: str) -> None:
        await self.ownershipManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token_deferred(self, registryAddress: str, tokenId: str, shouldForce: Optional[bool] = False) -> None:
        await self.tokenManager.update_token_metadata_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)
        await self.ownershipManager.update_token_ownership_deferred(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token(self, registryAddress: str, tokenId: str, shouldForce: Optional[bool] = False) -> None:
        await self.tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)
        await self.ownershipManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def update_collection_deferred(self, address: str, shouldForce: Optional[bool] = False) -> None:
        await self.collectionManager.update_collection_deferred(address=address, shouldForce=shouldForce)

    async def update_collection(self, address: str, shouldForce: Optional[bool] = False) -> None:
        await self.collectionManager.update_collection(address=address, shouldForce=shouldForce)

    async def update_collection_tokens_deferred(self, address: str, shouldForce: Optional[bool] = False) -> None:
        await self.tokenManager.update_collection_tokens_deferred(address=address, shouldForce=shouldForce)

    async def update_collection_tokens(self, address: str, shouldForce: Optional[bool] = False) -> None:
        await self.tokenManager.update_collection_tokens(address=address, shouldForce=shouldForce)

    async def update_activity_for_all_collections_deferred(self) -> None:
        await self.activityManager.update_activity_for_all_collections_deferred()

    async def update_activity_for_all_collections(self) -> None:
        await self.activityManager.update_activity_for_all_collections()

    async def update_activity_for_collection_deferred(self, address: str, startDate: datetime.datetime) -> None:
        await self.activityManager.update_activity_for_collection_deferred(address=address, startDate=startDate)

    async def update_activity_for_collection(self, address: str, startDate: datetime.datetime) -> None:
        await self.activityManager.update_activity_for_collection(address=address, startDate=startDate)

    async def update_total_activity_for_collection(self, address: str) -> None:
        await self.activityManager.update_total_activity_for_collection(address=address)

    async def update_total_activity_for_all_collections_deferred(self) -> None:
        await self.activityManager.update_total_activity_for_all_collections_deferred()

    async def update_total_activity_for_all_collections(self, shouldDeferWork: Optional[bool] = True) -> None:
        await self.activityManager.update_total_activity_for_all_collections(shouldDeferWork=shouldDeferWork)

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

    async def refresh_latest_listings_for_all_collections_deferred(self, delaySeconds: int = 0) -> None:
        await self.listingManager.refresh_latest_listings_for_all_collections_deferred(delaySeconds=delaySeconds)

    async def refresh_latest_listings_for_all_collections(self) -> None:
        await self.listingManager.refresh_latest_listings_for_all_collections()

    async def refresh_latest_listings_for_collection_deferred(self, address: str, delaySeconds: int = 0) -> None:
        await self.listingManager.refresh_latest_listings_for_collection_deferred(address=address, delaySeconds=delaySeconds)

    async def refresh_latest_listings_for_collection(self, address: str) -> None:
        await self.listingManager.refresh_latest_listings_for_collection(address=address)

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

    async def reprocess_owner_token_ownerships(self, userAddress: str) -> None:
        collectionTokenIds = await self.ownershipManager.reprocess_owner_token_ownerships(ownerAddress=userAddress)
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

    async def process_block(self, blockNumber: int, shouldSkipProcessingTokens: Optional[bool] = None, shouldSkipUpdatingOwnerships: Optional[bool] = None, shouldSkipUpdatingStakings: Optional[bool] = None) -> None:
        await self.blockManager.process_block(blockNumber=blockNumber, shouldSkipProcessingTokens=shouldSkipProcessingTokens, shouldSkipUpdatingOwnerships=shouldSkipUpdatingOwnerships, shouldSkipUpdatingStakings=shouldSkipUpdatingStakings)

    async def update_all_twitter_users_deferred(self) -> None:
        await self.twitterManager.update_all_twitter_users_deferred()

    async def update_all_twitter_users(self) -> None:
        await self.twitterManager.update_all_twitter_users()

    async def refresh_overlap_for_collection(self, registryAddress: str) -> None:
        await self.collectionOverlapManager.refresh_overlap_for_collection(registryAddress=registryAddress)

    async def refresh_overlap_for_collection_deferred(self, registryAddress: str) -> None:
        await self.collectionOverlapManager.refresh_overlap_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_overlaps_for_all_collections_deferred(self) -> None:
        await self.collectionOverlapManager.refresh_overlaps_for_all_collections_deferred()

    async def refresh_overlaps_for_all_collections(self) -> None:
        await self.collectionOverlapManager.refresh_overlaps_for_all_collections()

    async def refresh_gallery_badge_holders_for_collection(self, registryAddress: str) -> None:
        await self.badgeManager.refresh_gallery_badge_holders_for_collection(registryAddress=registryAddress)

    async def refresh_gallery_badge_holders_for_collection_deferred(self, registryAddress: str) -> None:
        await self.badgeManager.refresh_gallery_badge_holders_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_gallery_badge_holders_for_all_collections_deferred(self) -> None:
        await self.badgeManager.refresh_gallery_badge_holders_for_all_collections_deferred()

    async def refresh_gallery_badge_holders_for_all_collections(self) -> None:
        await self.badgeManager.refresh_gallery_badge_holders_for_all_collections()

    async def update_token_stakings_for_all_collections_deferred(self) -> None:
        await self.tokenStakingManager.update_token_stakings_for_all_collections_deferred()

    async def update_token_stakings_for_collection(self, registryAddress: str) -> None:
        await self.tokenStakingManager.update_token_stakings_for_collection(address=registryAddress)

    async def update_token_staking_deferred(self, registryAddress: str, tokenId: str) -> None:
        await self.tokenStakingManager.update_token_staking_deferred(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token_staking(self, registryAddress: str, tokenId: str) -> None:
        await self.tokenStakingManager.update_token_staking(registryAddress=registryAddress, tokenId=tokenId)

    async def update_sub_collection_deferred(self, registryAddress: str, externalId: str) -> None:
        await self.subCollectionManager.update_sub_collection_deferred(registryAddress=registryAddress, externalId=externalId)

    async def update_sub_collection(self, registryAddress: str, externalId: str) -> None:
        await self.subCollectionManager.update_sub_collection(registryAddress=registryAddress, externalId=externalId)
