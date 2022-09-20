from core.queues.sqs_message_queue import SqsMessageQueue
from core.util import chain_util

from notd.collection_overlap_processor import CollectionOverlapProcessor
from notd.messages import RefreshAllCollectionOverlapMessageContent
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

    async def refresh_overlap_for_all_collections_deferred(self):
        await self.workQueue.send_message(message=RefreshAllCollectionOverlapMessageContent().to_message())

    async def refresh_overlap_for_all_collections(self):
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_overlap_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_overlap_for_collection_deferred(self, registryAddress: str):
        await self.workQueue.send_message(message=RefreshCollectionOverlapMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_overlap_for_collection(self, registryAddress: str) -> None:
        registryAddress = chain_util.normalize_address(registryAddress)
        retrievedCollectionOverlaps = await self.collectionOverlapProcessor.calculate_collection_overlap(address=registryAddress)
        async with self.saver.create_transaction() as connection:
            existingCollectionOverlapQuery = (
                TokenCollectionOverlapsTable.select()
                .with_only_columns([TokenCollectionOverlapsTable.c.collectionOverlapId])
                .where(TokenCollectionOverlapsTable.c.galleryAddress == registryAddress)
            )
            existingCollectionOverlapResult = await self.retriever.database.execute(query=existingCollectionOverlapQuery, connection=connection)
            collectionOverlapIdsToDelete = {row[0] for row in existingCollectionOverlapResult}
            await self.saver.delete_collection_overlaps(collectionOverlapIds=collectionOverlapIdsToDelete, connection=connection)
            await self.saver.create_collection_overlaps(retrievedCollectionOverlaps=retrievedCollectionOverlaps, connection=connection)
