from typing import Sequence
import sqlalchemy
from core.util import date_util
from core.util import chain_util
from notd.model import GmAccountRow, GmCollectionRow

from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import AccountCollectionGmsTable, AccountGmsTable, TokenOwnershipsTable
from notd.store.schema_conversions import account_gm_from_row


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
        # Want all the accounts with their latest row and a count of rows in week / month
        return []

    async def list_gm_collection_rows(self) -> Sequence[GmCollectionRow]:
        # Want all the collections grouped by day, week, month
        todayCountQuery = (
            AccountCollectionGmsTable.select()
            .with_only_columns([AccountCollectionGmsTable.c.registryAddress, sqlalchemy.count(AccountCollectionGmsTable.c.userAddress)])
            .where(AccountCollectionGmsTable.c.date > date_util.datetime_from_now(days=-1))
            .group_by(AccountCollectionGmsTable.c.registryAddress)
        )
        todayCountResult = await self.retriever.database.execute(query=todayCountQuery)

        return []
