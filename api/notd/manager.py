import asyncio
import logging
from typing import List

from notd.block_processor import BlockProcessor
from notd.store.saver import Saver
from notd.store.retriever import Direction
from notd.store.retriever import Order
from notd.store.retriever import Retriever
from notd.store.schema import TokenTransfersTable
from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.core.exceptions import DuplicateValueException
from notd.core.sqs_message_queue import SqsMessageQueue

class NotdManager:

    def __init__(self, blockProcessor: BlockProcessor, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue):
        self.blockProcessor = blockProcessor
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue

    async def receive_new_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())

    async def receive_new_blocks(self) -> None:
        latestTokenTransfers = await self.retriever.list_token_transfers(orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)], limit=1)
        latestProcessedBlockNumber = latestTokenTransfers[0].blockNumber
        latestBlockNumber = await self.blockProcessor.get_latest_block_number()
        logging.info(f'Scheduling messages for processing blocks from {latestProcessedBlockNumber} to {latestBlockNumber}')
        batchSize = 10
        for startBlockNumber in range(latestProcessedBlockNumber, latestBlockNumber + 1, batchSize):
            endBlockNumber = min(startBlockNumber + batchSize, latestBlockNumber + 1)
            await self.workQueue.send_message(message=ProcessBlockRangeMessageContent(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber).to_message())

    async def process_block_range(self, startBlockNumber: int, endBlockNumber: int) -> None:
        blockNumbers = list(range(startBlockNumber, endBlockNumber))
        await self.process_blocks(blockNumbers=blockNumbers)

    async def process_blocks(self, blockNumbers: List[int]) -> None:
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
