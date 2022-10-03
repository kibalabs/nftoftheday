import asyncio
import datetime
from typing import List
from typing import Tuple

from core import logging
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import list_util

from notd.collection_manager import CollectionManager
from notd.lock_manager import LockManager
from notd.messages import UpdateTokenOwnershipMessageContent
from notd.model import Collection
from notd.model import RetrievedTokenMultiOwnership
from notd.model import Token
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.token_ownership_processor import NoOwnershipException
from notd.token_ownership_processor import TokenOwnershipProcessor


class OwnershipManager:

    def __init__(self, saver: Saver, retriever: Retriever, tokenQueue: SqsMessageQueue, collectionManager: CollectionManager, lockManager: LockManager, tokenOwnershipProcessor: TokenOwnershipProcessor) -> None:
        self.saver = saver
        self.retriever = retriever
        self.tokenQueue = tokenQueue
        self.collectionManager = collectionManager
        self.lockManager = lockManager
        self.tokenOwnershipProcessor = tokenOwnershipProcessor

    async def update_token_ownerships_deferred(self, collectionTokenIds: List[Tuple[str, str]]) -> None:
        if len(collectionTokenIds) == 0:
            return
        collectionTokenIds = set(collectionTokenIds)
        messages = [UpdateTokenOwnershipMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message() for (registryAddress, tokenId) in collectionTokenIds]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_token_ownership_deferred(self, registryAddress: str, tokenId: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        await self.tokenQueue.send_message(message=UpdateTokenOwnershipMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_token_ownership(self, registryAddress: str, tokenId: str):
        registryAddress = chain_util.normalize_address(value=registryAddress)
        collection = await self.collectionManager.get_collection_by_address(address=registryAddress)
        if collection.doesSupportErc721:
            await self._update_token_single_ownership(registryAddress=registryAddress, tokenId=tokenId)
        elif collection.doesSupportErc1155:
            await self._update_token_multi_ownership(registryAddress=registryAddress, tokenId=tokenId)

    async def _update_token_single_ownership(self, registryAddress: str, tokenId: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        async with self.lockManager.with_lock(name=f"update-single-ownership-{registryAddress}-{tokenId}", timeoutSeconds=5, expirySeconds=300):
            async with self.saver.create_transaction() as connection:
                try:
                    tokenOwnership = await self.retriever.get_token_ownership_by_registry_address_token_id(connection=connection, registryAddress=registryAddress, tokenId=tokenId)
                except NotFoundException:
                    tokenOwnership = None
                try:
                    retrievedTokenOwnership = await self.tokenOwnershipProcessor.calculate_token_single_ownership(registryAddress=registryAddress, tokenId=tokenId)
                except NoOwnershipException:
                    logging.error(f'No ownership found for {registryAddress}:{tokenId}')
                    return
                if tokenOwnership:
                    await self.saver.update_token_ownership(connection=connection, tokenOwnershipId=tokenOwnership.tokenOwnershipId, ownerAddress=retrievedTokenOwnership.ownerAddress, transferDate=retrievedTokenOwnership.transferDate, transferValue=retrievedTokenOwnership.transferValue, transferTransactionHash=retrievedTokenOwnership.transferTransactionHash)
                else:
                    await self.saver.create_token_ownership(connection=connection, registryAddress=retrievedTokenOwnership.registryAddress, tokenId=retrievedTokenOwnership.tokenId, ownerAddress=retrievedTokenOwnership.ownerAddress, transferDate=retrievedTokenOwnership.transferDate, transferValue=retrievedTokenOwnership.transferValue, transferTransactionHash=retrievedTokenOwnership.transferTransactionHash)

    @staticmethod
    def _uniqueness_tuple_from_token_multi_ownership(retrievedTokenMultiOwnership: RetrievedTokenMultiOwnership) -> Tuple[str, str, str, int, int, datetime.datetime, str]:
        return (retrievedTokenMultiOwnership.registryAddress, retrievedTokenMultiOwnership.tokenId, retrievedTokenMultiOwnership.ownerAddress, retrievedTokenMultiOwnership.quantity, retrievedTokenMultiOwnership.averageTransferValue, retrievedTokenMultiOwnership.latestTransferDate, retrievedTokenMultiOwnership.latestTransferTransactionHash)

    async def _update_token_multi_ownership(self, registryAddress: str, tokenId: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        latestTransfers = await self.retriever.list_token_transfers(fieldFilters=[
            StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
            StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
        ], orders=[Order(fieldName=BlocksTable.c.updatedDate.key, direction=Direction.DESCENDING)], limit=1)
        if len(latestTransfers) == 0:
            return
        latestTransfer = latestTransfers[0]
        latestOwnerships = await self.retriever.list_token_multi_ownerships(fieldFilters=[
            StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.registryAddress.key, eq=registryAddress),
            StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.tokenId.key, eq=tokenId),
        ], orders=[Order(fieldName=TokenMultiOwnershipsTable.c.updatedDate.key, direction=Direction.DESCENDING)], limit=1)
        latestOwnership = latestOwnerships[0] if len(latestOwnerships) > 0 else None
        if latestOwnership is not None and latestOwnership.updatedDate > latestTransfer.updatedDate:
            logging.info(f'Skipping updating token_multi_ownership because last record ({latestOwnership.updatedDate}) is newer that last transfer update ({latestTransfer.updatedDate})')
            return
        retrievedTokenMultiOwnerships = await self.tokenOwnershipProcessor.calculate_token_multi_ownership(registryAddress=registryAddress, tokenId=tokenId)
        async with self.lockManager.with_lock(name=f"update-multi-ownership-{registryAddress}-{tokenId}", timeoutSeconds=5, expirySeconds=300):
            async with self.saver.create_transaction() as connection:
                currentTokenMultiOwnerships = await self.retriever.list_token_multi_ownerships(connection=connection, fieldFilters=[
                    StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.tokenId.key, eq=tokenId),
                ])
                existingOwnershipTuplesMap = {self._uniqueness_tuple_from_token_multi_ownership(retrievedTokenMultiOwnership=tokenMultiOwnership): tokenMultiOwnership for tokenMultiOwnership in currentTokenMultiOwnerships}
                existingOwnershipTuples = set(existingOwnershipTuplesMap.keys())
                retrievedOwnershipTuplesMaps = {self._uniqueness_tuple_from_token_multi_ownership(retrievedTokenMultiOwnership=retrievedTokenMultiOwnership): retrievedTokenMultiOwnership for retrievedTokenMultiOwnership in retrievedTokenMultiOwnerships}
                retrievedOwnershipTuples = set(retrievedOwnershipTuplesMaps.keys())
                tokenMultiOwnershipIdsToDelete = []
                for existingTuple, existingTokenMultiOwnership in existingOwnershipTuplesMap.items():
                    if existingTuple in retrievedOwnershipTuples:
                        continue
                    tokenMultiOwnershipIdsToDelete.append(existingTokenMultiOwnership.tokenMultiOwnershipId)
                await self.saver.delete_token_multi_ownerships(connection=connection, tokenMultiOwnershipIds=tokenMultiOwnershipIdsToDelete)
                retrievedTokenMultiOwnershipsToSave = []
                for retrievedTuple, retrievedTokenMultiOwnership in retrievedOwnershipTuplesMaps.items():
                    if retrievedTuple in existingOwnershipTuples:
                        continue
                    retrievedTokenMultiOwnershipsToSave.append(retrievedTokenMultiOwnership)
                await self.saver.create_token_multi_ownerships(connection=connection, retrievedTokenMultiOwnerships=retrievedTokenMultiOwnershipsToSave)
                logging.info(f'Saving multi ownerships: saved {len(retrievedTokenMultiOwnershipsToSave)}, deleted {len(tokenMultiOwnershipIdsToDelete)}, kept {len(existingOwnershipTuples - retrievedOwnershipTuples) - len(tokenMultiOwnershipIdsToDelete)}')
                # NOTE(krishan711): if nothing changed, force update one so that it doesn't update again
                if len(existingOwnershipTuplesMap) > 0 and len(retrievedTokenMultiOwnershipsToSave) == 0 and len(tokenMultiOwnershipIdsToDelete) == 0:
                    firstOwnership = list(existingOwnershipTuplesMap.values())[0]
                    await self.saver.update_token_multi_ownership(connection=connection, tokenMultiOwnershipId=firstOwnership.tokenMultiOwnershipId, ownerAddress=firstOwnership.ownerAddress)

    async def list_collection_tokens_by_owner(self, address: str, ownerAddress: str, collection: Collection) -> List[Token]:
        address = chain_util.normalize_address(value=address)
        tokens = []
        if collection.doesSupportErc721:
            tokenOwnerships = await self.retriever.list_token_ownerships(fieldFilters=[
                StringFieldFilter(fieldName=TokenOwnershipsTable.c.registryAddress.key, eq=address),
                StringFieldFilter(fieldName=TokenOwnershipsTable.c.ownerAddress.key, eq=ownerAddress),
            ])
            tokens += [Token(registryAddress=tokenOwnership.registryAddress, tokenId=tokenOwnership.tokenId) for tokenOwnership in tokenOwnerships]
        elif collection.doesSupportErc1155:
            tokenMultiOwnerships = await self.retriever.list_token_multi_ownerships(fieldFilters=[
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.registryAddress.key, eq=address),
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.ownerAddress.key, eq=ownerAddress),
                StringFieldFilter(fieldName=TokenMultiOwnershipsTable.c.quantity.key, eq=0),
            ])
            tokens += [Token(registryAddress=tokenMultiOwnership.registryAddress, tokenId=tokenMultiOwnership.tokenId) for tokenMultiOwnership in tokenMultiOwnerships]
        return tokens

    async def reprocess_owner_token_ownerships(self, ownerAddress: str) -> None:
        tokenTransfers = await self.retriever.list_token_transfers(fieldFilters=[StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=ownerAddress)])
        collectionTokenIds = list({(transfer.registryAddress, transfer.tokenId) for transfer in tokenTransfers})
        logging.info(f'Refreshing {len(collectionTokenIds)} ownerships')
        for collectionTokenIdChunk in list_util.generate_chunks(lst=collectionTokenIds, chunkSize=10):
            await asyncio.gather(*[self.update_token_ownership(registryAddress=registryAddress, tokenId=tokenId) for (registryAddress, tokenId) in collectionTokenIdChunk])
        return collectionTokenIds
