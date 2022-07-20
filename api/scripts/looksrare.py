import asyncio
import datetime
import logging
import os
import sys
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Tuple

from core.requester import Requester

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import RetrievedTokenListing


async def test():
    requester = Requester()
    queryData = {
        'isOrderAsk':'true',
        'collection':'0xbCe3781ae7Ca1a5e050Bd9C4c77369867eBc307e',
        'status[]':'VALID',
        'pagination[first]': 100,
        'sort':'PRICE_ASC',
    }
    flag = True
    listings = []
    assetListings = []
    while flag:
        response = await requester.get(url='https://api.looksrare.org/api/v1/orders', dataDict=queryData, timeout=30)
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
        tokenListingDict: Dict[Tuple(str, str), RetrievedTokenListing] = defaultdict(RetrievedTokenListing)
        if len(assetListings) > 0:
            sortedAssetListings: List[RetrievedTokenListing] = sorted(assetListings, key=lambda listing: listing.value, reverse=True)
            for listing in sortedAssetListings:
                tokenListingDict[listing.registryAddress,listing.tokenId] = listing 
            listings = list(tokenListingDict.values())
        return listings

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
