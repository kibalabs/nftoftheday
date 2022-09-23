
from typing import Optional

from core.exceptions import NotFoundException
from core.util import date_util
from notd.account_ens_name_processor import AccountEnsNameProcessor
from notd.model import AccountEnsName
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class EnsManager:

    def __init__(self, retriever: Retriever, saver: Saver, accountEnsNameProcessor: AccountEnsNameProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.accountEnsNameProcessor=accountEnsNameProcessor

    async def get_account_ens_name(self, accountAddress: str) -> Optional[AccountEnsName]:
        async with self.saver.create_transaction() as connection:
            try:
                accountEnsName = await self.retriever.get_account_ens_name_by_account_address(accountAddress=accountAddress, connection=connection)
            except NotFoundException:
                accountEnsName = None
            if accountEnsName:
                if accountEnsName.ensName and accountEnsName.updatedDate < date_util.datetime_from_now(days=-3):
                    return accountEnsName
                await self.saver.delete_account_ens_name(accountEnsNameId=accountEnsName.accountEnsNameId, connection=connection)
            ensName = await self.accountEnsNameProcessor.get_ens_name(accountAddress=accountAddress)
            accountEnsName = await self.saver.create_account_ens_name(accountAddress=accountAddress, ensName=ensName, connection=connection)
            print(accountEnsName)
            return accountEnsName
