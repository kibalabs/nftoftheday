from typing import Set
from typing import Tuple

import sqlalchemy
from core import logging
from core.queues.message_queue import MessageQueue
from core.queues.model import Message
from core.store.retriever import StringFieldFilter

from notd.messages import RefreshTokenStakingsForStakingAddressMessageContent
from notd.messages import UpdateTokenStakingMessageContent
from notd.model import STAKING_ADDRESSES
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenStakingsTable
from notd.store.schema import TokenTransfersTable
from notd.token_staking_processor import TokenStakingProcessor


class TokenStakingManager:

    def __init__(self, retriever: Retriever,saver: Saver, tokenQueue: MessageQueue[Message], workQueue: MessageQueue[Message], tokenStakingProcessor: TokenStakingProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.workQueue = workQueue
        self.tokenQueue = tokenQueue
        self.tokenStakingProcessor = tokenStakingProcessor

    async def update_token_stakings_deferred(self, stakingCollectionTokenIds: Set[Tuple[str, str]]) -> None:
        if len(stakingCollectionTokenIds) == 0:
            return
        uniqueCollectionTokenIds = set(stakingCollectionTokenIds)
        messages = [UpdateTokenStakingMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message() for (registryAddress, tokenId) in uniqueCollectionTokenIds]
        await self.tokenQueue.send_messages(messages=messages)

    async def update_token_staking_deferred(self, registryAddress: str, tokenId: str) -> None:
        await self.tokenQueue.send_message(message=UpdateTokenStakingMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_token_staking(self, registryAddress: str, tokenId: str) -> None:
        retrievedTokenStaking = await self.tokenStakingProcessor.retrieve_updated_token_staking(registryAddress=registryAddress, tokenId=tokenId)
        async with self.saver.create_transaction() as connection:
            currentTokenStakings = await self.retriever.list_token_stakings(fieldFilters=[
                StringFieldFilter(fieldName=TokenStakingsTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenStakingsTable.c.tokenId.key, eq=tokenId)],
                limit=1
            )
            if len(currentTokenStakings) > 0:
                currentTokenStakingId = currentTokenStakings[0].tokenStakingId
                logging.info(f'Deleting existing stakings for registryAddress: {registryAddress}, tokenId: {tokenId}')
                await self.saver.delete_token_staking(tokenStakingId=currentTokenStakingId, connection=connection)
            if retrievedTokenStaking:
                logging.info(f'Saving stakings for registryAddress: {registryAddress}, tokenId: {tokenId}')
                await self.saver.create_token_staking(retrievedTokenStaking=retrievedTokenStaking, connection=connection)

    async def refresh_token_stakings_for_all_staking_addresses_deferred(self) -> None:
        for index, stakingAddress in enumerate(STAKING_ADDRESSES):
            await self.workQueue.send_message(message=RefreshTokenStakingsForStakingAddressMessageContent(stakingAddress=stakingAddress).to_message(), delaySeconds=index*20)

    async def refresh_token_stakings_for_staking_address_deferred(self, stakingAddress: str) -> None:
        await self.workQueue.send_message(message=RefreshTokenStakingsForStakingAddressMessageContent(stakingAddress=stakingAddress).to_message())

    async def refresh_token_stakings_for_staking_address(self, stakingAddress: str) -> None:
        ownerQuery = (
        sqlalchemy.select(TokenTransfersTable.c.fromAddress.distinct())
        .where((TokenTransfersTable.c.toAddress == stakingAddress))
        )
        stakerAddressesResult = await self.retriever.database.execute(query=ownerQuery)
        stakerAddresses = [stakerAddress for stakerAddress, in list(stakerAddressesResult)]
        async with self.saver.create_transaction() as connection:
            for stakerAddress in stakerAddresses:
                retrievedTokenStakings = await self.tokenStakingProcessor.retrieve_owner_token_stakings(ownerAddress=stakerAddress, stakingAddress=stakingAddress)
                query = (
                    sqlalchemy.select(TokenStakingsTable.c.tokenStakingId)
                    .where((TokenStakingsTable.c.ownerAddress == stakerAddress))
                )
                result = await self.retriever.database.execute(query=query, connection=connection)
                tokenStakingIdsToDelete = [tokenStakingId for tokenStakingId, in result]
                logging.info(f'Deleting {len(tokenStakingIdsToDelete)} tokenStaking.')
                await self.saver.delete_token_stakings(tokenStakingIds=tokenStakingIdsToDelete, connection=connection)
                logging.info(f'Saving {len(retrievedTokenStakings)} tokenStaking.')
                await self.saver.create_token_stakings(retrievedTokenStakings=retrievedTokenStakings, connection=connection)
