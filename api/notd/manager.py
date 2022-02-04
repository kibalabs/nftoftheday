import asyncio
import datetime
import json
import logging
from typing import List
from typing import Sequence

from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import RandomOrder
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.block_processor import BlockProcessor
from notd.messages import ProcessBlockMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.model import Collection, CollectionStatistics
from notd.model import RetrievedTokenTransfer
from notd.model import SponsoredToken
from notd.model import Token
from notd.model import TokenMetadata
from notd.model import UiData
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable
from notd.token_manager import TokenManager


class NotdManager:

    def __init__(self, blockProcessor: BlockProcessor, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, tokenManager: TokenManager, requester: Requester, revueApiKey: str):
        self.blockProcessor = blockProcessor
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenManager = tokenManager
        self.requester = requester
        self._tokenCache = dict()
        with open("notd/sponsored_tokens.json", "r") as sponsoredTokensFile:
            sponsoredTokensDicts = json.loads(sponsoredTokensFile.read())
        self.revueApiKey = revueApiKey
        self.sponsoredTokens = [SponsoredToken.from_dict(sponsoredTokenDict) for sponsoredTokenDict in sponsoredTokensDicts]

    def get_sponsored_token(self) -> Token:
        sponsoredToken = self.sponsoredTokens[0].token
        currentDate = date_util.datetime_from_now()
        allPastTokens = [sponsoredToken.token for sponsoredToken in self.sponsoredTokens if sponsoredToken.date < currentDate]
        if allPastTokens:
            sponsoredToken = allPastTokens[-1]
        return sponsoredToken

    async def retrieve_ui_data(self, startDate: datetime.datetime, endDate: datetime.datetime) -> UiData:
        highestPricedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        mostTradedToken = await self.retriever.get_most_traded_token(startDate=startDate, endDate=endDate)
        mostTradedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate),
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=mostTradedToken.registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=mostTradedToken.tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)]
        )
        randomTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[RandomOrder()],
            limit=1
        )
        transactionCount = await self.retriever.get_transaction_count(startDate=startDate, endDate=endDate)
        return UiData(
            highestPricedTokenTransfer=highestPricedTokenTransfers[0],
            mostTradedTokenTransfers=mostTradedTokenTransfers,
            randomTokenTransfer=randomTokenTransfers[0],
            sponsoredToken=self.get_sponsored_token(),
            transactionCount=transactionCount
        )
    async def get_collection_stats(self, address: str, startDate: datetime.datetime, endDate: datetime.datetime) -> CollectionStatistics:
        items = await self.retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=address),
            ],
        )
        itemCount = len(items)

        holders = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=address),
            ]
        )
        toAddresses = [holder.toAddress for holder in holders]
        fromAddresses = [holder.fromAddress for holder in holders]
        for holderAddress in toAddresses:
            if holderAddress in fromAddresses:
                toAddresses.remove(holderAddress)

        holderCount = len(holderAddress)

        trades= await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=address),
            ],
        )
        totalTradeVolume = sum([trade.value for trade in trades])

        trades24h = trades= await self.retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate),
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=address),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
        )
        tradeVolume24Hours = sum([trade.value for trade in trades24h])
        highestSaleLast24Hours = trades24h[0] if len(trades24h) >0 else None
        lowestSaleLast24Hours = trades24h[len(trades24h)] if len(trades24h) >0 else None

    
        return CollectionStatistics(
            itemCount=itemCount,
            holderCount=holderCount,
            totalTradeVolume=totalTradeVolume,
            lowestSaleLast24Hours=lowestSaleLast24Hours,
            highestSaleLast24Hours=highestSaleLast24Hours,
            tradeVolume24Hours=tradeVolume24Hours,
            )

    async def subscribe_email(self, email: str) -> None:
        await self.requester.post_json(url='https://www.getrevue.co/api/v2/subscribers', dataDict={'email': email.lower(), 'double_opt_in': False}, headers={'Authorization': f'Token {self.revueApiKey}'})

    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        return await self.tokenManager.update_token_metadata_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        return await self.tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_collection_deferred(self, address: str, shouldForce: bool = False) -> None:
        return await self.tokenManager.update_collection_deferred(address=address, shouldForce=shouldForce)

    async def update_collection(self, address: str, shouldForce: bool = False) -> None:
        return await self.tokenManager.update_collection(address=address, shouldForce=shouldForce)

    async def get_collection_by_address(self, address: str) -> Collection:
        return await self.tokenManager.get_collection_by_address(address=address)

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str) -> TokenMetadata:
        return await self.tokenManager.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)

    async def receive_new_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())

    async def receive_new_blocks(self) -> None:
        latestTokenTransfers = await self.retriever.list_token_transfers(orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)], limit=1)
        latestProcessedBlockNumber = latestTokenTransfers[0].blockNumber
        latestBlockNumber = await self.blockProcessor.get_latest_block_number()
        logging.info(f'Scheduling messages for processing blocks from {latestProcessedBlockNumber} to {latestBlockNumber}')
        # NOTE(krishan711): the delay is to mitigate soft fork problems
        for blockNumber in reversed(range(latestProcessedBlockNumber, latestBlockNumber + 1)):
            await self.workQueue.send_message(message=ProcessBlockMessageContent(blockNumber=blockNumber).to_message(), delaySeconds=60)

    async def _create_token_transfers(self, retrievedTokenTransfers: List[RetrievedTokenTransfer]) -> None:
        for retrievedTokenTransfer in retrievedTokenTransfers:
            tokenTransfers = await self.retriever.list_token_transfers(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenTransfersTable.c.transactionHash.key, eq=retrievedTokenTransfer.transactionHash),
                    StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=retrievedTokenTransfer.registryAddress),
                    StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=retrievedTokenTransfer.tokenId),
                    StringFieldFilter(fieldName=TokenTransfersTable.c.fromAddress.key, eq=retrievedTokenTransfer.fromAddress),
                    StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=retrievedTokenTransfer.toAddress),
                ], limit=1, shouldIgnoreRegistryBlacklist=True
            )
            if len(tokenTransfers) > 0:
                logging.info(f'Skipping saving {retrievedTokenTransfer.transactionHash}:{retrievedTokenTransfer.registryAddress}:{retrievedTokenTransfer.tokenId} as its already saved')
                continue
            await self.saver.create_token_transfer(retrievedTokenTransfer=retrievedTokenTransfer)

    async def process_block_range(self, startBlockNumber: int, endBlockNumber: int) -> None:
        blockNumbers = list(range(startBlockNumber, endBlockNumber))
        await self.process_blocks(blockNumbers=blockNumbers)

    async def process_blocks(self, blockNumbers: Sequence[int]) -> None:
        await asyncio.gather(*[self.process_block(blockNumber=blockNumber) for blockNumber in blockNumbers])

    async def process_block(self, blockNumber: int) -> None:
        retrievedTokenTransfers = await self.blockProcessor.get_transfers_in_block(blockNumber=blockNumber)
        logging.info(f'Found {len(retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        await asyncio.gather(*[self.update_token_metadata_deferred(registryAddress=retrievedTokenTransfer.registryAddress, tokenId=retrievedTokenTransfer.tokenId) for retrievedTokenTransfer in retrievedTokenTransfers])
        await asyncio.gather(*[self.update_collection_deferred(address=address) for address in set(retrievedTokenTransfer.registryAddress for retrievedTokenTransfer in retrievedTokenTransfers)])
        await self._create_token_transfers(retrievedTokenTransfers=retrievedTokenTransfers)
