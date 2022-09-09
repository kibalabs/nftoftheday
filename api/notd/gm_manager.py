from typing import Sequence

import sqlalchemy
from core.util import chain_util
from core.util import date_util

from notd.model import GmAccountRow
from notd.model import GmCollectionRow
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import AccountCollectionGmsTable
from notd.store.schema import AccountGmsTable
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema_conversions import account_gm_from_row
from notd.store.schema_conversions import collection_from_row


class GmManager:

    def __init__(self, retriever: Retriever, saver: Saver) -> None:
        self.retriever = retriever
        self.saver = saver

    async def create_gm(self, account: str, signatureMessage: str, signature: str) -> None:
        account = chain_util.normalize_address(value=account)
        # TODO(krishan711): validate signature
        todayDate = date_util.start_of_day()
        latestAccountGmQuery = (
            AccountGmsTable.select()
            .where(AccountGmsTable.c.address == account)
            .order_by(AccountGmsTable.c.date.desc())
            .limit(1)
        )
        latestAccountGmResult = await self.retriever.database.execute(query=latestAccountGmQuery)
        latestAccountGmRow = latestAccountGmResult.first()
        latestAccountGm = account_gm_from_row(row=latestAccountGmRow) if latestAccountGmRow else None
        if latestAccountGm and latestAccountGm.date >= todayDate:
            # NOTE(krishan711): could check here that this date has all the current collections
            return
        streakLength = latestAccountGm.streakLength + 1 if latestAccountGm and latestAccountGm.date == date_util.datetime_from_datetime(dt=todayDate, days=-1) else 1
        ownedCollectionsQuery = (
            TokenOwnershipsTable.select()
            .with_only_columns([TokenOwnershipsTable.c.registryAddress.distinct()])
            .where(TokenOwnershipsTable.c.ownerAddress == account)
        )
        ownedCollectionsResult = await self.retriever.database.execute(query=ownedCollectionsQuery)
        ownedCollectionAddresses = {registryAddress for (registryAddress, ) in ownedCollectionsResult}
        async with self.saver.create_transaction() as connection:
            await self.saver.create_account_gm(address=account, date=todayDate, streakLength=streakLength, signatureMessage=signatureMessage, signature=signature, connection=connection)
            for registryAddress in ownedCollectionAddresses:
                await self.saver.create_account_collection_gm(accountAddress=account, registryAddress=registryAddress, date=todayDate, signatureMessage=signatureMessage, signature=signature, connection=connection)

    async def list_gm_account_rows(self) -> Sequence[GmAccountRow]:
        latestRowQuery = (
            AccountGmsTable.select()
            .with_only_columns([AccountGmsTable.c.address, sqlalchemy.func.max(AccountGmsTable.c.date).label('date')])
            .where(AccountGmsTable.c.date.in_([date_util.start_of_day(), date_util.start_of_day(dt=date_util.datetime_from_now(days=-1))]))
            .group_by(AccountGmsTable.c.address)
        ).subquery()
        weekCountQuery = (
            AccountGmsTable.select()
            .with_only_columns([AccountGmsTable.c.address, sqlalchemy.func.count(AccountGmsTable.c.accountGmId).label('count')])
            .where(AccountGmsTable.c.date > date_util.datetime_from_now(days=-7))
            .group_by(AccountGmsTable.c.address)
        ).subquery()
        monthCountQuery = (
            AccountGmsTable.select()
            .with_only_columns([AccountGmsTable.c.address, sqlalchemy.func.count(AccountGmsTable.c.accountGmId).label('count')])
            .where(AccountGmsTable.c.date > date_util.datetime_from_now(days=-30))
            .group_by(AccountGmsTable.c.address)
        ).subquery()
        accountRowsQuery = (
            sqlalchemy.select(AccountGmsTable, weekCountQuery, monthCountQuery)
            .join(weekCountQuery, weekCountQuery.c.address == AccountGmsTable.c.address)
            .join(monthCountQuery, monthCountQuery.c.address == AccountGmsTable.c.address)
            .where(sqlalchemy.tuple_(AccountGmsTable.c.address, AccountGmsTable.c.date).in_(latestRowQuery))
            .order_by(AccountGmsTable.c.streakLength.desc(), monthCountQuery.c.count.desc())
        )
        accountRowsResult = await self.retriever.database.execute(query=accountRowsQuery)
        accountRows = [
            GmAccountRow(
                address=row[AccountGmsTable.c.address],
                streakLength=row[AccountGmsTable.c.streakLength],
                lastDate=row[AccountGmsTable.c.date],
                weekCount=int(row[weekCountQuery.c.count]),
                monthCount=int(row[monthCountQuery.c.count]),
            ) for row in accountRowsResult
        ]
        return accountRows

    async def list_gm_collection_rows(self) -> Sequence[GmCollectionRow]:
        todayCountQuery = (
            AccountCollectionGmsTable.select()
            .with_only_columns([AccountCollectionGmsTable.c.registryAddress, sqlalchemy.func.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('count')])
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-1))
            .group_by(AccountCollectionGmsTable.c.registryAddress)
        ).subquery()
        weekCountQuery = (
            AccountCollectionGmsTable.select()
            .with_only_columns([AccountCollectionGmsTable.c.registryAddress, sqlalchemy.func.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('count')])
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-7))
            .group_by(AccountCollectionGmsTable.c.registryAddress)
        ).subquery()
        monthCountQuery = (
            AccountCollectionGmsTable.select()
            .with_only_columns([AccountCollectionGmsTable.c.registryAddress, sqlalchemy.func.count(AccountCollectionGmsTable.c.accountCollectionGmId).label('count')])
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-30))
            .group_by(AccountCollectionGmsTable.c.registryAddress)
        ).subquery()
        collectionRowsQuery = (
            sqlalchemy.select(TokenCollectionsTable, monthCountQuery, weekCountQuery, todayCountQuery)
            .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenCollectionsTable.c.address)
            .join(monthCountQuery, monthCountQuery.c.registryAddress == TokenCollectionsTable.c.address)
            .join(weekCountQuery, weekCountQuery.c.registryAddress == TokenCollectionsTable.c.address, isouter=True)
            .join(todayCountQuery, todayCountQuery.c.registryAddress == TokenCollectionsTable.c.address, isouter=True)
            .order_by(todayCountQuery.c.count.desc(), CollectionTotalActivitiesTable.c.totalValue.desc())
        )
        collectionRowsResult = await self.retriever.database.execute(query=collectionRowsQuery)
        collectionRows = [
            GmCollectionRow(
                collection=collection_from_row(row=row),
                todayCount=int(row[todayCountQuery.c.count]) if row[todayCountQuery.c.count] else 0,
                weekCount=int(row[weekCountQuery.c.count]) if row[weekCountQuery.c.count] else 0,
                monthCount=int(row[monthCountQuery.c.count]) if row[monthCountQuery.c.count] else 0,
            ) for row in collectionRowsResult
        ]
        return collectionRows
