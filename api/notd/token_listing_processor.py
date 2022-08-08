import asyncio
import datetime
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Optional

from core import logging
from core.requester import Requester
from core.util import date_util
from core.util import list_util
from notd.lock_manager import LockManager

from notd.model import RetrievedTokenListing


class TokenListingProcessor:

    def __init__(self, requester: Requester, openseaRequester: Requester, lockManger: LockManager):
        self.requester = requester
        self.openseaRequester = openseaRequester
        self.lockManager = lockManger

    async def get_opensea_listings_for_tokens(self, registryAddress: str, tokenIds: List[str]) -> List[RetrievedTokenListing]:
        listings = []
        async with self.lockManager.with_lock(name="opensea_lock", timeoutSeconds=30, expirySeconds=120):
            for index, chunkedTokenIds in enumerate(list_util.generate_chunks(lst=tokenIds, chunkSize=30)):
                logging.stat('RETRIEVE_LISTINGS_OPENSEA', registryAddress, index)
                queryData = {
                    'token_ids': chunkedTokenIds,
                    'asset_contract_address': registryAddress,
                    'include_orders': True,
                    'limit': len(chunkedTokenIds),
                }
                response = await self.openseaRequester.get(url='https://api.opensea.io/api/v1/assets', dataDict=queryData, timeout=30)
                responseJson = response.json()
                for asset in responseJson['assets']:
                    assetListings = []
                    for sellOrder in (asset.get('sell_orders') or []):
                        side = sellOrder["side"]
                        if side != 1:
                            continue
                        saleKind = sellOrder["sale_kind"]
                        if saleKind != 0:
                            # NOTE(krishan711): what should happen here?
                            continue
                        cancelled = sellOrder["cancelled"]
                        if cancelled:
                            # NOTE(krishan711): what should happen here?
                            continue
                        startDate = datetime.datetime.utcfromtimestamp(sellOrder["listing_time"])
                        endDate = datetime.datetime.utcfromtimestamp(sellOrder["expiration_time"])
                        currentPrice = int(sellOrder["current_price"].split('.')[0])
                        offererAddress = sellOrder["maker"]["address"]
                        sourceId = sellOrder["order_hash"]
                        isValueNative = sellOrder["payment_token_contract"]["symbol"] == "ETH"
                        listing = RetrievedTokenListing(
                            registryAddress=registryAddress,
                            tokenId=asset['token_id'],
                            startDate=startDate,
                            endDate=endDate,
                            isValueNative=isValueNative,
                            value=currentPrice,
                            offererAddress=offererAddress,
                            source='opensea-wyvern',
                            sourceId=sourceId,
                        )
                        assetListings.append(listing)
                    for seaportSellOrder in (asset.get('seaport_sell_orders') or []):
                        side = seaportSellOrder["side"]
                        if side != 'ask':
                            continue
                        orderType = seaportSellOrder["order_type"]
                        if orderType != 'basic':
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
                        isValueNative = True
                        # NOTE(krishan711): should isValueNative and value be calculated using considerations?
                        listing = RetrievedTokenListing(
                            registryAddress=registryAddress,
                            tokenId=asset['token_id'],
                            startDate=startDate,
                            endDate=endDate,
                            isValueNative=isValueNative,
                            value=currentPrice,
                            offererAddress=offererAddress,
                            source='opensea-seaport',
                            sourceId=sourceId,
                        )
                        assetListings.append(listing)
                    if len(assetListings) > 0:
                        # NOTE(krishan711): take the lowest one
                        sortedAssetListings = sorted(assetListings, key=lambda listing: listing.value, reverse=False)
                        listings.append(sortedAssetListings[0])
                # NOTE(krishan711): sleep to avoid opensea limits
                await asyncio.sleep(0.25)
            return listings

    async def get_changed_opensea_token_listings_for_collection(self, address: str, startDate: datetime.datetime) -> List[str]:
        print("here")
        async with self.lockManager.with_lock(name="opensea_request", timeoutSeconds=30, expirySeconds=600):
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
                    response = await self.openseaRequester.get(url="https://api.opensea.io/api/v1/events", dataDict=queryData, timeout=600)
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
        async with self.lockManager.with_lock(name="looksrare_request", timeoutSeconds=30, expirySeconds=120):
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
                    offererAddress = order['signer']
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
            tokenListingDict: Dict[str, RetrievedTokenListing] = defaultdict(RetrievedTokenListing)
            for listing in assetListings:
                if listing.tokenId not in tokenListingDict:
                    tokenListingDict[listing.tokenId] = listing
            return list(tokenListingDict.values())

    async def get_looksrare_listing_for_token(self, registryAddress: str, tokenId: str) -> Optional[RetrievedTokenListing]:
        async with self.lockManager.with_lock(name="looksrare_request", timeoutSeconds=30, expirySeconds=120):
            queryData = {
                'isOrderAsk': 'true',
                'collection': registryAddress,
                'tokenId': tokenId,
                'status[]': 'VALID',
                'pagination[first]': 100,
                'sort': 'PRICE_ASC',
            }
            assetListing: Optional[RetrievedTokenListing] = None
            logging.stat('RETRIEVE_TOKEN_LISTING_LOOKSRARE', registryAddress, 0)
            response = await self.requester.get(url='https://api.looksrare.org/api/v1/orders', dataDict=queryData, timeout=30)
            responseJson = response.json()
            for order in responseJson['data']:
                startDate = datetime.datetime.utcfromtimestamp(order["startTime"])
                endDate = datetime.datetime.utcfromtimestamp(order["endTime"])
                currentPrice = int(order["price"])
                offererAddress = order['signer']
                sourceId = order["hash"]
                # NOTE(Femi-Ogunkola): LooksRare seems to send eth listings with weth currency address
                isValueNative = order["currencyAddress"] == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
                assetListing = RetrievedTokenListing(
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
                break
            return assetListing

    async def get_looksrare_listings_for_tokens(self, registryAddress: str, tokenIds: List[str]) -> List[RetrievedTokenListing]:
        listings = []
        for chunkedTokenIds in list_util.generate_chunks(lst=tokenIds, chunkSize=30):
            listings += await asyncio.gather(*[self.get_looksrare_listing_for_token(registryAddress=registryAddress, tokenId=tokenId) for tokenId in chunkedTokenIds])
            await asyncio.sleep(0.1)
        listings = [listing for listing in listings if listing is not None]
        return listings

    async def get_changed_looksrare_token_listings_for_collection(self, address: str, startDate: datetime.datetime):
        async with self.lockManager.with_lock(name="looksrare_request", timeoutSeconds=30, expirySeconds=120):
            tokenIdsToReprocess = set()
            for eventType in ["CANCEL_LIST", "LIST" ]:
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
