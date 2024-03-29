import datetime
from typing import List

from core import logging
from core.queues.message_queue import MessageQueue
from core.queues.message_queue_processor import MessageNeedsReprocessingException
from core.queues.model import Message
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.lock_manager import LockTimeoutException
from notd.messages import RefreshListingsForAllCollections
from notd.messages import RefreshListingsForCollectionMessageContent
from notd.messages import UpdateListingsForAllCollections
from notd.messages import UpdateListingsForCollection
from notd.model import GALLERY_COLLECTIONS
from notd.model import TokenListing
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import OrderedTokenListingsView
from notd.store.schema_conversions import token_listing_from_row
from notd.token_listing_processor import TokenListingProcessor


class ListingManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: MessageQueue[Message], tokenListingProcessor: TokenListingProcessor) -> None:
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenListingProcessor = tokenListingProcessor

    async def update_latest_listings_for_all_collections_deferred(self, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=UpdateListingsForAllCollections().to_message(), delaySeconds=delaySeconds)

    async def update_latest_listings_for_all_collections(self) -> None:
        # NOTE(krishan711): delay because of opensea limits, find a nicer way to do this
        for index, registryAddress in enumerate(GALLERY_COLLECTIONS):
            await self.update_latest_listings_for_collection_deferred(address=registryAddress, delaySeconds=min(900, int(60 * 0.2 * index)))

    async def update_latest_listings_for_collection_deferred(self, address: str, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=UpdateListingsForCollection(address=address).to_message(), delaySeconds=delaySeconds)

    async def refresh_latest_listings_for_all_collections_deferred(self, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=RefreshListingsForAllCollections().to_message(), delaySeconds=delaySeconds)

    async def refresh_latest_listings_for_all_collections(self) -> None:
        # NOTE(krishan711): delay because of opensea limits, find a nicer way to do this
        for index, registryAddress in enumerate(GALLERY_COLLECTIONS):
            await self.refresh_latest_listings_for_collection_deferred(address=registryAddress, delaySeconds=min(900, int(20 * 5 * index)))

    async def refresh_latest_listings_for_collection_deferred(self, address: str, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=RefreshListingsForCollectionMessageContent(address=address).to_message(), delaySeconds=delaySeconds)

    async def _update_full_latest_listings_for_collection(self, address: str) -> None:
        # tokenIdsQuery = (
        #     TokenMetadatasTable.select()
        #     .with_only_columns(TokenMetadatasTable.c.tokenId)
        #     .where(TokenMetadatasTable.c.registryAddress == address)
        #     .order_by(TokenMetadatasTable.c.tokenId.asc())
        # )
        # tokenIdsQueryResult = await self.retriever.database.execute(query=tokenIdsQuery)
        # tokenIds = [tokenId for (tokenId, ) in tokenIdsQueryResult]
        openseaListings = await self.tokenListingProcessor.get_opensea_listings_for_collection(registryAddress=address)
        logging.info(f'Retrieved {len(openseaListings)} openseaListings')
        # looksrareListings = await self.tokenListingProcessor.get_looksrare_listings_for_collection(registryAddress=address)
        # logging.info(f'Retrieved {len(looksrareListings)} looksrareListings')
        # raribleListings = await self.tokenListingProcessor.get_rarible_listings_for_tokens(registryAddress=address, tokenIds=tokenIds)
        # logging.info(f'Retrieved {len(raribleListings)} raribleListings')
        allListings = openseaListings # + looksrareListings + raribleListings
        # TODO(krishan711): change this to not delete existing. should add / remove / update changed only
        async with self.saver.create_transaction() as connection:
            currentLatestTokenListings = await self.retriever.list_latest_token_listings(fieldFilters=[
                StringFieldFilter(fieldName=LatestTokenListingsTable.c.registryAddress.key, eq=address)
            ], connection=connection)
            currentLatestTokenListingIds = [latestTokenListing.tokenListingId for latestTokenListing in currentLatestTokenListings]
            logging.info(f'Deleting {len(currentLatestTokenListingIds)} existing listings')
            await self.saver.delete_latest_token_listings(latestTokenListingIds=currentLatestTokenListingIds, connection=connection)
            logging.info(f'Saving {len(allListings)} listings')
            await self.saver.create_latest_token_listings(retrievedTokenListings=allListings, connection=connection)

    async def _update_partial_latest_listings_for_collection(self, address: str, startDate: datetime.datetime) -> None:
        openseaTokenIdsToReprocess = await self.tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=address, startDate=startDate)
        logging.info(f'Got {len(openseaTokenIdsToReprocess)} changed opensea tokenIds')
        # looksrareTokenIdsToReprocess = await self.tokenListingProcessor.get_changed_looksrare_token_listings_for_collection(address=address, startDate=startDate)
        # logging.info(f'Got {len(looksrareTokenIdsToReprocess)} changed looksrare tokenIds')
        # raribleTokenIdsToReprocess = await self.tokenListingProcessor.get_changed_rarible_token_listings_for_collection(address=address, startDate=startDate)
        # logging.info(f'Got {len(raribleTokenIdsToReprocess)} changed rarible tokenIds')
        openseaListings = await self.tokenListingProcessor.get_opensea_listings_for_tokens(registryAddress=address, tokenIds=openseaTokenIdsToReprocess)
        logging.info(f'Retrieved {len(openseaListings)} openseaListings')
        # looksrareListings = await self.tokenListingProcessor.get_looksrare_listings_for_tokens(registryAddress=address, tokenIds=looksrareTokenIdsToReprocess)
        # logging.info(f'Retrieved {len(looksrareListings)} looksrareListings')
        # raribleListings = await self.tokenListingProcessor.get_rarible_listings_for_tokens(registryAddress=address, tokenIds=raribleTokenIdsToReprocess)
        # logging.info(f'Retrieved {len(raribleListings)} raribleListings')
        async with self.saver.create_transaction() as connection:
            existingOpenseaListingsQuery = (
                LatestTokenListingsTable.select()
                    .with_only_columns(LatestTokenListingsTable.c.latestTokenListingId)
                    .where(LatestTokenListingsTable.c.registryAddress == address)
                    .where(LatestTokenListingsTable.c.tokenId.in_(openseaTokenIdsToReprocess))
                    .where(LatestTokenListingsTable.c.source.in_(['opensea-seaport', 'opensea-wyvern']))
            )
            existingOpenseaListingsResult = await self.retriever.database.execute(query=existingOpenseaListingsQuery, connection=connection)
            openseaListingIdsToDelete = {int(row[0]) for row in existingOpenseaListingsResult}
            # existingLooksrareListingsQuery = (
            #     LatestTokenListingsTable.select()
            #         .with_only_columns(LatestTokenListingsTable.c.latestTokenListingId)
            #         .where(LatestTokenListingsTable.c.registryAddress == address)
            #         .where(LatestTokenListingsTable.c.tokenId.in_(looksrareTokenIdsToReprocess))
            #         .where(LatestTokenListingsTable.c.source == 'looksrare')
            # )
            # existingLooksrareListingsResult = await self.retriever.database.execute(query=existingLooksrareListingsQuery, connection=connection)
            # looksrareListingIdsToDelete = {int(row[0]) for row in existingLooksrareListingsResult}
            # existingRaribleListingsQuery = (
            #     LatestTokenListingsTable.select()
            #         .with_only_columns(LatestTokenListingsTable.c.latestTokenListingId)
            #         .where(LatestTokenListingsTable.c.registryAddress == address)
            #         .where(LatestTokenListingsTable.c.tokenId.in_(raribleTokenIdsToReprocess))
            #         .where(LatestTokenListingsTable.c.source == 'rarible')
            # )
            # existingRaribleListingsResult = await self.retriever.database.execute(query=existingRaribleListingsQuery, connection=connection)
            # raribleListingIdsToDelete = {int(row[0]) for row in existingRaribleListingsResult}
            allListingIdsToDelete = list(openseaListingIdsToDelete) # | looksrareListingIdsToDelete | raribleListingIdsToDelete)
            allListings = openseaListings # + looksrareListings + raribleListings
            await self.saver.delete_latest_token_listings(latestTokenListingIds=allListingIdsToDelete, connection=connection)
            await self.saver.create_latest_token_listings(retrievedTokenListings=allListings, connection=connection)

    async def update_latest_listings_for_collection(self, address: str) -> None:
        currentDate = date_util.datetime_from_now()
        latestFullUpdate = await self.retriever.get_latest_update_by_key_name(key='update_latest_token_listings', name=address)
        latestPartialUpdate = await self.retriever.get_latest_update_by_key_name(key='update_partial_latest_token_listings', name=address)
        try:
            await self._update_partial_latest_listings_for_collection(address=address, startDate=max(latestFullUpdate.date, latestPartialUpdate.date))
        except LockTimeoutException as exception:
            logging.info(f'Skipping updating latest collection listings due to: {str(exception)}')
            return
        await self.saver.update_latest_update(latestUpdateId=latestPartialUpdate.latestUpdateId, date=currentDate)

    async def refresh_latest_listings_for_collection(self, address: str) -> None:
        currentDate = date_util.datetime_from_now()
        latestFullUpdate = await self.retriever.get_latest_update_by_key_name(key='update_latest_token_listings', name=address)
        if currentDate < date_util.datetime_from_datetime(dt=latestFullUpdate.date, hours=1):
            logging.info('Skipping recently refresh collection listing')
            return
        try:
            await self._update_full_latest_listings_for_collection(address=address)
        except LockTimeoutException as exception:
            raise MessageNeedsReprocessingException(delaySeconds=(60 * 10), originalException=exception)
        await self.saver.update_latest_update(latestUpdateId=latestFullUpdate.latestUpdateId, date=currentDate)

    async def list_all_listings_for_collection_token(self, registryAddress: str, tokenId: str) -> List[TokenListing]:
        query = (
            OrderedTokenListingsView.select()
            .where(OrderedTokenListingsView.c.registryAddress == registryAddress)
            .where(OrderedTokenListingsView.c.tokenId == tokenId)
            .order_by(OrderedTokenListingsView.c.tokenListingIndex.asc())
        )
        result = await self.retriever.database.execute(query=query)
        tokenListings = [token_listing_from_row(row, OrderedTokenListingsView) for row in result.mappings()]
        return tokenListings
