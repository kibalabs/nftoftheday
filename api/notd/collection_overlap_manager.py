import logging

from core.queues.message_queue import MessageQueue
from core.queues.model import Message
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import list_util

from notd.collection_overlap_processor import CollectionOverlapProcessor
from notd.messages import RefreshAllCollectionOverlapsMessageContent
from notd.messages import RefreshCollectionOverlapMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionOverlapsTable


class CollectionOverlapManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: MessageQueue[Message], collectionOverlapProcessor: CollectionOverlapProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.collectionOverlapProcessor = collectionOverlapProcessor
        self.workQueue = workQueue

    async def refresh_overlaps_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=RefreshAllCollectionOverlapsMessageContent().to_message())

    async def refresh_overlaps_for_all_collections(self) -> None:
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_overlap_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_overlap_for_collection_deferred(self, registryAddress: str) -> None:
        await self.workQueue.send_message(message=RefreshCollectionOverlapMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_overlap_for_collection(self, registryAddress: str) -> None:
        registryAddress = chain_util.normalize_address(registryAddress)
        retrievedCollectionOverlaps = await self.collectionOverlapProcessor.calculate_collection_overlap(registryAddress=registryAddress)
        async with self.saver.create_transaction() as connection:
            # TODO(krishan711): this would be more efficient if only changed ones are deleted and re-saved
            currentCollectionOverlaps = await self.retriever.list_collection_overlaps(fieldFilters=[
                StringFieldFilter(fieldName=TokenCollectionOverlapsTable.c.registryAddress.key, eq=registryAddress),
            ], connection=connection)
            collectionOverlapIdsToDelete = {collectionOverlaps.collectionOverlapId for collectionOverlaps in currentCollectionOverlaps}
            logging.info(f'Deleting {len(collectionOverlapIdsToDelete)} existing collection overlaps')
            for chunkedIds in list_util.generate_chunks(lst=list(collectionOverlapIdsToDelete), chunkSize=100):
                await self.saver.delete_collection_overlaps(collectionOverlapIds=chunkedIds, connection=connection)
            logging.info(f'Saving {len(retrievedCollectionOverlaps)} overlaps')
            await self.saver.create_collection_overlaps(retrievedCollectionOverlaps=retrievedCollectionOverlaps, connection=connection)
