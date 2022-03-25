from typing import Dict, List

from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import chain_util

from notd.model import RetrievedTokenMultiOwnership, RetrievedTokenOwnership
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable


class TokenOwnershipProcessor:

    def __init__(self,retriever: Retriever):
        self.retriever = retriever

    async def calculate_token_single_ownership(self, registryAddress: str, tokenId: str)-> RetrievedTokenOwnership:
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=False,
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=1,
        )
        latestTokenTransfer = tokenTransfers[0]
        return RetrievedTokenOwnership(
            registryAddress=registryAddress,
            tokenId=tokenId,
            ownerAddress=latestTokenTransfer.toAddress,
            transferDate=latestTokenTransfer.blockDate,
            transferValue=latestTokenTransfer.value,
            transferTransactionHash=latestTokenTransfer.transactionHash,
        )

    async def calculate_token_multi_ownership(self, registryAddress: str, tokenId: str) -> List[RetrievedTokenMultiOwnership]:
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=False,
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.ASCENDING)],
        )
        ownerships: Dict[str, RetrievedTokenMultiOwnership] = dict()
        for tokenTransfer in tokenTransfers:
            print('tokenTransfer', tokenTransfer)
            if tokenTransfer.toAddress != chain_util.BURN_ADDRESS:
                receiverOwnership = ownerships.get(tokenTransfer.toAddress)
                if not receiverOwnership:
                    receiverOwnership = RetrievedTokenMultiOwnership(
                        registryAddress=registryAddress,
                        tokenId=tokenId,
                        ownerAddress=tokenTransfer.toAddress,
                        quantity=0,
                        averageValue=0,
                        latestTransferDate=tokenTransfer.blockDate,
                        latestTransferTransactionHash=tokenTransfer.transactionHash,
                    )
                    ownerships[tokenTransfer.toAddress] = receiverOwnership
                    receiverOwnership.quantity += tokenTransfer.amount
                receiverOwnership.latestTransferDate = tokenTransfer.blockDate
                receiverOwnership.latestTransferTransactionHash = tokenTransfer.transactionHash
            if tokenTransfer.fromAddress != chain_util.BURN_ADDRESS:
                senderOwnership = ownerships.get(tokenTransfer.fromAddress)
                if not senderOwnership:
                    senderOwnership = RetrievedTokenMultiOwnership(
                        registryAddress=registryAddress,
                        tokenId=tokenId,
                        ownerAddress=tokenTransfer.toAddress,
                        quantity=0,
                        averageValue=0,
                        latestTransferDate=tokenTransfer.blockDate,
                        latestTransferTransactionHash=tokenTransfer.transactionHash,
                    )
                    ownerships[tokenTransfer.fromAddress] = senderOwnership
                senderOwnership.quantity -= tokenTransfer.amount
                senderOwnership.latestTransferDate = tokenTransfer.blockDate
                senderOwnership.latestTransferTransactionHash = tokenTransfer.transactionHash
        print('list(ownerships.values())', list(ownerships.values()))
        return list(ownerships.values())
