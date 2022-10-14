import logging

from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import list_util

from notd.badge_processor import BadgeProcessor
from notd.messages import RefreshAllUserBadgesMessageContent
from notd.messages import RefreshUserBadgesForCollectionMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import CollectionBadgeHoldersTable


class BadgeManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: SqsMessageQueue, badgeProcessor: BadgeProcessor) -> None:
        self.retriever= retriever
        self.saver= saver
        self.workQueue= workQueue
        self.badgeProcessor= badgeProcessor

    async def refresh_all_users_badges_deferred(self):
        await self.workQueue.send_message(message=RefreshAllUserBadgesMessageContent().to_message())

    async def refresh_all_users_badges(self):
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_user_badges_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_user_badges_for_collection_deferred(self, registryAddress: str):
        await self.workQueue.send_message(message=RefreshUserBadgesForCollectionMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_user_badges_for_collection(self, registryAddress: str):
        registryAddress = chain_util.normalize_address(registryAddress)
        # NOTE(Femi-Ogunkola): Figure out how to map to rudeboy processor and get all the badge holders at once
        retrievedCollectionBadgeHolders = await self.badgeProcessor.calculate_badges(registryAddress=registryAddress)
        async with self.saver.create_transaction() as connection:
            # TODO(krishan711): this would be more efficient if only changed ones are deleted and re-saved
            currentCollectionBadgeHolders = await self.retriever.list_collection_badge_holders(fieldFilters=[
                StringFieldFilter(fieldName=CollectionBadgeHoldersTable.c.registryAddress.key, eq=registryAddress),
            ], connection=connection)
            collectionBadgeHoldersToDelete = {collectionBadgeHolders.collectionBadgeHolderId for collectionBadgeHolders in currentCollectionBadgeHolders}
            logging.info(f'Deleting {len(collectionBadgeHoldersToDelete)} existing gallery badges')
            for chunkedIds in list_util.generate_chunks(lst=list(collectionBadgeHoldersToDelete), chunkSize=100):
                await self.saver.delete_collection_badge_holders(collectionBadgeHolderIds=chunkedIds, connection=connection)
            logging.info(f'Saving {len(retrievedCollectionBadgeHolders)} gallery badges')
            await self.saver.create_collection_badge_holders(retrievedCollectionBadgeHolders=retrievedCollectionBadgeHolders, connection=connection)
