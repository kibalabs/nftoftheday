import asyncio
import datetime
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Tuple

from core import logging
from core.requester import Requester
from core.util import list_util

from notd.model import RetrievedTokenListing


class TokenListingProcessor:

    def __init__(self, requester: Requester, openseaRequester: Requester):
        self.requester = requester
        self.openseaRequester = openseaRequester

    async def get_opensea_listings_for_tokens(self, registryAddress: str, tokenIds: str) -> List[RetrievedTokenListing]:
        listings = []
        for chunkedTokenIs in list_util.generate_chunks(lst=tokenIds, chunkSize=30):
            logging.info(f'Getting opensea listings for {len(chunkedTokenIs)} tokens...')
            queryData = {
                'token_ids': chunkedTokenIs,
                'asset_contract_address': registryAddress,
                'include_orders': True,
                'limit': len(chunkedTokenIs),
            }
            response = await self.openseaRequester.get(url='https://api.opensea.io/api/v1/assets', dataDict=queryData, timeout=30)
            responseJson = response.json()
            for asset in responseJson['assets']:
                assetListings = []
                for sellOrder in (asset['sell_orders'] or []):
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
                for seaportSellOrder in (asset['seaport_sell_orders'] or []):
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
            await asyncio.sleep(0.1)
        return listings

    async def get_looks_rare_listings_for_collection(self, registryAddress: str) -> List[RetrievedTokenListing]:
        listings = []
        queryData = {
            'isOrderAsk':'true',
            'collection':registryAddress,
            'status[]':'VALID',
            'pagination[first]': 100,
            'sort':'PRICE_DESC',
        }
        flag = True
        assetListings = []
        while flag:
            response = await self.requester.get(url='https://api.looksrare.org/api/v1/orders', dataDict=queryData, timeout=30)
            responseJson = response.json()
            if len(responseJson['data']) == 0:
                flag = False
                break
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
                    source='LooksRare',
                    sourceId=sourceId,
                )
                assetListings.append(listing)
            queryData['pagination[cursor]'] = order['hash']
        tokenListingDict: Dict[str, RetrievedTokenListing] = defaultdict(RetrievedTokenListing)
        if len(assetListings) > 0:
            for listing in assetListings:
                tokenListingDict[listing.tokenId] = listing
            listings = list(tokenListingDict.values())
        return listings
