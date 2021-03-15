import asyncio
import datetime
import logging
from typing import Sequence

from notd.block_processor import BlockProcessor
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from notd.core.store.retriever import Direction
from notd.core.store.retriever import Order
from notd.core.store.retriever import RandomOrder
from notd.core.store.retriever import DateFieldFilter
from notd.core.store.retriever import StringFieldFilter
from notd.core.requester import Requester
from notd.core.exceptions import NotFoundException
from notd.store.schema import TokenTransfersTable
from notd.model import UiData
from notd.model import Token
from notd.model import RegistryToken
from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.core.exceptions import DuplicateValueException
from notd.core.sqs_message_queue import SqsMessageQueue
from notd.opensea_client import OpenseaClient
from notd.token_client import TokenClient

class NotdManager:

    def __init__(self, blockProcessor: BlockProcessor, saver: Saver, retriever: NotdRetriever, workQueue: SqsMessageQueue, openseaClient: OpenseaClient, tokenClient: TokenClient):
        self.blockProcessor = blockProcessor
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.openseaClient = openseaClient
        self.tokenClient = tokenClient
        self._tokenCache = dict()

    async def retrieve_ui_data(self, startDate: datetime.datetime, endDate: datetime.datetime) -> UiData:
        highestPricedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        mostTradedToken = await self.retriever.get_most_traded_token(startDate=startDate, endDate=endDate)
        mostTradedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=mostTradedToken.registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=mostTradedToken.tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)]
        )
        randomTokenTransfers = await self.retriever.list_token_transfers(orders=[RandomOrder()], limit=1)
        return UiData(
            highestPricedTokenTransfer=highestPricedTokenTransfers[0],
            mostTradedTokenTransfers=mostTradedTokenTransfers,
            randomTokenTransfer=randomTokenTransfers[0],
            sponsoredToken=Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='64159879865138287087882027887075729047962830622590748212892263500451722297345')
        )

    async def receive_new_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())

    async def receive_new_blocks(self) -> None:
        latestTokenTransfers = await self.retriever.list_token_transfers(orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)], limit=1)
        latestProcessedBlockNumber = latestTokenTransfers[0].blockNumber
        latestBlockNumber = await self.blockProcessor.get_latest_block_number()
        logging.info(f'Scheduling messages for processing blocks from {latestProcessedBlockNumber} to {latestBlockNumber}')
        batchSize = 25
        for startBlockNumber in reversed(range(latestProcessedBlockNumber, latestBlockNumber + 1, batchSize)):
            endBlockNumber = min(startBlockNumber + batchSize, latestBlockNumber + 1)
            await self.workQueue.send_message(message=ProcessBlockRangeMessageContent(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber).to_message())

    async def process_block_range(self, startBlockNumber: int, endBlockNumber: int) -> None:
        blockNumbers = list(range(startBlockNumber, endBlockNumber))
        await self.process_blocks(blockNumbers=blockNumbers)

    async def process_blocks(self, blockNumbers: Sequence[int]) -> None:
        await asyncio.gather(*[self.process_block(blockNumber=blockNumber) for blockNumber in blockNumbers])

    async def process_block(self, blockNumber: int) -> None:
        retrievedTokenTransfers = await self.blockProcessor.get_transfers_in_block(blockNumber=blockNumber)
        logging.info(f'Found {len(retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        for retrievedTokenTransfer in retrievedTokenTransfers:
            logging.debug(f'Transferred {retrievedTokenTransfer.tokenId} from {retrievedTokenTransfer.fromAddress} to {retrievedTokenTransfer.toAddress}')
            logging.debug(f'Paid {retrievedTokenTransfer.value / 100000000000000000.0}Ξ ({retrievedTokenTransfer.gasUsed * retrievedTokenTransfer.gasPrice / 100000000000000000.0}Ξ) to {retrievedTokenTransfer.registryAddress}')
            logging.debug(f'OpenSea url: https://opensea.io/assets/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
            logging.debug(f'OpenSea api url: https://api.opensea.io/api/v1/asset/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
            try:
                await self.saver.create_token_transfer(transactionHash=retrievedTokenTransfer.transactionHash, registryAddress=retrievedTokenTransfer.registryAddress, fromAddress=retrievedTokenTransfer.fromAddress, toAddress=retrievedTokenTransfer.toAddress, tokenId=retrievedTokenTransfer.tokenId, value=retrievedTokenTransfer.value, gasLimit=retrievedTokenTransfer.gasLimit, gasPrice=retrievedTokenTransfer.gasPrice, gasUsed=retrievedTokenTransfer.gasUsed, blockNumber=retrievedTokenTransfer.blockNumber, blockHash=retrievedTokenTransfer.blockHash, blockDate=retrievedTokenTransfer.blockDate)
            except DuplicateValueException:
                logging.debug(f'Ignoring previously saved transaction')

    async def retreive_registry_token(self, registryAddress: str, tokenId: str) -> RegistryToken:
        cacheKey = f'{registryAddress}:{tokenId}'
        if cacheKey in self._tokenCache:
            return self._tokenCache[cacheKey]
        try:
            registryToken = await self.openseaClient.retreive_registry_token(registryAddress=registryAddress, tokenId=tokenId)
        except NotFoundException:
            registryToken = await self.tokenClient.retreive_registry_token(registryAddress=registryAddress, tokenId=tokenId)
        self._tokenCache[cacheKey] = registryToken
        return registryToken
