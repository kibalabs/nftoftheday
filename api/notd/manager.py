import asyncio
import datetime
import json
import logging
from typing import List, Sequence

from core.exceptions import DuplicateValueException
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import RandomOrder
from core.store.retriever import StringFieldFilter
from core.util import date_util

from notd.block_processor import BlockProcessor
from notd.collection_processor import CollectionDoesNotExist
from notd.collection_processor import CollectionProcessor
from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.model import Collection, SponsoredToken
from notd.model import RegistryToken
from notd.model import RetrievedTokenMetadata
from notd.model import RetrievedTokenTransfer
from notd.model import Token
from notd.model import UiData
from notd.opensea_client import OpenseaClient
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable
from notd.token_client import TokenClient
from notd.token_metadata_processor import TokenDoesNotExistException
from notd.token_metadata_processor import TokenHasNoMetadataException
from notd.token_metadata_processor import TokenMetadataProcessor


class NotdManager:

    def __init__(self, blockProcessor: BlockProcessor, saver: Saver, retriever: Retriever, workQueue: SqsMessageQueue, openseaClient: OpenseaClient, tokenClient: TokenClient, requester: Requester, tokenMetadataProcessor: TokenMetadataProcessor, collectionProcessor: CollectionProcessor):
        self.blockProcessor = blockProcessor
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.openseaClient = openseaClient
        self.tokenClient = tokenClient
        self.requester = requester
        self._tokenCache = dict()
        self.tokenMetadataProcessor = tokenMetadataProcessor
        self.collectionProcessor = collectionProcessor

    def get_sponsored_token(self) -> Token:
        sponsoredTokens = self.load_sponsored_tokens()
        sponsoredToken = sponsoredTokens[0].token
        currentDate = date_util.datetime_from_now()
        allPastTokens = [sponsorItem.token for sponsorItem in sponsoredTokens if  (sponsorItem.date) < currentDate]
        if allPastTokens:
            sponsoredToken = allPastTokens[-1]
        return sponsoredToken

    @staticmethod
    def load_sponsored_tokens() -> List[SponsoredToken]:
        with open("notd/sponsored_tokens.json", "r") as sponsoredTokensFile:
            sponsoredTokensDicts = json.loads(sponsoredTokensFile.read())
        sponsoredTokens = [SponsoredToken.from_dict(sponsoredTokenDict) for sponsoredTokenDict in sponsoredTokensDicts]
        return sponsoredTokens


    async def retrieve_ui_data(self, startDate: datetime.datetime, endDate: datetime.datetime) -> UiData:
        highestPricedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        mostTradedToken = await self.retriever.get_most_traded_token(startDate=startDate, endDate=endDate)
        mostTradedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate),
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=mostTradedToken.registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=mostTradedToken.tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)]
        )
        randomTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[RandomOrder()],
            limit=1
        )
        transactionCount = await self.retriever.get_transaction_count(startDate=startDate,endDate=endDate)
        return UiData(
            highestPricedTokenTransfer=highestPricedTokenTransfers[0],
            mostTradedTokenTransfers=mostTradedTokenTransfers,
            randomTokenTransfer=randomTokenTransfers[0],
            sponsoredToken=self.get_sponsored_token(),
            transactionCount=transactionCount
        )

    async def receive_new_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())

    async def receive_new_blocks(self) -> None:
        latestTokenTransfers = await self.retriever.list_token_transfers(orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)], limit=1)
        latestProcessedBlockNumber = latestTokenTransfers[0].blockNumber
        latestBlockNumber = await self.blockProcessor.get_latest_block_number()
        logging.info(f'Scheduling messages for processing blocks from {latestProcessedBlockNumber} to {latestBlockNumber}')
        batchSize = 3
        for startBlockNumber in reversed(range(latestProcessedBlockNumber, latestBlockNumber + 1, batchSize)):
            endBlockNumber = min(startBlockNumber + batchSize, latestBlockNumber + 1)
            await self.workQueue.send_message(message=ProcessBlockRangeMessageContent(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber).to_message())

    async def process_block_range(self, startBlockNumber: int, endBlockNumber: int) -> None:
        blockNumbers = list(range(startBlockNumber, endBlockNumber))
        await self.process_blocks(blockNumbers=blockNumbers)

    async def process_blocks(self, blockNumbers: Sequence[int]) -> None:
        await asyncio.gather(*[self.process_block(blockNumber=blockNumber) for blockNumber in blockNumbers])

    async def _create_token_transfer(self, retrievedTokenTransfer: RetrievedTokenTransfer) -> None:
        try:
            await self.saver.create_token_transfer(retrievedTokenTransfer=retrievedTokenTransfer)
        except DuplicateValueException:
            logging.debug('Ignoring previously saved transfer')

    async def process_block(self, blockNumber: int) -> None:
        # TODO(krishan711): uncomment this when we can save in transactions (which is currently blocked by the duplication exception)
        # blockTransfers = await self.retriever.list_token_transfers(
        #     fieldFilters=[
        #         IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, eq=blockNumber),
        #     ], limit=1,
        # )
        # if len(blockTransfers) > 0:
        #     logging.info('Skipping block because it already has transfers.')
        #     return
        retrievedTokenTransfers = await self.blockProcessor.get_transfers_in_block(blockNumber=blockNumber)
        logging.info(f'Found {len(retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        await asyncio.gather(*[self._create_token_transfer(retrievedTokenTransfer=retrievedTokenTransfer) for retrievedTokenTransfer in retrievedTokenTransfers])
        retrievedAddresses = set()
        for retrievedTokenTransfer in retrievedTokenTransfers:
            await self.workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=retrievedTokenTransfer.registryAddress, tokenId=retrievedTokenTransfer.tokenId).to_message())
            retrievedAddresses.add(retrievedTokenTransfer.registryAddress)
        for address in retrievedAddresses:
            await self.workQueue.send_message(message=UpdateCollectionMessageContent(address=address).to_message())

    async def update_token_metadata(self, registryAddress: str, tokenId: str) -> None:
        savedTokenMetadatas = await self.retriever.list_token_metadata(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenMetadataTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenMetadataTable.c.tokenId.key, eq=tokenId),
            ], limit=1,
        )
        savedTokenMetadata = savedTokenMetadatas[0] if len(savedTokenMetadatas) > 0 else None
        if savedTokenMetadata and savedTokenMetadata.updatedDate >= date_util.datetime_from_now(days=-3):
            logging.info('Skipping token because it has been updated recently.')
            return
        try:
            retrievedTokenMetadata = await self.tokenMetadataProcessor.retrieve_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
        except TokenDoesNotExistException:
            logging.info(f'Failed to retrieve non-existant token: {registryAddress}: {tokenId}')
            return
        except TokenHasNoMetadataException:
            logging.info(f'Failed to retrieve metadata for token: {registryAddress}: {tokenId}')
            return
        if savedTokenMetadata:
            await self.saver.update_token_metadata(tokenMetadataId=savedTokenMetadata.tokenMetadataId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)
        else:
            await self.saver.create_token_metadata(registryAddress=registryAddress, tokenId=tokenId, metadataUrl=retrievedTokenMetadata.metadataUrl, imageUrl=retrievedTokenMetadata.imageUrl, name=retrievedTokenMetadata.name, description=retrievedTokenMetadata.description, attributes=retrievedTokenMetadata.attributes)

    async def retreive_registry_token(self, registryAddress: str, tokenId: str) -> RegistryToken:
        cacheKey = f'{registryAddress}:{tokenId}'
        if cacheKey in self._tokenCache:
            return self._tokenCache[cacheKey]
        try:
            registryToken = await self.openseaClient.retreive_registry_token(registryAddress=registryAddress, tokenId=tokenId)
        except NotFoundException:
            registryToken = await self.tokenClient.retreive_registry_token(registryAddress=registryAddress, tokenId=tokenId)
        self._tokenCache[cacheKey] = registryToken
        return registryToken

    async def subscribe_email(self, email: str) -> None:
        await self.requester.post(url='https://api.kiba.dev/v1/newsletter-subscriptions', dataDict={'topic': 'tokenhunt', 'email': email.lower()})

    async def retreive_token_metadata(self, registryAddress: str, tokenId: str) -> RegistryToken:
        tokenMetadatas = await self.retriever.list_token_metadata(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenMetadataTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=TokenMetadataTable.c.tokenId.key, eq=tokenId),
            ], limit=1,
        )
        if len(tokenMetadatas) == 0:
            cacheKey = f'{registryAddress}:{tokenId}'
            if cacheKey in self._tokenCache:
                registryToken = self._tokenCache[cacheKey]
            else:
                registryToken = await self.openseaClient.retreive_registry_token(registryAddress=registryAddress, tokenId=tokenId)
                self._tokenCache[cacheKey] = registryToken
            await self.workQueue.send_message(message=UpdateTokenMetadataMessageContent(registryAddress=registryAddress, tokenId=tokenId).to_message())
            tokenMetadatas.append(RetrievedTokenMetadata(registryAddress=registryToken.registryAddress, tokenId=registryToken.tokenId, metadataUrl=registryToken.openSeaUrl, imageUrl=registryToken.imageUrl, name=registryToken.name, description=None, attributes=None))
        return tokenMetadatas[0]

    async def update_collection(self, address: str) -> None:
        collections = await self.retriever.list_collection(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, eq=address),
            ], limit=1,
        )
        collection = collections[0] if len(collections) > 0 else None
        if collection and collection.updatedDate >= date_util.datetime_from_now(days=-7):
            logging.info('Skipping Collection because it has been updated recently.')
            return
        try:
            retrievedCollection = await self.collectionProcessor.retrieve_collection(address=address)
        except CollectionDoesNotExist:
            logging.info(f'Failed to retrieve non-existant collection: {address}')
            return
        if collection:
            await self.saver.update_collection(collectionId=collection.collectionId, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl)
        else:
            await self.saver.create_collection(address=address, name=retrievedCollection.name, symbol=retrievedCollection.symbol, description=retrievedCollection.description, imageUrl=retrievedCollection.imageUrl, twitterUsername=retrievedCollection.twitterUsername, instagramUsername=retrievedCollection.instagramUsername, wikiUrl=retrievedCollection.wikiUrl, openseaSlug=retrievedCollection.openseaSlug, url=retrievedCollection.url, discordUrl=retrievedCollection.discordUrl, bannerImageUrl=retrievedCollection.bannerImageUrl)

    async def retreive_collection(self, address: str) -> Collection:
        collections = await self.retriever.list_collection(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, eq=address),
            ], limit=1,
        )
        if len(collections) == 0:
            raise NotFoundException()
        return collections[0]
