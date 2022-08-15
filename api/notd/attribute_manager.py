from core import logging
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.messages import UpdateCollectionTokenAttributesMessageContent
from notd.messages import UpdateTokenAttributesForAllCollectionsMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenMetadatasTable
from notd.token_attributes_processor import TokenAttributeProcessor


class AttributeManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, tokenQueue: SqsMessageQueue, tokenAttributeProcessor: TokenAttributeProcessor) -> None:
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenQueue = tokenQueue
        self.tokenAttributeProcessor = tokenAttributeProcessor

    async def update_token_attributes_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=UpdateTokenAttributesForAllCollectionsMessageContent().to_message())

    async def update_token_attributes_for_all_collections(self) -> None:
        startDate = date_util.datetime_from_now()
        latestUpdate = await self.retriever.get_latest_update_by_key_name(key='token_attributes')
        latestProcessedDate = latestUpdate.date
        logging.info(f'Finding changed tokens since {latestProcessedDate}')
        updatedTokenMetadatasQuery = (
            TokenMetadatasTable.select()
            .with_only_columns([TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId])
            .where(TokenMetadatasTable.c.registryAddress.in_(GALLERY_COLLECTIONS))
            .where(TokenMetadatasTable.c.updatedDate >= latestProcessedDate)
        )
        updatedTokenMetadatasQueryResult = await self.retriever.database.execute(query=updatedTokenMetadatasQuery)
        updatedTokenMetadatas = set(updatedTokenMetadatasQueryResult)
        logging.info(f'Scheduling processing for {len(updatedTokenMetadatas)} changed tokens')
        messages = [UpdateCollectionTokenAttributesMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message() for (registryAddress, tokenId) in updatedTokenMetadatas]
        await self.tokenQueue.send_messages(messages=messages)
        await self.saver.update_latest_update(latestUpdateId=latestUpdate.latestUpdateId, date=startDate)

    async def update_collection_token_attributes_deferred(self, registryAddress: str, tokenId: str) -> None:
        await self.tokenQueue.send_message(message=UpdateCollectionTokenAttributesMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())

    async def update_collection_token_attributes(self, registryAddress: str, tokenId: str) -> None:
        tokenAttributes = await self.tokenAttributeProcessor.get_token_attributes(registryAddress=registryAddress, tokenId=tokenId)
        logging.info(f'Retrieved {len(tokenAttributes)} attributes')
        # TODO(krishan711): change this to not delete existing. should add / remove / update changed only
        async with self.saver.create_transaction() as connection:
            currentTokenAttributes = await self.retriever.list_token_attributes(fieldFilters=[
                StringFieldFilter(fieldName=TokenAttributesTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenAttributesTable.c.tokenId.key, eq=tokenId)
            ], connection=connection)
            currentTokenAttributeIds = [tokenAttributes.tokenAttributeId for tokenAttributes in currentTokenAttributes]
            logging.info(f'Deleting {len(currentTokenAttributeIds)} existing attributes')
            await self.saver.delete_token_attributes(tokenAttributeIds=currentTokenAttributeIds, connection=connection)
            logging.info(f'Saving {len(tokenAttributes)} attributes')
            await self.saver.create_token_attributes(retrievedTokenAttributes=tokenAttributes, connection=connection)
