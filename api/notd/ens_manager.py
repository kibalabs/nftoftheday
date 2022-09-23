
from typing import Optional

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
        accountEnsName = await self.retriever.get_account_ens_name_by_account_address(accountAddress=accountAddress)
        if accountEnsName:
            if accountEnsName.ensName and accountEnsName.updatedDate < 3:
                return accountEnsName
            await self.saver.delete_account_ens_name(accountEnsNameId=accountEnsName.accountEnsNameId)
        ensName = await self.accountEnsNameProcessor.get_ens_name(accountAddress=accountAddress)
        accountEnsName = await self.saver.create_account_ens_name(accountAddress=accountAddress, ensName=ensName)
        return accountEnsName
