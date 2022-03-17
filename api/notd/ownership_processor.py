from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter

from notd.model import RetrievedTokenOwnership
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable


class TokenOwnershipProcessor:

    def __init__(self,retriever: Retriever):
        self.retriever = retriever

    async def retrieve_erc721_token_ownership(self, registryAddress: str, tokenId: str):
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=False,
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenType.key, eq='erc721'),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=1
        )
        tokenTransfer = tokenTransfers[0]
        return RetrievedTokenOwnership(
            ownerAddress=tokenTransfer.toAddress,
            registryAddress=registryAddress,
            tokenId=tokenId,
            purchasedDate=tokenTransfer.blockDate,
            purchasedValue=tokenTransfer.value,
            transactionHash=tokenTransfer.transactionHash,
        )
