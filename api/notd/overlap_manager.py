import logging
from core.queues.sqs_message_queue import SqsMessageQueue
from core.util import chain_util
from core.util import list_util
from core.store.retriever import StringFieldFilter


from notd.collection_overlap_processor import CollectionOverlapProcessor
from notd.messages import RefreshAllCollectionOverlapsMessageContent
from notd.messages import RefreshCollectionOverlapMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionOverlapsTable


class OverlapManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: SqsMessageQueue, collectionOverlapProcessor: CollectionOverlapProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.collectionOverlapProcessor = collectionOverlapProcessor
        self.workQueue = workQueue

    async def refresh_overlaps_for_all_collections_deferred(self):
        await self.workQueue.send_message(message=RefreshAllCollectionOverlapsMessageContent().to_message())

    async def refresh_overlaps_for_all_collections(self):
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_overlap_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_overlap_for_collection_deferred(self, registryAddress: str):
        await self.workQueue.send_message(message=RefreshCollectionOverlapMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_overlap_for_collection(self, registryAddress: str) -> None:
        registryAddress = chain_util.normalize_address(registryAddress)
        retrievedCollectionOverlaps = await self.collectionOverlapProcessor.calculate_collection_overlap(address=registryAddress)
        async with self.saver.create_transaction() as connection:
            currentCollectionOverlaps = await self.retriever.list_collection_overlaps(fieldFilters=[
                StringFieldFilter(fieldName=TokenCollectionOverlapsTable.c.registryAddress.key, eq=registryAddress),
            ], connection=connection)
            collectionOverlapIdsToDelete = {collectionOverlaps.collectionOverlapId for collectionOverlaps in currentCollectionOverlaps}
            logging.info(f'Deleting {len(collectionOverlapIdsToDelete)} existing collection overlaps')
            for chunkedIds in list_util.generate_chunks(lst=list(collectionOverlapIdsToDelete), chunkSize=100):
                await self.saver.delete_collection_overlaps(collectionOverlapIds=chunkedIds, connection=connection)
            logging.info(f'Saving {len(retrievedCollectionOverlaps)} overlaps')
            await self.saver.create_collection_overlaps(retrievedCollectionOverlaps=retrievedCollectionOverlaps, connection=connection)
