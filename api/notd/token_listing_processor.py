import asyncio
import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from core import logging
from core.requester import Requester
from core.util import chain_util
from core.util import date_util
from core.util import list_util
from core.util.typing_util import JSON1

from notd.collection_manager import CollectionManager
from notd.lock_manager import LockManager
from notd.model import RetrievedTokenListing

_OPENSEA_API_LISTING_CHUNK_SIZE = 30
_LOOKSRARE_API_LISTING_CHUNK_SIZE = 30

SECONDS_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
MILLISECONDS_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

def _timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(timestamp)

def _parse_date_string(dateString: str) -> datetime.datetime:
    if '.' in dateString:
        return date_util.datetime_from_string(dateString, dateFormat=MILLISECONDS_DATETIME_FORMAT)
    return date_util.datetime_from_string(dateString, dateFormat=SECONDS_DATETIME_FORMAT)

class TokenListingProcessor:

    def __init__(self, requester: Requester, openseaRequester: Requester, lockManager: LockManager, collectionManger: CollectionManager):
        self.requester = requester
        self.openseaRequester = openseaRequester
        self.lockManager = lockManager
        self.collectionManger = collectionManger

    async def get_opensea_listings_for_collection(self, registryAddress: str) -> List[RetrievedTokenListing]:
        listings = []
        async with self.lockManager.with_lock(name='opensea-requester', timeoutSeconds=100, expirySeconds=240):
            collection = await self.collectionManger.get_collection_by_address(address=registryAddress)
            collectionOpenseaSlug = collection.openseaSlug
            nextPageId: Optional[str] = None
            pageCount = 0
            while True:
                logging.stat('RETRIEVE_LISTINGS_OPENSEA', registryAddress, float(f'{pageCount}'))
                queryData: Dict[str, JSON1] = {
                    "type": "basic",
                    "limit": 100
                }
                if nextPageId:
                    queryData['next'] = nextPageId
                response = await self.openseaRequester.get(url=f'https://api.opensea.io/v2/listings/collection/{collectionOpenseaSlug}/all', dataDict=queryData, timeout=30)
                responseJson = response.json()
                for openseaListing in (responseJson.get('listings') or []):
                    startDate = _timestamp_to_datetime(timestamp=int(openseaListing['protocol_data']["parameters"]["startTime"]))
                    endDate = _timestamp_to_datetime(timestamp=int(openseaListing['protocol_data']["parameters"]["endTime"]))
                    currentPrice = int(openseaListing["price"]['current']['value'])
                    offererAddress = openseaListing["protocol_data"]["parameters"]['offerer']
                    sourceId = openseaListing["order_hash"]
                    tokenId = openseaListing["protocol_data"]["parameters"]['offer'][0]['identifierOrCriteria']
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
                        source='opensea',
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

    async def get_opensea_listings_for_tokens(self, registryAddress: str, tokenIds: Sequence[str]) -> List[RetrievedTokenListing]:
        listings = []
        async with self.lockManager.with_lock(name='opensea-requester', timeoutSeconds=100, expirySeconds=int(10 * len(tokenIds) / _OPENSEA_API_LISTING_CHUNK_SIZE)):
            for index, chunkedTokenIds in enumerate(list_util.generate_chunks(lst=tokenIds, chunkSize=_OPENSEA_API_LISTING_CHUNK_SIZE)):
                nextPageId: Optional[str] = None
                pageCount = 0
                while True:
                    logging.stat('RETRIEVE_LISTINGS_OPENSEA', registryAddress, float(f'{index}.{pageCount}'))
                    queryData: Dict[str, JSON1] = {
                        'token_ids': chunkedTokenIds,  # type: ignore[dict-item]
                        'asset_contract_address': registryAddress,
                    }
                    if nextPageId:
                        queryData['cursor'] = nextPageId
                    response = await self.openseaRequester.get(url='https://api.opensea.io/api/v2/orders/ethereum/seaport/listings', dataDict=queryData, timeout=30)
                    responseJson = response.json()
                    for seaportSellOrder in (responseJson.get('orders') or []):
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
        secondsSinceStartDate = (date_util.datetime_from_now() - startDate).seconds
        async with self.lockManager.with_lock(name='opensea-requester', timeoutSeconds=10, expirySeconds=max(60, int(secondsSinceStartDate / 100))):
            tokensIdsToReprocess = set()
            index = 0
            for eventType in ['created', 'cancelled']:
                queryData: Dict[str, JSON1] = {
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
        async with self.lockManager.with_lock(name='looksrare-requester', timeoutSeconds=10, expirySeconds=120):
            queryData: Dict[str, JSON1] = {
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
                await asyncio.sleep(0.1)
            return assetListings

    async def _get_looksrare_listings_for_token(self, registryAddress: str, tokenId: str) -> List[RetrievedTokenListing]:
        queryData: Dict[str, JSON1] = {
            'isOrderAsk': 'true',
            'collection': registryAddress,
            'tokenId': tokenId,
            'status[]': 'VALID',
            'pagination[first]': 100,
            'sort': 'PRICE_ASC',
        }
        assetListings: List[RetrievedTokenListing] = []
        index = 0
        while True:
            logging.stat('RETRIEVE_TOKEN_LISTINGS_LOOKSRARE', registryAddress, index)
            index += 1
            response = await self.requester.get(url='https://api.looksrare.org/api/v1/orders', dataDict=queryData, timeout=30)
            responseJson = response.json()
            if len(responseJson['data']) == 0:
                break
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
            await asyncio.sleep(0.1)
        return assetListings

    async def get_looksrare_listings_for_tokens(self, registryAddress: str, tokenIds: List[str]) -> List[RetrievedTokenListing]:
        async with self.lockManager.with_lock(name='looksrare-requester', timeoutSeconds=10, expirySeconds=int(10 * len(tokenIds) / _LOOKSRARE_API_LISTING_CHUNK_SIZE)):
            listings = []
            for chunkedTokenIds in list_util.generate_chunks(lst=tokenIds, chunkSize=_LOOKSRARE_API_LISTING_CHUNK_SIZE):
                listings += await asyncio.gather(*[self._get_looksrare_listings_for_token(registryAddress=registryAddress, tokenId=tokenId) for tokenId in chunkedTokenIds])
            listings = [listing for listing in listings if listing is not None]
            allListings = [item for sublist in listings for item in sublist]
            return allListings

    async def get_changed_looksrare_token_listings_for_collection(self, address: str, startDate: datetime.datetime) -> List[str]:
        secondsSinceStartDate = (date_util.datetime_from_now() - startDate).seconds
        async with self.lockManager.with_lock(name='looksrare-requester', timeoutSeconds=10, expirySeconds=max(60, int(secondsSinceStartDate / 100))):
            tokenIdsToReprocess = set()
            for eventType in ["CANCEL_LIST", "LIST"]:
                queryData: Dict[str, JSON1] = {
                    'collection': address,
                    'type': eventType,
                    'pagination[first]': 150
                }
                latestEventId = None
                hasReachedEnd = False
                page = 0
                while not hasReachedEnd:
                    logging.stat(f'RETRIEVE_CHANGED_LISTINGS_LOOKSRARE_{eventType}'.upper(), address, page)
                    response = await self.requester.get(url='https://api.looksrare.org/api/v1/events', dataDict=queryData)
                    responseJson = response.json()
                    logging.info(f'Got {len(responseJson["data"])} looksrare events')
                    if len(responseJson['data']) == 0:
                        break
                    for event in responseJson['data']:
                        if date_util.datetime_from_string(event['createdAt'], dateFormat=MILLISECONDS_DATETIME_FORMAT) < startDate:
                            hasReachedEnd = True
                            break
                        tokenIdsToReprocess.add(event.get('token').get('tokenId'))
                        latestEventId = event['id']
                    queryData['pagination[cursor]'] = latestEventId
                    page += 1
            return list(tokenIdsToReprocess)

    async def _get_rarible_listings_for_token(self, registryAddress: str, tokenId: str) -> List[RetrievedTokenListing]:
        assetListings: List[RetrievedTokenListing] = []
        queryData: Dict[str, JSON1] = {
            'platform': 'RARIBLE',
            'itemId': f'ETHEREUM:{registryAddress}:{tokenId}',
            'status': 'ACTIVE',
            'size': 1000
        }
        index = 0
        pageCount = 0
        while True:
            logging.stat('RETRIEVE_LISTINGS_RARIBLE', registryAddress, float(f'{tokenId}.{index}'))
            response = await self.requester.get(url='https://api.rarible.org/v0.1/orders/sell/byItem', dataDict=queryData, timeout=30)
            responseJson = response.json()
            for order in responseJson['orders']:
                createdDate = _parse_date_string(dateString=order['createdAt'])
                startDate = _parse_date_string(dateString=order['startedAt']) if order.get('startedAt') else createdDate
                endDate = _parse_date_string(dateString=order['endedAt']) if order.get('endedAt') else date_util.datetime_from_datetime(dt=startDate, weeks=52*3)
                currentPrice = int(float(order['makePrice']) * 1000000000000000000)
                maker = order['maker']
                makerAddress = maker.split(':')[1]
                offererAddress = chain_util.normalize_address(makerAddress)
                sourceId = order['salt']
                isValueNative = order['take']['type']['@type'] == 'ETH'
                listing = RetrievedTokenListing(
                    registryAddress=registryAddress,
                    tokenId=order['make']['type']['tokenId'],
                    startDate=startDate,
                    endDate=endDate,
                    isValueNative=isValueNative,
                    value=currentPrice,
                    offererAddress=offererAddress,
                    source='rarible',
                    sourceId=sourceId,
                )
                assetListings.append(listing)
            continuationId = responseJson.get('continuation')
            if not continuationId:
                break
            await asyncio.sleep(0.25)
            queryData['continuation'] = continuationId
            pageCount += 1
        return assetListings

    async def get_rarible_listings_for_tokens(self, registryAddress: str, tokenIds: List[str]) -> List[RetrievedTokenListing]:
        async with self.lockManager.with_lock(name='rarible-requester', timeoutSeconds=10, expirySeconds=int(10 * len(tokenIds) / 100)):
            listings = []
            for chunkedTokenIds in list_util.generate_chunks(lst=tokenIds, chunkSize=100):
                listings += await asyncio.gather(*[self._get_rarible_listings_for_token(registryAddress=registryAddress, tokenId=tokenId) for tokenId in chunkedTokenIds])
            listings = [listing for listing in listings if listing is not None]
            allListings = [item for sublist in listings for item in sublist]
            return allListings

    async def get_changed_rarible_token_listings_for_collection(self, address: str, startDate: datetime.datetime) -> List[str]:
        secondsSinceStartDate = (date_util.datetime_from_now() - startDate).seconds
        async with self.lockManager.with_lock(name='rarible-requester', timeoutSeconds=10, expirySeconds=max(120, int(secondsSinceStartDate / 100))):
            tokenIdsToReprocess = set()
            queryData: Dict[str, JSON1] = {
                'collection': f"ETHEREUM:{address}",
                'type': ["CANCEL_LIST", "LIST"],
                'size': 50,
                'sort': "LATEST_FIRST"
            }
            cursor = None
            hasReachedEnd = False
            page = 0
            while not hasReachedEnd:
                logging.stat(f'RETRIEVE_CHANGED_LISTINGS_RARIBLE'.upper(), address, page)
                response = await self.requester.get(url='https://api.rarible.org/v0.1/activities/byCollection', dataDict=queryData, timeout=60)
                responseJson = response.json()
                logging.info(f'Got {len(responseJson["activities"])} rarible events')
                if len(responseJson['activities']) == 0:
                    break
                for activity in responseJson['activities']:
                    activityDate = _parse_date_string(dateString=activity["lastUpdatedAt"])
                    if activityDate < startDate:
                        hasReachedEnd = True
                        break
                    if activity["source"] != "RARIBLE":
                        continue
                    tokenIdsToReprocess.add(activity.get('make').get('tokenId'))
                cursor = responseJson.get('cursor')
                if not cursor:
                    break
                await asyncio.sleep(0.25)
                queryData['cursor'] = cursor
                page += 1
            return list(tokenIdsToReprocess)
