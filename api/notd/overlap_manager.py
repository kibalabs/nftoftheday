from core.util import chain_util

from notd.store.schema import TokenCollectionOverlapsTable
from notd.collection_overlap_processor import CollectionOverlapProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver


class OverlapManager:

    def __init__(self, retriever: Retriever, saver: Saver, collectionOverlapProcessor: CollectionOverlapProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.collectionOverlapProcessor = collectionOverlapProcessor

    async def update_overlap_for_collection(self, galleryAddress: str) -> None:
        galleryAddress = chain_util.normalize_address(galleryAddress)
        retrievedCollectionOverlaps = await self.collectionOverlapProcessor.calculate_collection_overlap(address=galleryAddress)
        async with self.saver.create_transaction() as connection:
            existingCollectionOverlapQuery = (
                TokenCollectionOverlapsTable.select()
                .with_only_columns([TokenCollectionOverlapsTable.c.collectionOverlapId])
                .where(TokenCollectionOverlapsTable.c.galleryAddress == galleryAddress)
            )
            existingCollectionOverlapResult = await self.retriever.database.execute(query=existingCollectionOverlapQuery, connection=connection)
            collectionOverlapIdsToDelete = list(existingCollectionOverlapResult)
            await self.saver.delete_collection_overlaps(collectionOverlapIds=collectionOverlapIdsToDelete, connection=connection)
            await self.saver.create_collection_overlaps(retrievedCollectionOverlaps=retrievedCollectionOverlaps, connection=connection)
