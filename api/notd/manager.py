import datetime
import json
import logging
from typing import List
from typing import Sequence
from typing import Tuple
from asyncpg import PrivilegeNotGranted

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

from notd.block_processor import BlockProcessor
from notd.messages import ProcessBlockMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import ReprocessBlocksMessageContent
from notd.model import Collection
from notd.model import ProcessedBlock
from notd.model import SponsoredToken
from notd.model import Token
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.model import TradedToken
from notd.model import UiData
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
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

    async def retrieve_highest_priced_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        highestPricedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=BlocksTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        return highestPricedTokenTransfers[0]

    async def retrieve_random_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        randomTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=BlocksTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[RandomOrder()],
            limit=1
        )
        return randomTokenTransfers[0]

    async def get_transfer_count(self, startDate: datetime.datetime, endDate: datetime.datetime) ->int:
        return await self.retriever.get_transaction_count(startDate=startDate, endDate=endDate)

    async def retrieve_ui_data(self, startDate: datetime.datetime, endDate: datetime.datetime) -> UiData:
        mostTradedToken = await self.retriever.get_most_traded_token(startDate=startDate, endDate=endDate)
        mostTradedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(fieldName=BlocksTable.c.blockDate.key, gte=startDate, lt=endDate),
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=mostTradedToken.registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=mostTradedToken.tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)]
        )
        return UiData(
            highestPricedTokenTransfer=await self.retrieve_highest_priced_transfer(startDate=startDate, endDate=endDate),
            randomTokenTransfer=await self.retrieve_random_transfer(startDate=startDate, endDate=endDate),
            mostTradedTokenTransfers = mostTradedTokenTransfers,
            sponsoredToken=self.get_sponsored_token(),
            transactionCount=await self.get_transfer_count(startDate=startDate, endDate=endDate)
        )

    async def retrieve_most_traded_token_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        mostTradedToken = await self.retriever.get_most_traded_token(startDate=startDate, endDate=endDate)
        mostTradedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate),
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=mostTradedToken.registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=mostTradedToken.tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)]
        )
        return TradedToken(
            collectionToken=mostTradedToken,
            latestTransfer=mostTradedTokenTransfers[0],
            transferCount=len(mostTradedTokenTransfers)
        )

    async def get_collection_recent_sales(self, registryAddress: str, limit: int, offset: int) -> List[TokenTransfer]:
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=True,
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                IntegerFieldFilter(fieldName=TokenTransfersTable.c.value.key, gt=0),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

    async def get_collection_token_recent_sales(self, registryAddress: str, tokenId: str, limit: int, offset: int) -> List[TokenTransfer]:
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=True,
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
                IntegerFieldFilter(fieldName=TokenTransfersTable.c.value.key, gt=0),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

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
        await self.process_blocks_deferred(blockNumbers=blockNumbers)

    async def process_blocks_deferred(self, blockNumbers: Sequence[int], delaySeconds: int = 0) -> None:
        messages = [ProcessBlockMessageContent(blockNumber=blockNumber).to_message() for blockNumber in blockNumbers]
        await self.workQueue.send_messages(messages=messages, delaySeconds=delaySeconds)

    async def process_block_deferred(self, blockNumber: int, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=ProcessBlockMessageContent(blockNumber=blockNumber).to_message(), delaySeconds=delaySeconds)

    async def process_block(self, blockNumber: int) -> None:
        processedBlock = await self.blockProcessor.process_block(blockNumber=blockNumber)
        logging.info(f'Found {len(processedBlock.retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        collectionAddresses = list(set(retrievedTokenTransfer.registryAddress for retrievedTokenTransfer in processedBlock.retrievedTokenTransfers))
        logging.info(f'Found {len(collectionAddresses)} collections in block #{blockNumber}')
        collectionTokenIds = list(set((retrievedTokenTransfer.registryAddress, retrievedTokenTransfer.tokenId) for retrievedTokenTransfer in processedBlock.retrievedTokenTransfers))
        logging.info(f'Found {len(collectionTokenIds)} tokens in block #{blockNumber}')
        await self.tokenManager.update_collections_deferred(addresses=collectionAddresses)
        await self.tokenManager.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds)
        await self._save_processed_block(processedBlock=processedBlock)

    @staticmethod
    def _uniqueness_tuple_from_token_transfer(tokenTransfer: TokenTransfer) -> Tuple[str, str, str, str, str, int, str, int]:
        return (tokenTransfer.transactionHash, tokenTransfer.registryAddress, tokenTransfer.tokenId, tokenTransfer.fromAddress, tokenTransfer.toAddress, tokenTransfer.blockNumber, tokenTransfer.blockHash, tokenTransfer.amount)

    async def _save_processed_block(self, processedBlock: ProcessedBlock) -> None:
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
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, eq=processedBlock.blockNumber),
                ], shouldIgnoreRegistryBlacklist=True
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
            await self.saver.delete_token_transfers(connection=connection, tokenTransferIds=tokenTransferIdsToDelete)
            retrievedTokenTransfersToSave = []
            for retrievedTuple, retrievedTokenTransfer in retrievedTupleTransferMaps.items():
                if retrievedTuple in existingTuples:
                    continue
                retrievedTokenTransfersToSave.append(retrievedTokenTransfer)
            await self.saver.create_token_transfers(connection=connection, retrievedTokenTransfers=retrievedTokenTransfersToSave)
            logging.info(f'Saving transfers for block {processedBlock.blockNumber}: saved {len(retrievedTokenTransfersToSave)}, deleted {len(tokenTransferIdsToDelete)}, kept {len(existingTokenTransfers) - len(tokenTransferIdsToDelete)}')
