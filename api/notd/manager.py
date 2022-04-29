import datetime
import json
import random
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple

import sqlalchemy
from core import logging
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import IntegerFieldFilter
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.block_processor import BlockProcessor
from notd.messages import ProcessBlockMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import ReprocessBlocksMessageContent
from notd.model import BaseSponsoredToken
from notd.model import Collection
from notd.model import CollectionActivity
from notd.model import CollectionStatistics
from notd.model import ProcessedBlock
from notd.model import SponsoredToken
from notd.model import Token
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.model import TradedToken
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row
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
        self.sponsoredTokens = [BaseSponsoredToken.from_dict(
            sponsoredTokenDict) for sponsoredTokenDict in sponsoredTokensDicts]

    async def get_sponsored_token(self) -> SponsoredToken:
        baseSponsoredToken = self.sponsoredTokens[0]
        currentDate = date_util.datetime_from_now()
        allPastTokens = [
            sponsoredToken for sponsoredToken in self.sponsoredTokens if sponsoredToken.date < currentDate]
        if allPastTokens:
            baseSponsoredToken = max(
                allPastTokens, key=lambda sponsoredToken: sponsoredToken.date)
        latestTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key,
                                  eq=baseSponsoredToken.token.registryAddress),
                StringFieldFilter(
                    fieldName=TokenTransfersTable.c.tokenId.key, eq=baseSponsoredToken.token.tokenId),
            ],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key,
                          direction=Direction.DESCENDING)],
            limit=1
        )
        return SponsoredToken(date=baseSponsoredToken.date, token=baseSponsoredToken.token, latestTransfer=latestTransfers[0] if len(latestTransfers) > 0 else None)

    async def retrieve_highest_priced_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        highestPricedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(
                fieldName=BlocksTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key,
                          direction=Direction.DESCENDING)],
            limit=1
        )
        return highestPricedTokenTransfers[0]

    async def retrieve_random_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        # NOTE(krishan711): this is no longer actually random, it's just the latest (random is too slow)
        randomTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(
                fieldName=BlocksTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key,
                          direction=Direction.DESCENDING)],
            offset=random.randint(1000, 10000),
            limit=1,
        )
        return randomTokenTransfers[0]

    async def get_transfer_count(self, startDate: datetime.datetime, endDate: datetime.datetime) -> int:
        return await self.retriever.get_transaction_count(startDate=startDate, endDate=endDate)

    async def retrieve_most_traded_token_transfer(self, startDate: datetime.datetime, endDate: datetime.datetime) -> TokenTransfer:
        mostTradedToken = await self.retriever.get_most_traded_token(startDate=startDate, endDate=endDate)
        query = (
            sqlalchemy.select([TokenTransfersTable, BlocksTable]).join(
                BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(BlocksTable.c.blockDate >= startDate)
            .where(BlocksTable.c.blockDate < endDate)
            .where(TokenTransfersTable.c.registryAddress == mostTradedToken.registryAddress)
            .where(TokenTransfersTable.c.tokenId == mostTradedToken.tokenId)
            .order_by(TokenTransfersTable.c.value.desc())
        )
        result = await self.retriever.database.execute(query=query, connection=None)
        latestTransferRow = result.first()
        countResult = await self.retriever.database.execute(query=sqlalchemy.select(sqlalchemy.func.count()).select_from(query), connection=None)
        transferCount = countResult.scalar()
        return TradedToken(
            latestTransfer=token_transfer_from_row(latestTransferRow),
            transferCount=transferCount,
        )

    async def get_collection_recent_sales(self, registryAddress: str, limit: int, offset: int) -> List[TokenTransfer]:
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=True,
            fieldFilters=[
                StringFieldFilter(
                    fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                IntegerFieldFilter(
                    fieldName=TokenTransfersTable.c.value.key, gt=0),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key,
                          direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

    # TODO remove startDate
    # TODO Normalize address
    async def get_collection_statistics(self, address: str) -> CollectionStatistics:
        itemCount = await self.retriever.get_collection_item_count(address=address)
        holderCount = len(await self.retriever.list_token_ownerships(fieldFilters=[StringFieldFilter(fieldName=TokenOwnershipsTable.c.registryAddress.key, eq=address)]))
        totalTradedVolume = 0
        startDate = 0
        collectionActivity = (await self.retriever.get_collection_activity(address=address, startDate=startDate, period=1))[0]
        return CollectionStatistics(
            itemCount=itemCount,
            holderCount=holderCount,
            saleCount=0,
            transferCount=0,
            totalTradeVolume=totalTradedVolume,
            lowestSaleLast24Hours=collectionActivity.minimumValue,
            highestSaleLast24Hours=collectionActivity.maximumValue,
            tradeVolume24Hours=collectionActivity.totalVolume,
        )

    async def get_collection_daily_activities(self, registryAddress: str) -> List[CollectionActivity]:
        collectionActivity = await self.retriever.get_collection_activity(address=registryAddress, startDate=None, period=90)
        return collectionActivity

    async def get_collection_token_recent_sales(self, registryAddress: str, tokenId: str, limit: int, offset: int) -> List[TokenTransfer]:
        tokenTransfers = await self.retriever.list_token_transfers(
            shouldIgnoreRegistryBlacklist=True,
            fieldFilters=[
                StringFieldFilter(
                    fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(
                    fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
                IntegerFieldFilter(
                    fieldName=TokenTransfersTable.c.value.key, gt=0),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key,
                          direction=Direction.DESCENDING)],
            limit=limit,
            offset=offset,
        )
        return tokenTransfers

    async def list_account_tokens(self, accountAddress: str, limit: int, offset: int) -> List[Token]:
        tokenSingleOwnerships = await self.retriever.list_token_ownerships(
            fieldFilters=[
                StringFieldFilter(
                    fieldName=TokenOwnershipsTable.c.ownerAddress.key, eq=accountAddress),
            ],
            orders=[Order(fieldName=TokenOwnershipsTable.c.transferDate.key,
                          direction=Direction.DESCENDING)],
            limit=limit+offset,
        )
        tokenMultiOwnerships = await self.retriever.list_token_multi_ownerships(
            fieldFilters=[
                StringFieldFilter(
                    fieldName=TokenMultiOwnershipsTable.c.ownerAddress.key, eq=accountAddress),
                StringFieldFilter(
                    fieldName=TokenMultiOwnershipsTable.c.quantity.key, ne=0),
            ],
            orders=[Order(fieldName=TokenMultiOwnershipsTable.c.latestTransferDate.key,
                          direction=Direction.DESCENDING)],
            limit=limit+offset,
        )
        tokenOwnershipTuples = [(ownership.registryAddress, ownership.tokenId,
                                 ownership.transferDate) for ownership in tokenSingleOwnerships]
        tokenOwnershipTuples += [(ownership.registryAddress, ownership.tokenId,
                                  ownership.latestTransferDate) for ownership in tokenMultiOwnerships]
        sortedTokenOwnershipTuples = sorted(
            tokenOwnershipTuples, key=lambda tuple: tuple[2], reverse=True)
        return [Token(registryAddress=registryAddress, tokenId=tokenId) for (registryAddress, tokenId, _) in sortedTokenOwnershipTuples]

    async def subscribe_email(self, email: str) -> None:
        await self.requester.post_json(url='https://www.getrevue.co/api/v2/subscribers', dataDict={'email': email.lower(), 'double_opt_in': False}, headers={'Authorization': f'Token {self.revueApiKey}'})

    async def update_token_metadata_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_metadata(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_ownership_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_ownership_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_token_ownership(self, registryAddress: str, tokenId: str) -> None:
        await self.tokenManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token_deferred(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata_deferred(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)
        await self.tokenManager.update_token_ownership_deferred(registryAddress=registryAddress, tokenId=tokenId)

    async def update_token(self, registryAddress: str, tokenId: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_token_metadata(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)
        await self.tokenManager.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId, shouldForce=shouldForce)

    async def update_collection_deferred(self, address: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_collection_deferred(address=address, shouldForce=shouldForce)

    async def update_collection(self, address: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_collection(address=address, shouldForce=shouldForce)

    async def update_collection_tokens_deferred(self, address: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_collection_tokens_deferred(address=address, shouldForce=shouldForce)

    async def update_collection_tokens(self, address: str, shouldForce: bool = False) -> None:
        await self.tokenManager.update_collection_tokens(address=address, shouldForce=shouldForce)

    async def update_activity_for_all_collections_deferred(self) -> None:
        await self.tokenManager.update_activity_for_all_collections_deferred()

    async def update_activity_for_all_collections(self) -> None:
        await self.tokenManager.update_activity_for_all_collections()

    async def update_activity_for_collection_deferred(self, registryAddress: str, startDate: datetime.datetime) -> None:
        await self.tokenManager.update_activity_for_collection_deferred(registryAddress=registryAddress, startDate=startDate)

    async def update_activity_for_collection(self, address: str, startDate: datetime.datetime) -> None:
        await self.tokenManager.update_activity_for_collection(registryAddress=address, startDate=startDate)

    async def get_collection_by_address(self, address: str) -> Collection:
        return await self.tokenManager.get_collection_by_address(address=address)

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str) -> TokenMetadata:
        return await self.tokenManager.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)

    async def list_collection_tokens_by_owner(self, address: str, ownerAddress: str) -> List[Token]:
        return await self.tokenManager.list_collection_tokens_by_owner(address=address, ownerAddress=ownerAddress)

    async def reprocess_owner_token_ownerships(self, accountAddress: str) -> None:
        await self.tokenManager.reprocess_owner_token_ownerships(ownerAddress=accountAddress)

    async def receive_new_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())

    async def receive_new_blocks(self) -> None:
        latestBlocks = await self.retriever.list_blocks(orders=[Order(fieldName=BlocksTable.c.blockNumber.key, direction=Direction.DESCENDING)], limit=1)
        latestProcessedBlockNumber = latestBlocks[0].blockNumber
        latestBlockNumber = await self.blockProcessor.get_latest_block_number()
        logging.info(
            f'Scheduling messages for processing blocks from {latestProcessedBlockNumber} to {latestBlockNumber}')
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
        logging.info(
            f'Scheduling messages for reprocessing {len(blockNumbers)} blocks')
        await self.process_blocks_deferred(blockNumbers=blockNumbers, shouldSkipProcessingTokens=True)

    async def process_blocks_deferred(self, blockNumbers: Sequence[int], shouldSkipProcessingTokens: Optional[bool] = None, delaySeconds: int = 0) -> None:
        messages = [ProcessBlockMessageContent(
            blockNumber=blockNumber, shouldSkipProcessingTokens=shouldSkipProcessingTokens).to_message() for blockNumber in blockNumbers]
        await self.workQueue.send_messages(messages=messages, delaySeconds=delaySeconds)

    async def process_block_deferred(self, blockNumber: int, shouldSkipProcessingTokens: Optional[bool] = None, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=ProcessBlockMessageContent(blockNumber=blockNumber, shouldSkipProcessingTokens=shouldSkipProcessingTokens).to_message(), delaySeconds=delaySeconds)

    async def process_block(self, blockNumber: int, shouldSkipProcessingTokens: Optional[bool] = None) -> None:
        processedBlock = await self.blockProcessor.process_block(blockNumber=blockNumber)
        logging.info(
            f'Found {len(processedBlock.retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        collectionTokenIds = await self._save_processed_block(processedBlock=processedBlock)
        logging.info(
            f'Found {len(collectionTokenIds)} changed tokens in block #{blockNumber}')
        collectionAddresses = list(
            set(registryAddress for registryAddress, _ in collectionTokenIds))
        logging.info(
            f'Found {len(collectionAddresses)} changed collections in block #{blockNumber}')
        await self.tokenManager.update_token_ownerships_deferred(collectionTokenIds=collectionTokenIds)
        if not shouldSkipProcessingTokens:
            await self.tokenManager.update_collections_deferred(addresses=collectionAddresses)
            await self.tokenManager.update_token_metadatas_deferred(collectionTokenIds=collectionTokenIds)

    @staticmethod
    def _uniqueness_tuple_from_token_transfer(tokenTransfer: TokenTransfer) -> Tuple[str, str, str, str, str, int, int]:
        return (tokenTransfer.transactionHash, tokenTransfer.registryAddress, tokenTransfer.tokenId, tokenTransfer.fromAddress, tokenTransfer.toAddress, tokenTransfer.blockNumber, tokenTransfer.amount)

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
                fieldFilters=[
                    StringFieldFilter(
                        fieldName=TokenTransfersTable.c.blockNumber.key, eq=processedBlock.blockNumber),
                ], shouldIgnoreRegistryBlacklist=True
            )
            existingTuplesTransferMap = {self._uniqueness_tuple_from_token_transfer(
                tokenTransfer=tokenTransfer): tokenTransfer for tokenTransfer in existingTokenTransfers}
            existingTuples = set(existingTuplesTransferMap.keys())
            retrievedTupleTransferMaps = {self._uniqueness_tuple_from_token_transfer(
                tokenTransfer=tokenTransfer): tokenTransfer for tokenTransfer in processedBlock.retrievedTokenTransfers}
            retrievedTuples = set(retrievedTupleTransferMaps.keys())
            tokenTransferIdsToDelete = []
            for existingTuple, existingTokenTransfer in existingTuplesTransferMap.items():
                if existingTuple in retrievedTuples:
                    continue
                tokenTransferIdsToDelete.append(
                    existingTokenTransfer.tokenTransferId)
                changedTokens.add(
                    (existingTokenTransfer.registryAddress, existingTokenTransfer.tokenId))
            await self.saver.delete_token_transfers(connection=connection, tokenTransferIds=tokenTransferIdsToDelete)
            retrievedTokenTransfersToSave = []
            for retrievedTuple, retrievedTokenTransfer in retrievedTupleTransferMaps.items():
                if retrievedTuple in existingTuples:
                    continue
                retrievedTokenTransfersToSave.append(retrievedTokenTransfer)
                changedTokens.add(
                    (retrievedTokenTransfer.registryAddress, retrievedTokenTransfer.tokenId))
            await self.saver.create_token_transfers(connection=connection, retrievedTokenTransfers=retrievedTokenTransfersToSave)
            logging.info(
                f'Saving transfers for block {processedBlock.blockNumber}: saved {len(retrievedTokenTransfersToSave)}, deleted {len(tokenTransferIdsToDelete)}, kept {len(existingTokenTransfers) - len(tokenTransferIdsToDelete)}')
        return list(changedTokens)
