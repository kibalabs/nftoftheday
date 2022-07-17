import asyncio
import datetime
from typing import List

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
