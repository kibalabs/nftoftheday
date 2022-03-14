import sqlalchemy
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.store.retriever import RandomOrder
from core.store.retriever import StringFieldFilter
from core.util import date_util
from notd.model import RetrievedTokenOwnership, TokenOwnership
from core.store.retriever import StringFieldFilter

from notd.store.schema import BlocksTable, TokenMetadataTable, TokenTransfersTable
from notd.store.retriever import Retriever


class OwnershipProcessor:

    def __init__(self,retriever: Retriever):
        self.retriever = retriever
    
    async def get_ownership(self, registryAddress: str, tokenId: str):
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=True,
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
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
            transferId=tokenTransfer.tokenTransferId,
            transactionHash=tokenTransfer.transactionHash,
        )
