import asyncio
import datetime
import random
from typing import List
from typing import Set
from typing import Tuple

import sqlalchemy
from core import logging
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from core.util import list_util

from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_processor import CollectionDoesNotExist
from notd.collection_processor import CollectionProcessor
from notd.date_util import date_hour_from_datetime
from notd.date_util import generate_clock_hour_intervals
from notd.messages import UpdateActivityForAllCollectionsMessageContent
from notd.messages import UpdateActivityForCollectionMessageContent
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateCollectionTokenAttributesMessageContent
from notd.messages import UpdateCollectionTokensMessageContent
from notd.messages import UpdateListingsForAllCollections
from notd.messages import UpdateListingsForCollection
from notd.messages import UpdateTokenAttributesForAllCollectionsMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.messages import UpdateTokenOwnershipMessageContent
from notd.model import GALLERY_COLLECTIONS
from notd.model import Collection
from notd.model import RetrievedTokenMultiOwnership
from notd.model import Token
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.token_attributes_processor import TokenAttributeProcessor
from notd.token_listing_processor import TokenListingProcessor
from notd.token_metadata_processor import TokenDoesNotExistException
from notd.token_metadata_processor import TokenHasNoMetadataException
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import NoOwnershipException
from notd.token_ownership_processor import TokenOwnershipProcessor


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
