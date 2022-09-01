import datetime
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple

import sqlalchemy
from core import logging
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.block_processor import BlockProcessor
from notd.collection_manager import CollectionManager
from notd.messages import ProcessBlockMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import ReprocessBlocksMessageContent
from notd.model import ProcessedBlock
from notd.model import TokenTransfer
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable
from notd.token_manager import TokenManager


class BlockManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, blockProcessor: BlockProcessor, ownershipManager: OwnershipManager, collectionManager: CollectionManager, tokenManager: TokenManager) -> None:
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.blockProcessor = blockProcessor
        self.ownershipManager = ownershipManager
        self.collectionManager = collectionManager
        self.tokenManager = tokenManager

    async def receive_new_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())

    async def receive_new_blocks(self) -> None:
        latestBlocks = await self.retriever.list_blocks(orders=[Order(fieldName=BlocksTable.c.blockNumber.key, direction=Direction.DESCENDING)], limit=1)
        latestProcessedBlockNumber = latestBlocks[0].blockNumber
        latestBlockNumber = await self.blockProcessor.get_latest_block_number()
        logging.info(f'Scheduling messages for processing blocks from {latestProcessedBlockNumber} to {latestBlockNumber}')
        await self.process_blocks_deferred(blockNumbers=list(reversed(range(latestProcessedBlockNumber, latestBlockNumber + 1))))

    async def reprocess_old_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReprocessBlocksMessageContent().to_message())

    async def reprocess_old_blocks(self) -> None:
        blocksToReprocessQuery = (
            sqlalchemy.select(BlocksTable.c.blockNumber)
            .where(BlocksTable.c.createdDate < date_util.datetime_from_now(minutes=-10))
            .where(BlocksTable.c.updatedDate - BlocksTable.c.blockDate < datetime.timedelta(minutes=10))
        )
        result = await self.retriever.database.execute(query=blocksToReprocessQuery)
        blockNumbers = [blockNumber for (blockNumber, ) in result]
        logging.info(f'Scheduling messages for reprocessing {len(blockNumbers)} blocks')
        await self.process_blocks_deferred(blockNumbers=blockNumbers, shouldSkipProcessingTokens=True)

    async def process_blocks_deferred(self, blockNumbers: Sequence[int], shouldSkipProcessingTokens: Optional[bool] = None, delaySeconds: int = 0) -> None:
        messages = [ProcessBlockMessageContent(blockNumber=blockNumber, shouldSkipProcessingTokens=shouldSkipProcessingTokens).to_message() for blockNumber in blockNumbers]
        await self.workQueue.send_messages(messages=messages, delaySeconds=delaySeconds)

    async def process_block_deferred(self, blockNumber: int, shouldSkipProcessingTokens: Optional[bool] = None, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=ProcessBlockMessageContent(blockNumber=blockNumber, shouldSkipProcessingTokens=shouldSkipProcessingTokens).to_message(), delaySeconds=delaySeconds)

    async def process_block(self, blockNumber: int, shouldSkipProcessingTokens: Optional[bool] = None, shouldSkipUpdatingOwnerships: Optional[bool] = None) -> None:
        processedBlock = await self.blockProcessor.process_block(blockNumber=blockNumber)
        logging.info(f'Found {len(processedBlock.retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        collectionTokenIds = await self._save_processed_block(processedBlock=processedBlock)
        collectionAddresses = list(set(registryAddress for registryAddress, _ in collectionTokenIds))
        logging.info(f'Found {len(collectionTokenIds)} changed tokens and {len(collectionAddresses)} changed collections in block #{blockNumber}')
        if not shouldSkipUpdatingOwnerships:
            await self.ownershipManager.update_token_ownerships_deferred(collectionTokenIds=collectionTokenIds)
        if not shouldSkipProcessingTokens:
            await self.collectionManager.update_collections_deferred(addresses=collectionAddresses)
            await self.tokenManager.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds)

    @staticmethod
    def _uniqueness_tuple_from_token_transfer(tokenTransfer: TokenTransfer) -> Tuple[str, str, str, str, str, int, int, int, str, bool, bool, bool, bool, bool, str]:
        return (tokenTransfer.transactionHash, tokenTransfer.registryAddress, tokenTransfer.tokenId, tokenTransfer.fromAddress, tokenTransfer.toAddress, tokenTransfer.blockNumber, tokenTransfer.amount, tokenTransfer.value,tokenTransfer.tokenType, tokenTransfer.isMultiAddress, tokenTransfer.isInterstitial, tokenTransfer.isBatch, tokenTransfer.isSwap, tokenTransfer.isOutbound, tokenTransfer.contractAddress)

    async def _save_processed_block(self, processedBlock: ProcessedBlock) -> Sequence[Tuple[str, str]]:
        changedTokens: Set[Tuple[str, str]] = set()
        async with self.saver.create_transaction() as connection:
            try:
                block = await self.retriever.get_block_by_number(connection=connection, blockNumber=processedBlock.blockNumber)
            except NotFoundException:
                block = None
            if block:
                await self.saver.update_block(connection=connection, blockId=block.blockId, blockHash=processedBlock.blockHash, blockDate=processedBlock.blockDate)
            else:
                await self.saver.create_block(connection=connection, blockNumber=processedBlock.blockNumber, blockHash=processedBlock.blockHash, blockDate=processedBlock.blockDate)
            existingTokenTransfers = await self.retriever.list_token_transfers(
                connection=connection,
                fieldFilters=[StringFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, eq=processedBlock.blockNumber)],
            )
            existingTuplesTransferMap = {self._uniqueness_tuple_from_token_transfer(tokenTransfer=tokenTransfer): tokenTransfer for tokenTransfer in existingTokenTransfers}
            existingTuples = set(existingTuplesTransferMap.keys())
            retrievedTupleTransferMaps = {self._uniqueness_tuple_from_token_transfer(tokenTransfer=tokenTransfer): tokenTransfer for tokenTransfer in processedBlock.retrievedTokenTransfers}
            retrievedTuples = set(retrievedTupleTransferMaps.keys())
            tokenTransferIdsToDelete = []
            for existingTuple, existingTokenTransfer in existingTuplesTransferMap.items():
                if existingTuple in retrievedTuples:
                    continue
                tokenTransferIdsToDelete.append(existingTokenTransfer.tokenTransferId)
                changedTokens.add((existingTokenTransfer.registryAddress, existingTokenTransfer.tokenId))
            await self.saver.delete_token_transfers(connection=connection, tokenTransferIds=tokenTransferIdsToDelete)
            retrievedTokenTransfersToSave = []
            for retrievedTuple, retrievedTokenTransfer in retrievedTupleTransferMaps.items():
                if retrievedTuple in existingTuples:
                    continue
                retrievedTokenTransfersToSave.append(retrievedTokenTransfer)
                changedTokens.add((retrievedTokenTransfer.registryAddress, retrievedTokenTransfer.tokenId))
            await self.saver.create_token_transfers(connection=connection, retrievedTokenTransfers=retrievedTokenTransfersToSave)
            logging.info(f'Saving transfers for block {processedBlock.blockNumber}: saved {len(retrievedTokenTransfersToSave)}, deleted {len(tokenTransferIdsToDelete)}, kept {len(existingTokenTransfers) - len(tokenTransferIdsToDelete)}')
        return list(changedTokens)
