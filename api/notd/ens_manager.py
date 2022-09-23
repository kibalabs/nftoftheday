
from typing import Optional
from notd.store.retriever import Retriever
from notd.model import AccountEnsName


class EnsManager:

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever
        pass

    async def get_account_ens_name(self, accountAddress: str) -> Optional[AccountEnsName]:
        accountEnsName = await self.retriever.get_account_ens_name_by_account_address(accountAddress=accountAddress)
        if accountEnsName.updatedDate < 3:
            return accountEnsName
        else:
            await self.update_account_ens_name(accountAddress=accountAddress)
        
    
    async def update_account_ens_name(self, accountAddress: str) -> None:
        pass