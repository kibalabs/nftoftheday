
import asyncio
import datetime
import logging
import os
import sys
from core.requester import Requester
import pandas as pd


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.model import RetrievedTokenListing

async def test():
    requester = Requester()
    queryData = { 
        'isOrderAsk':'true',
        'collection':'0xbce3781ae7ca1a5e050bd9c4c77369867ebc307e',
        'status[]':'VALID',
        'pagination[first]': 100,
        'sort':'PRICE_ASC',
    }
    flag = True
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
            #Note(Femi-Ogunkola): Confirm what the signer address is
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
    pd.DataFrame(assetListings).to_csv('globin_town.csv')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
