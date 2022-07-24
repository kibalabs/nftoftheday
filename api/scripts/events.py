import asyncio
import logging
import os
import sys


from core.requester import Requester
from core.util import date_util

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.token_listing_processor import TokenListingProcessor


async def test():
    requester = Requester()
    # tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=None)
    # looksrareListing = await tokenListingProcessor.get_looks_rare_listings_for_collection(registryAddress='0xbce3781ae7ca1a5e050bd9c4c77369867ebc307e')
    # print(looksrareListing, len(looksrareListing))
    registryAddress = '0xbce3781ae7ca1a5e050bd9c4c77369867ebc307e'
    endDate = date_util.datetime_from_now()
    startDate = date_util.datetime_from_datetime(endDate, hours=-24)
    tokens = []
    queryData = {
        'collection': registryAddress,
        'type': "LIST",
        'pagination[first]': 150
    }
    while startDate < endDate:
        print('here')
        #print(date_util.datetime_from_datetime(startDate, hours=+1))
        response = await requester.get(url='https://api.looksrare.org/api/v1/events', dataDict=queryData)
        responseJson = response.json()
        # print(len(responseJson['data']), int(startDate.timestamp()))
        if len(responseJson['data']) == 0:
            break
        for event in responseJson['data']:
            if event['order']['startTime'] >=  int(startDate.timestamp()):
                tokens.append((event['token']['collectionAddress'], event['token']['tokenId']))
                print(event['id'])
        queryData['pagination[cursor]'] = event['id']
        print(tokens)
        startDate = date_util.datetime_from_datetime(startDate, hours=+1)
        


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
