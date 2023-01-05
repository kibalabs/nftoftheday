from typing import Set
from typing import Tuple

from core import logging
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter

from notd.messages import UpdateTokenStakingMessageContent
from notd.messages import UpdateTokenStakingsForCollectionMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenStakingsTable
from notd.token_staking_processor import TokenStakingProcessor


class TokenStakingManager:

    def __init__(self, retriever: Retriever,saver: Saver, tokenQueue: SqsMessageQueue, workQueue: SqsMessageQueue, tokenStakingProcessor: TokenStakingProcessor) -> None:
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

    async def update_token_stakings_for_all_collections_deferred(self) -> None:
        for index, stakingAddress in enumerate(GALLERY_COLLECTIONS):
            await self.workQueue.send_message(message=UpdateTokenStakingsForCollectionMessageContent(address=stakingAddress).to_message(), delaySeconds=index*20)

    async def update_token_stakings_for_collection_deferred(self, address: str) -> None:
        await self.workQueue.send_message(message=UpdateTokenStakingsForCollectionMessageContent(address=address).to_message())

    async def update_token_stakings_for_collection(self, address: str) -> None:
        retrievedTokenStakings = await self.tokenStakingProcessor.retrieve_token_stakings(registryAddress=address)
        async with self.saver.create_transaction() as connection:
            currentTokenStakings = await self.retriever.list_token_stakings(fieldFilters=[
                StringFieldFilter(fieldName=TokenStakingsTable.c.registryAddress.key, eq=address)
            ])
            currentTokenStakingIds = [tokenStaking.tokenStakingId for tokenStaking in currentTokenStakings]
            logging.info(f'Deleting {len(currentTokenStakingIds)} existing stakings')
            await self.saver.delete_token_stakings(tokenStakingIds=currentTokenStakingIds, connection=connection)
            logging.info(f'Saving {len(retrievedTokenStakings)} stakings')
            await self.saver.create_token_stakings(retrievedTokenStakings=retrievedTokenStakings, connection=connection)
