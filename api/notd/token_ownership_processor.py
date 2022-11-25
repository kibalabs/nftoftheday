import datetime
from typing import Dict
from typing import List
from typing import Optional

from core.exceptions import KibaException
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import DateFieldFilter
from core.store.retriever import FieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util

from notd.model import RetrievedTokenMultiOwnership
from notd.model import RetrievedTokenOwnership
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable


class NoOwnershipException(KibaException):
    def __init__(self) -> None:
        super().__init__(message='No ownership')

class TokenOwnershipProcessor:

    def __init__(self,retriever: Retriever):
        self.retriever = retriever

    async def calculate_token_single_ownership(self, registryAddress: str, tokenId: str, date: Optional[datetime.datetime] = None)-> RetrievedTokenOwnership:
        filters: List[FieldFilter] = [
            StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
            StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
        ]
        if date:
            filters.append(DateFieldFilter(fieldName=BlocksTable.c.blockDate.key, lte=date))
        tokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=filters,
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=1,
        )
        if len(tokenTransfers) == 0:
            raise NoOwnershipException()
        latestTokenTransfer = tokenTransfers[0]
        return RetrievedTokenOwnership(
            registryAddress=registryAddress,
            tokenId=tokenId,
            ownerAddress=latestTokenTransfer.toAddress,
            transferDate=latestTokenTransfer.blockDate,
            transferValue=latestTokenTransfer.value,
            transferTransactionHash=latestTokenTransfer.transactionHash,
        )

    async def calculate_token_multi_ownership(self, registryAddress: str, tokenId: str, date: Optional[datetime.datetime] = None) -> List[RetrievedTokenMultiOwnership]:
        ownerships: Dict[str, RetrievedTokenMultiOwnership] = {}
        offset = 0
        limit = 500
        filters: List[FieldFilter] = [
            StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
            StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
        ]
        if date:
            filters.append(DateFieldFilter(fieldName=BlocksTable.c.blockDate.key, lte=date))
        while True:
            tokenTransfers = await self.retriever.list_token_transfers(
                fieldFilters=filters,
                orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.ASCENDING)],
                limit=limit,
                offset=offset,
            )
            for tokenTransfer in tokenTransfers:
                if tokenTransfer.toAddress != chain_util.BURN_ADDRESS:
                    receiverOwnership = ownerships.get(tokenTransfer.toAddress)
                    if not receiverOwnership:
                        receiverOwnership = RetrievedTokenMultiOwnership(
                            registryAddress=registryAddress,
                            tokenId=tokenId,
                            ownerAddress=tokenTransfer.toAddress,
                            quantity=0,
                            averageTransferValue=0,
                            latestTransferDate=tokenTransfer.blockDate,
                            latestTransferTransactionHash=tokenTransfer.transactionHash,
                        )
                        ownerships[tokenTransfer.toAddress] = receiverOwnership
                    currentTotalValue = (receiverOwnership.averageTransferValue * receiverOwnership.quantity) + tokenTransfer.value
                    receiverOwnership.quantity += tokenTransfer.amount
                    receiverOwnership.averageTransferValue = int(currentTotalValue / receiverOwnership.quantity) if receiverOwnership.quantity > 0 else 0
                    receiverOwnership.latestTransferDate = tokenTransfer.blockDate
                    receiverOwnership.latestTransferTransactionHash = tokenTransfer.transactionHash
                if tokenTransfer.fromAddress != chain_util.BURN_ADDRESS:
                    senderOwnership = ownerships.get(tokenTransfer.fromAddress)
                    if not senderOwnership:
                        senderOwnership = RetrievedTokenMultiOwnership(
                            registryAddress=registryAddress,
                            tokenId=tokenId,
                            ownerAddress=tokenTransfer.fromAddress,
                            quantity=0,
                            averageTransferValue=0,
                            latestTransferDate=tokenTransfer.blockDate,
                            latestTransferTransactionHash=tokenTransfer.transactionHash,
                        )
                        ownerships[tokenTransfer.fromAddress] = senderOwnership
                    currentTotalValue = (senderOwnership.averageTransferValue * senderOwnership.quantity) - tokenTransfer.value
                    senderOwnership.quantity -= tokenTransfer.amount
                    senderOwnership.averageTransferValue = int(currentTotalValue / senderOwnership.quantity) if senderOwnership.quantity > 0 else 0
                    senderOwnership.latestTransferDate = tokenTransfer.blockDate
                    senderOwnership.latestTransferTransactionHash = tokenTransfer.transactionHash
            if len(tokenTransfers) < limit:
                break
            offset += limit
        return list(ownerships.values())
