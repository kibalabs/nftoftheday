import asyncio
import datetime
from typing import List
from typing import Optional

from core import logging
from core.requester import Requester
from core.util import chain_util
from core.util import date_util
from core.util import list_util

from notd.lock_manager import LockManager
from notd.model import RetrievedTokenListing

_OPENSEA_API_LISTING_CHUNK_SIZE = 30
_LOOKSRARE_API_LISTING_CHUNK_SIZE = 30

class TokenListingProcessor:

    def __init__(self, requester: Requester, openseaRequester: Requester, lockManager: LockManager):
        self.requester = requester
        self.openseaRequester = openseaRequester
        self.lockManager = lockManager

    async def get_opensea_listings_for_tokens(self, registryAddress: str, tokenIds: List[str]) -> List[RetrievedTokenListing]:
        listings = []
        async with self.lockManager.with_lock(name='opensea-requester', timeoutSeconds=100, expirySeconds=(1.5 * len(tokenIds) / _OPENSEA_API_LISTING_CHUNK_SIZE)):
            for index, chunkedTokenIds in enumerate(list_util.generate_chunks(lst=tokenIds, chunkSize=_OPENSEA_API_LISTING_CHUNK_SIZE)):
                nextPageId = None
                pageCount = 0
                while True:
                    logging.stat('RETRIEVE_LISTINGS_OPENSEA', registryAddress, float(f'{index}.{pageCount}'))
                    queryData = {
                        'token_ids': chunkedTokenIds,
                        'asset_contract_address': registryAddress,
                    }
                    if nextPageId:
                        queryData['cursor'] = nextPageId
                    response = await self.openseaRequester.get(url='https://api.opensea.io/api/v2/orders/ethereum/seaport/listings', dataDict=queryData, timeout=30)
                    responseJson = response.json()
                    for seaportSellOrder in (responseJson.get('orders') or []):
                        print('seaportSellOrder', seaportSellOrder)
                        side = seaportSellOrder["side"]
                        if side != 'ask':
                            continue
                        orderType = seaportSellOrder["order_type"]
                        if orderType != 'basic':
                            # NOTE(krishan711): what should happen here?
                            continue
                        if len(seaportSellOrder['maker_asset_bundle']['assets']) == 0:
                            # NOTE(krishan711): what should happen here?
                            continue
                        cancelled = seaportSellOrder["cancelled"]
                        if cancelled:
                            # NOTE(krishan711): what should happen here?
                            continue
                        startDate = datetime.datetime.utcfromtimestamp(seaportSellOrder["listing_time"])
                        endDate = datetime.datetime.utcfromtimestamp(seaportSellOrder["expiration_time"])
                        currentPrice = int(seaportSellOrder["current_price"].split('.')[0])
                        offererAddress = seaportSellOrder["maker"]["address"]
                        sourceId = seaportSellOrder["order_hash"]
                        tokenId = seaportSellOrder['maker_asset_bundle']['assets'][0]['token_id']
                        isValueNative = True
                        # NOTE(krishan711): should isValueNative and value be calculated using considerations?
                        listing = RetrievedTokenListing(
                            registryAddress=registryAddress,
                            tokenId=tokenId,
                            startDate=startDate,
                            endDate=endDate,
                            isValueNative=isValueNative,
                            value=currentPrice,
                            offererAddress=chain_util.normalize_address(offererAddress),
                            source='opensea-seaport',
                            sourceId=sourceId,
                        )
                        listings.append(listing)
                    # NOTE(krishan711): sleep to avoid opensea limits
                    await asyncio.sleep(0.2)
                    if responseJson.get('next'):
                        nextPageId = responseJson.get('next')
                        pageCount += 1
                    else:
                        break
        return listings

    async def get_changed_opensea_token_listings_for_collection(self, address: str, startDate: datetime.datetime) -> List[str]:
        async with self.lockManager.with_lock(name='opensea-requester', timeoutSeconds=10, expirySeconds=60):
            tokensIdsToReprocess = set()
            index = 0
            for eventType in ['created', 'cancelled']:
                queryData = {
                    'asset_contract_address': address,
                    'occurred_after': int(startDate.timestamp()),
                    'event_type': eventType,
                }
                while True:
                    logging.stat(f'RETRIEVE_CHANGED_LISTINGS_OPENSEA_{eventType}'.upper(), address, index)
                    index += 1
                    response = await self.openseaRequester.get(url="https://api.opensea.io/api/v1/events", dataDict=queryData, timeout=30)
                    responseJson = response.json()
                    logging.info(f'Got {len(responseJson["asset_events"])} opensea events')
                    for event in responseJson['asset_events']:
                        if event.get('asset'):
                            tokensIdsToReprocess.add(event['asset']['token_id'])
                    await asyncio.sleep(0.25)
                    if not responseJson.get('next'):
                        break
                    queryData['cursor'] = responseJson['next']
            return list(tokensIdsToReprocess)

    async def get_looksrare_listings_for_collection(self, registryAddress: str) -> List[RetrievedTokenListing]:
        async with self.lockManager.with_lock(name='looksrare-requester', timeoutSeconds=10, expirySeconds=60):
            queryData = {
                'isOrderAsk': 'true',
                'collection': registryAddress,
                'status[]': 'VALID',
                'pagination[first]': 100,
                'sort': 'PRICE_ASC',
            }
            assetListings: List[RetrievedTokenListing] = []
            index = 0
            while True:
                logging.stat('RETRIEVE_LISTINGS_LOOKSRARE', registryAddress, index)
                index += 1
                response = await self.requester.get(url='https://api.looksrare.org/api/v1/orders', dataDict=queryData, timeout=30)
                responseJson = response.json()
                if len(responseJson['data']) == 0:
                    break
                latestOrderHash = None
                for order in responseJson['data']:
                    startDate = datetime.datetime.utcfromtimestamp(order["startTime"])
                    endDate = datetime.datetime.utcfromtimestamp(order["endTime"])
                    currentPrice = int(order["price"])
                    offererAddress = chain_util.normalize_address(order['signer'])
                    sourceId = order["hash"]
                    # NOTE(Femi-Ogunkola): LooksRare seems to send eth listings with weth currency address
                    isValueNative = order["currencyAddress"] == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
                    listing = RetrievedTokenListing(
                        registryAddress=order['collectionAddress'],
                        tokenId=order['tokenId'],
                        startDate=startDate,
                        endDate=endDate,
                        isValueNative=isValueNative,
                        value=currentPrice,
                        offererAddress=offererAddress,
                        source='looksrare',
                        sourceId=sourceId,
                    )
                    assetListings.append(listing)
                    latestOrderHash = order['hash']
                queryData['pagination[cursor]'] = latestOrderHash
            return assetListings

    async def get_looksrare_listing_for_token(self, registryAddress: str, tokenId: str) -> Optional[RetrievedTokenListing]:
        queryData = {
            'isOrderAsk': 'true',
            'collection': registryAddress,
            'tokenId': tokenId,
            'status[]': 'VALID',
            'pagination[first]': 100,
            'sort': 'PRICE_ASC',
        }
        assetListings = []
        logging.stat('RETRIEVE_TOKEN_LISTING_LOOKSRARE', registryAddress, 0)
        response = await self.requester.get(url='https://api.looksrare.org/api/v1/orders', dataDict=queryData, timeout=30)
        responseJson = response.json()
        for order in responseJson['data']:
            startDate = datetime.datetime.utcfromtimestamp(order["startTime"])
            endDate = datetime.datetime.utcfromtimestamp(order["endTime"])
            currentPrice = int(order["price"])
            offererAddress = chain_util.normalize_address(order['signer'])
            sourceId = order["hash"]
            # NOTE(Femi-Ogunkola): LooksRare seems to send eth listings with weth currency address
            isValueNative = order["currencyAddress"] == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            assetListings += [RetrievedTokenListing(
                registryAddress=order['collectionAddress'],
                tokenId=order['tokenId'],
                startDate=startDate,
                endDate=endDate,
                isValueNative=isValueNative,
                value=currentPrice,
                offererAddress=offererAddress,
                source='looksrare',
                sourceId=sourceId,
            )]
        return assetListings

    async def get_looksrare_listings_for_tokens(self, registryAddress: str, tokenIds: List[str]) -> List[RetrievedTokenListing]:
        async with self.lockManager.with_lock(name='looksrare-requester', timeoutSeconds=10, expirySeconds=(1.5 * len(tokenIds) / _LOOKSRARE_API_LISTING_CHUNK_SIZE)):
            listings = []
            for chunkedTokenIds in list_util.generate_chunks(lst=tokenIds, chunkSize=_LOOKSRARE_API_LISTING_CHUNK_SIZE):
                listings += await asyncio.gather(*[self.get_looksrare_listing_for_token(registryAddress=registryAddress, tokenId=tokenId) for tokenId in chunkedTokenIds])
                await asyncio.sleep(0.25)
            listings = [listing for listing in listings if listing is not None]
            allListings = [item for sublist in listings for item in sublist]
            return allListings

    async def get_changed_looksrare_token_listings_for_collection(self, address: str, startDate: datetime.datetime):
        async with self.lockManager.with_lock(name='looksrare-requester', timeoutSeconds=10, expirySeconds=60):
            tokenIdsToReprocess = set()
            for eventType in ["CANCEL_LIST", "LIST"]:
                queryData = {
                    'collection': address,
                    'type': eventType,
                    'pagination[first]': 150
                }
                latestEventId = None
                hasReachedEnd = False
                while not hasReachedEnd:
                    response = await self.requester.get(url='https://api.looksrare.org/api/v1/events', dataDict=queryData)
                    responseJson = response.json()
                    logging.info(f'Got {len(responseJson["data"])} looksrare events')
                    if len(responseJson['data']) == 0:
                        break
                    for event in responseJson['data']:
                        if date_util.datetime_from_string(event['createdAt'], dateFormat='%Y-%m-%dT%H:%M:%S.%fZ') < startDate:
                            hasReachedEnd = True
                            break
                        tokenIdsToReprocess.add(event.get('token').get('tokenId'))
                        latestEventId = event['id']
                    queryData['pagination[cursor]'] = latestEventId
            return list(tokenIdsToReprocess)
