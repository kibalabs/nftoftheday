
import asyncio
import datetime
import logging
import os
import sys
from core.requester import Requester


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import RetrievedTokenListing

async def test():
    requester = Requester()
    queryData = {
                'collection': '0x2744fE5e7776BCA0AF1CDEAF3bA3d1F5cae515d3',
                'type': 'LIST',
            }

    response = await requester.get(url='https://api.looksrare.org/api/v1/events', dataDict=queryData)
    responseJson = response.json()
    assetListings = []
    for event in responseJson['data']:
        if event['order']['status'] == "CANCELLED":
            continue
        if event['order']['status'] == "EXPIRED":
            continue
        if event['order']['status'] == "INVALID_OWNER":
            continue
        print( event['order']['status'])
        startDate = datetime.datetime.utcfromtimestamp(event['order']["startTime"])
        endDate = datetime.datetime.utcfromtimestamp(event['order']["endTime"])
        currentPrice = int(event['order']["price"])
        offererAddress = event['from']
        sourceId = event['order']["hash"]
        isValueNative = event['order']["currencyAddress"] == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        listing = RetrievedTokenListing(
            registryAddress=event['order']['collectionAddress'],
            tokenId=event['order']['tokenId'],
            startDate=startDate,
            endDate=endDate,
            isValueNative=isValueNative,
            value=currentPrice,
            offererAddress=offererAddress,
            source='LooksRare',
            sourceId=sourceId,
        )
        assetListings.append(listing)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())