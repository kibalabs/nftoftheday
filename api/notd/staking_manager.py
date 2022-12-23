from core import logging
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter

from notd.messages import RefreshStakingsForCollectionMessageContent
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenStakingsTable
from notd.token_staking_processor import TokenStakingProcessor


class StakingManager:

    def __init__(self, retriever: Retriever,saver: Saver, workQueue: SqsMessageQueue, tokenStakingProcessor: TokenStakingProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.workQueue = workQueue
        self.tokenStakingProcessor = tokenStakingProcessor

    async def refresh_collection_stakings_deferred(self, address: str) -> None:
        await self.workQueue.send_message(message=RefreshStakingsForCollectionMessageContent(address=address).to_message())

    async def refresh_collection_stakings(self, address: str) -> None:
        retrievedTokenStakings = await self.tokenStakingProcessor.calculate_staked_creepz_tokens(registryAddress=address)
        async with self.saver.create_transaction() as connection:
            currentTokenStakings = await self.retriever.list_token_stakings(fieldFilters=[
                StringFieldFilter(fieldName=TokenStakingsTable.c.registryAddress.key, eq=address)
            ],
            )
            currentTokenStakingIds = [tokenStaking.tokenStakingId for tokenStaking in currentTokenStakings]
            logging.info(f'Deleting {len(currentTokenStakingIds)} existing stakings')
            await self.saver.delete_token_stakings(tokenStakingIds=currentTokenStakingIds, connection=connection)
            logging.info(f'Saving {len(retrievedTokenStakings)} stakings')
            await self.saver.create_token_stakings(retrievedTokenStakings=retrievedTokenStakings, connection=connection)
