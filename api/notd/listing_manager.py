import datetime

from core import logging
from core.queues.sqs_message_queue import SqsMessageQueue
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.messages import UpdateListingsForAllCollections
from notd.messages import UpdateListingsForCollection
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import TokenMetadatasTable
from notd.token_listing_processor import TokenListingProcessor


class ListingManager:

    def __init__(self, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, tokenListingProcessor: TokenListingProcessor) -> None:
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.tokenListingProcessor = tokenListingProcessor

    async def update_latest_listings_for_all_collections_deferred(self, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=UpdateListingsForAllCollections().to_message(), delaySeconds=delaySeconds)

    async def update_latest_listings_for_all_collections(self) -> None:
        # NOTE(krishan711): delay because of opensea limits, find a nicer way to do this
        for index, registryAddress in enumerate(GALLERY_COLLECTIONS):
            await self.update_latest_listings_for_collection_deferred(address=registryAddress, delaySeconds=(60 * 5 * index))

    async def update_latest_listings_for_collection_deferred(self, address: str, delaySeconds: int = 0) -> None:
        await self.workQueue.send_message(message=UpdateListingsForCollection(address=address).to_message(), delaySeconds=delaySeconds)

    async def update_full_latest_listings_for_collection(self, address: str) -> None:
        tokenIdsQuery = (
            TokenMetadatasTable.select()
            .with_only_columns([TokenMetadatasTable.c.tokenId])
            .where(TokenMetadatasTable.c.registryAddress == address)
            .order_by(TokenMetadatasTable.c.tokenId.asc())
        )
        tokenIdsQueryResult = await self.retriever.database.execute(query=tokenIdsQuery)
        tokenIds = [tokenId for (tokenId, ) in tokenIdsQueryResult]
        openseaListings = await self.tokenListingProcessor.get_opensea_listings_for_tokens(registryAddress=address, tokenIds=tokenIds)
        logging.info(f'Retrieved {len(openseaListings)} openseaListings')
        looksrareListings = await self.tokenListingProcessor.get_looksrare_listings_for_collection(registryAddress=address)
        logging.info(f'Retrieved {len(looksrareListings)} looksrareListings')
        allListings = openseaListings + looksrareListings
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

    async def update_partial_latest_listings_for_collection(self, address: str, startDate: datetime.datetime) -> None:
        openseaTokenIdsToReprocess = await self.tokenListingProcessor.get_changed_opensea_token_listings_for_collection(address=address, startDate=startDate)
        logging.info(f'Got {len(openseaTokenIdsToReprocess)} changed opensea tokenIds')
        looksrareTokenIdsToReprocess = await self.tokenListingProcessor.get_changed_looksrare_token_listings_for_collection(address=address, startDate=startDate)
        logging.info(f'Got {len(looksrareTokenIdsToReprocess)} changed looksrare tokenIds')
        openseaListings = await self.tokenListingProcessor.get_opensea_listings_for_tokens(registryAddress=address, tokenIds=openseaTokenIdsToReprocess)
        logging.info(f'Retrieved {len(openseaListings)} openseaListings')
        looksrareListings = await self.tokenListingProcessor.get_looksrare_listings_for_tokens(registryAddress=address, tokenIds=looksrareTokenIdsToReprocess)
        logging.info(f'Retrieved {len(looksrareListings)} looksrareListings')
        async with self.saver.create_transaction() as connection:
            existingOpenseaListingsQuery = (
                LatestTokenListingsTable.select()
                    .with_only_columns([LatestTokenListingsTable.c.latestTokenListingId])
                    .where(LatestTokenListingsTable.c.registryAddress == address)
                    .where(LatestTokenListingsTable.c.tokenId.in_(openseaTokenIdsToReprocess))
                    .where(LatestTokenListingsTable.c.source.in_(['opensea-seaport', 'opensea-wyvern']))
            )
            existingOpenseaListingsResult = await self.retriever.database.execute(query=existingOpenseaListingsQuery, connection=connection)
            openseaListingIdsToDelete = {row[0] for row in existingOpenseaListingsResult}
            existingLooksrareListingsQuery = (
                LatestTokenListingsTable.select()
                    .with_only_columns([LatestTokenListingsTable.c.latestTokenListingId])
                    .where(LatestTokenListingsTable.c.registryAddress == address)
                    .where(LatestTokenListingsTable.c.tokenId.in_(looksrareTokenIdsToReprocess))
                    .where(LatestTokenListingsTable.c.source == 'looksrare')
            )
            existingLooksrareListingsResult = await self.retriever.database.execute(query=existingLooksrareListingsQuery, connection=connection)
            looksrareListingIdsToDelete = {row[0] for row in existingLooksrareListingsResult}
            allListingIdsToDelete = openseaListingIdsToDelete | looksrareListingIdsToDelete
            allListings = openseaListings + looksrareListings
            await self.saver.delete_latest_token_listings(latestTokenListingIds=allListingIdsToDelete, connection=connection)
            await self.saver.create_latest_token_listings(retrievedTokenListings=allListings, connection=connection)

    async def update_latest_listings_for_collection(self, address: str) -> None:
        currentDate = date_util.datetime_from_now()
        latestFullUpdate = await self.retriever.get_latest_update_by_key_name(key='update_latest_token_listings', name=address)
        latestPartialUpdate = await self.retriever.get_latest_update_by_key_name(key='update_partial_latest_token_listings', name=address)
        # if currentDate > date_util.datetime_from_datetime(dt=latestFullUpdate.date, hours=3):
        #     await self.update_full_latest_listings_for_collection(address=address)
        #     await self.saver.update_latest_update(latestUpdateId=latestFullUpdate.latestUpdateId, date=currentDate)
        # else:
        await self.update_partial_latest_listings_for_collection(address=address, startDate=max(latestFullUpdate.date, latestPartialUpdate.date))
        await self.saver.update_latest_update(latestUpdateId=latestPartialUpdate.latestUpdateId, date=currentDate)
