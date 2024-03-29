import asyncio
import json
from typing import Any
from typing import AsyncGenerator
from typing import List
from typing import Optional

import sqlalchemy
from core.exceptions import NotFoundException
from core.util import chain_util
from core.util import date_util
from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.sql import functions as sqlalchemyfunc

from notd.delegation_manager import DelegationManager
from notd.model import AccountGm
from notd.model import GmAccountRow
from notd.model import GmCollectionRow
from notd.model import LatestAccountGm
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import AccountCollectionGmsTable
from notd.store.schema import AccountGmsTable
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenOwnershipsView
from notd.store.schema_conversions import account_collection_gm_from_row
from notd.store.schema_conversions import account_gm_from_row
from notd.store.schema_conversions import collection_from_row


class GmNotification(BaseModel):
    address: Optional[str]


class GmManager:

    def __init__(self, retriever: Retriever, saver: Saver, delegationManager: DelegationManager) -> None:
        self.retriever = retriever
        self.saver = saver
        self.delegationManager = delegationManager
        self.notifications: List[GmNotification] = []

    # TODO(krishan711): The structure of the response should be handled in api layer
    async def generate_gms(self) -> AsyncGenerator[bytes, None]:
        nextIndex = len(self.notifications)
        while True:
            notificationCount = len(self.notifications)
            if notificationCount > nextIndex:
                for index, item in enumerate(self.notifications[nextIndex: notificationCount]):
                    outputString = f"id: {nextIndex + index}\ndata: {json.dumps(item.dict())}\n\n"
                    yield outputString.encode()
                nextIndex = notificationCount
            await asyncio.sleep(1)

    async def create_anonymous_gm(self) -> None:
        self.notifications.append(GmNotification(address=None))

    async def create_gm(self, account: str, signatureMessage: str, signature: str) -> AccountGm:
        delegations = await self.delegationManager.get_delegations(delegateAddress=account)
        for delegation in delegations:
            await self._create_gm(account=delegation.vaultAddress, delegateAddress=delegation.delegateAddress, signatureMessage=signatureMessage, signature=signature)
        return await self._create_gm(account=account, delegateAddress=None, signatureMessage=signatureMessage, signature=signature)

    async def _create_gm(self, account: str, delegateAddress: Optional[str], signatureMessage: str, signature: str) -> AccountGm:
        account = chain_util.normalize_address(value=account)
        delegateAddress = chain_util.normalize_address(value=delegateAddress) if delegateAddress else None
        # TODO(krishan711): validate signature
        self.notifications.append(GmNotification(address=account))
        todayDate = date_util.start_of_day()
        latestAccountGmQuery = (
            AccountGmsTable.select()
            .where(AccountGmsTable.c.address == account)
            .order_by(AccountGmsTable.c.date.desc())
            .limit(1)
        )
        latestAccountGmResult = await self.retriever.database.execute(query=latestAccountGmQuery)
        latestAccountGmRow = latestAccountGmResult.mappings().first()
        latestAccountGm = account_gm_from_row(latestAccountGmRow) if latestAccountGmRow else None
        if latestAccountGm and latestAccountGm.date >= todayDate:
            # NOTE(krishan711): could check here that this date has all the current collections
            return latestAccountGm
        streakLength = latestAccountGm.streakLength + 1 if latestAccountGm and latestAccountGm.date == date_util.datetime_from_datetime(dt=todayDate, days=-1) else 1
        ownedCollectionsQuery = (
            sqlalchemy.select(TokenOwnershipsView.c.registryAddress.distinct())
            .where(TokenOwnershipsView.c.ownerAddress == account)
            .where(TokenOwnershipsView.c.quantity > 0)
        )
        ownedCollectionsResult = await self.retriever.database.execute(query=ownedCollectionsQuery)
        ownedCollectionAddresses = {registryAddress for (registryAddress, ) in ownedCollectionsResult}
        async with self.saver.create_transaction() as connection:
            accountGm = await self.saver.create_account_gm(address=account, delegateAddress=delegateAddress, date=todayDate, streakLength=streakLength, collectionCount=len(ownedCollectionAddresses), signatureMessage=signatureMessage, signature=signature, connection=connection)
            for registryAddress in ownedCollectionAddresses:
                await self.saver.create_account_collection_gm(accountAddress=account, accountDelegateAddress=delegateAddress, registryAddress=registryAddress, date=todayDate, signatureMessage=signatureMessage, signature=signature, connection=connection)
        return accountGm

    async def list_gm_account_rows(self) -> List[GmAccountRow]:
        latestRowQuery: Select[Any] = (  # type: ignore[misc]
            sqlalchemy.select(AccountGmsTable.c.address, sqlalchemyfunc.max(AccountGmsTable.c.date).label('date'))
            .where(AccountGmsTable.c.date >= date_util.start_of_day(dt=date_util.datetime_from_now(days=-7)))
            .group_by(AccountGmsTable.c.address)
        )
        weekCountQuery = (
            sqlalchemy.select(AccountGmsTable.c.address, sqlalchemyfunc.count(AccountGmsTable.c.accountGmId).label('weekCount'))
            .where(AccountGmsTable.c.date > date_util.datetime_from_now(days=-7))
            .group_by(AccountGmsTable.c.address)
        ).subquery()
        monthCountQuery = (
            sqlalchemy.select(AccountGmsTable.c.address, sqlalchemyfunc.count(AccountGmsTable.c.accountGmId).label('monthCount'))
            .where(AccountGmsTable.c.date > date_util.datetime_from_now(days=-30))
            .group_by(AccountGmsTable.c.address)
        ).subquery()
        accountRowsQuery = (
            sqlalchemy.select(AccountGmsTable, weekCountQuery, monthCountQuery)
            .join(weekCountQuery, weekCountQuery.c.address == AccountGmsTable.c.address)
            .join(monthCountQuery, monthCountQuery.c.address == AccountGmsTable.c.address)
            .where(sqlalchemy.tuple_(AccountGmsTable.c.address, AccountGmsTable.c.date).in_(latestRowQuery))
            .order_by(AccountGmsTable.c.streakLength.desc(), AccountGmsTable.c.date.desc())
            .limit(500)
        )
        accountRowsResult = await self.retriever.database.execute(query=accountRowsQuery)
        accountRows = [
            GmAccountRow(
                address=row[AccountGmsTable.c.address],
                streakLength=row[AccountGmsTable.c.streakLength],
                lastDate=row[AccountGmsTable.c.date],
                weekCount=int(row['weekCount']),
                monthCount=int(row['monthCount']),
            ) for row in accountRowsResult.mappings()
        ]
        return accountRows

    async def list_gm_collection_account_rows(self, registryAddress: str) -> List[GmAccountRow]:
        latestRowQuery: Select[Any] = (  # type: ignore[misc]
            sqlalchemy.select(AccountCollectionGmsTable.c.accountAddress, sqlalchemyfunc.max(AccountCollectionGmsTable.c.date).label('date'))
            .where(AccountCollectionGmsTable.c.date >= date_util.start_of_day(dt=date_util.datetime_from_now(days=-7)))
            .where(AccountCollectionGmsTable.c.registryAddress == registryAddress)
            .group_by(AccountCollectionGmsTable.c.accountAddress)
        )
        latestAccountRowQuery = (
            sqlalchemy.select(AccountGmsTable.c.address, sqlalchemyfunc.max(AccountGmsTable.c.date).label('date'))
            .where(AccountGmsTable.c.date >= date_util.start_of_day(dt=date_util.datetime_from_now(days=-7)))
            .group_by(AccountGmsTable.c.address)
        ).subquery()
        weekCountQuery = (
            sqlalchemy.select(AccountCollectionGmsTable.c.accountAddress, sqlalchemyfunc.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('weekCount'))
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-7))
            .where(AccountCollectionGmsTable.c.registryAddress == registryAddress)
            .group_by(AccountCollectionGmsTable.c.accountAddress)
        ).subquery()
        monthCountQuery = (
            sqlalchemy.select(AccountCollectionGmsTable.c.accountAddress, sqlalchemyfunc.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('monthCount'))
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-30))
            .where(AccountCollectionGmsTable.c.registryAddress == registryAddress)
            .group_by(AccountCollectionGmsTable.c.accountAddress)
        ).subquery()
        accountRowsQuery = (
            sqlalchemy.select(AccountCollectionGmsTable, AccountGmsTable, latestAccountRowQuery, weekCountQuery, monthCountQuery)
            .join(latestAccountRowQuery, latestAccountRowQuery.c.address == AccountCollectionGmsTable.c.accountAddress)
            .join(AccountGmsTable, sqlalchemy.and_(latestAccountRowQuery.c.address == AccountGmsTable.c.address, latestAccountRowQuery.c.date == AccountGmsTable.c.date))
            .join(weekCountQuery, weekCountQuery.c.accountAddress == AccountCollectionGmsTable.c.accountAddress)
            .join(monthCountQuery, monthCountQuery.c.accountAddress == AccountCollectionGmsTable.c.accountAddress)
            .where(sqlalchemy.tuple_(AccountCollectionGmsTable.c.accountAddress, AccountCollectionGmsTable.c.date).in_(latestRowQuery))
            .where(AccountCollectionGmsTable.c.registryAddress == registryAddress)
            .order_by(AccountGmsTable.c.streakLength.desc(), AccountCollectionGmsTable.c.date.desc())
            .limit(500)
        )
        accountRowsResult = await self.retriever.database.execute(query=accountRowsQuery)
        accountRows = [
            GmAccountRow(
                address=row[AccountCollectionGmsTable.c.accountAddress],
                streakLength=row[AccountGmsTable.c.streakLength],
                lastDate=row[AccountCollectionGmsTable.c.date],
                weekCount=int(row['weekCount']),
                monthCount=int(row['monthCount']),
            ) for row in accountRowsResult.mappings()
        ]
        return accountRows

    async def list_gm_collection_rows(self) -> List[GmCollectionRow]:
        todayCountQuery = (
            sqlalchemy.select(AccountCollectionGmsTable.c.registryAddress, sqlalchemyfunc.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('todayCount'))
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-1))
            .group_by(AccountCollectionGmsTable.c.registryAddress)
        ).subquery()
        weekCountQuery = (
            sqlalchemy.select(AccountCollectionGmsTable.c.registryAddress, sqlalchemyfunc.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('weekCount'))
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-7))
            .group_by(AccountCollectionGmsTable.c.registryAddress)
        ).subquery()
        monthCountQuery = (
            sqlalchemy.select(AccountCollectionGmsTable.c.registryAddress, sqlalchemyfunc.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('monthCount'))
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-30))
            .group_by(AccountCollectionGmsTable.c.registryAddress)
        ).subquery()
        collectionRowsQuery = (
            sqlalchemy.select(TokenCollectionsTable, monthCountQuery, weekCountQuery, todayCountQuery)
            .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenCollectionsTable.c.address)
            .join(monthCountQuery, monthCountQuery.c.registryAddress == TokenCollectionsTable.c.address)
            .join(weekCountQuery, weekCountQuery.c.registryAddress == TokenCollectionsTable.c.address, isouter=True)
            .join(todayCountQuery, todayCountQuery.c.registryAddress == TokenCollectionsTable.c.address, isouter=True)
            .order_by(sqlalchemyfunc.coalesce(todayCountQuery.c.todayCount, 0).desc(), sqlalchemyfunc.coalesce(weekCountQuery.c.weekCount, 0).desc(), sqlalchemyfunc.coalesce(monthCountQuery.c.monthCount, 0).desc(), CollectionTotalActivitiesTable.c.totalValue.desc())
            .limit(500)
        )
        collectionRowsResult = await self.retriever.database.execute(query=collectionRowsQuery)
        collectionRows = [
            GmCollectionRow(
                collection=collection_from_row(row),
                todayCount=int(row['todayCount']) if row['todayCount'] else 0,
                weekCount=int(row['weekCount']) if row['weekCount'] else 0,
                monthCount=int(row['monthCount']) if row['monthCount'] else 0,
            ) for row in collectionRowsResult.mappings()
        ]
        return collectionRows

    async def get_latest_gm_for_account(self, address: str) -> LatestAccountGm:
        latestAccountGmQuery = (
            AccountGmsTable.select()
            .where(AccountGmsTable.c.address == address)
            .order_by(AccountGmsTable.c.date.desc())
            .limit(1)
        )
        latestAccountGmResult = await self.retriever.database.execute(query=latestAccountGmQuery)
        latestAccountGmRow = latestAccountGmResult.mappings().first()
        if not latestAccountGmRow:
            raise NotFoundException()
        latestAccountGm = account_gm_from_row(latestAccountGmRow)
        query = (
            AccountCollectionGmsTable.select()
            .where(AccountCollectionGmsTable.c.accountAddress == address)
            .where(AccountCollectionGmsTable.c.date == latestAccountGmRow.date)
        )
        latestAccountCollectionGmResult = await self.retriever.database.execute(query=query)
        latestAccountCollectionsGm = [account_collection_gm_from_row(row) for row in latestAccountCollectionGmResult.mappings()]
        return LatestAccountGm(
            accountGm=latestAccountGm,
            accountCollectionGms=latestAccountCollectionsGm
        )
