import asyncio
import logging
import os
import sys
import time


from core.requester import Requester
from core.util import date_util
from core.exceptions import NotFoundException
from core.store.database import Database



sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.token_listing_processor import TokenListingProcessor
from notd.model import COLLECTION_SPRITE_CLUB_ADDRESS, COLLECTION_GOBLINTOWN_ADDRESS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
openseaApiKey = os.environ['OPENSEA_API_KEY']


async def test():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["REMOTE_DB_USERNAME"], password=os.environ["REMOTE_DB_PASSWORD"], host=os.environ["REMOTE_DB_HOST"], port=os.environ["REMOTE_DB_PORT"], name=os.environ["REMOTE_DB_NAME"])
    # databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    requester = Requester()
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester)
    registryAddress = COLLECTION_GOBLINTOWN_ADDRESS
    startHour = date_util.datetime_from_string('2022-07-26T19:04:00.000000')
    endHour = date_util.datetime_from_datetime(dt=startHour, minutes=10)
    queryData = {
        'asset_contract_address': registryAddress,
        "occurred_after": startHour,
    }
    await database.connect()
    while startHour< endHour:
        #print(startHour, 'after')
        tokensToReprocess = []
        queryData['occurred_after'] = startHour
        queryData['occurred_before'] = date_util.datetime_from_datetime(dt=startHour, minutes=5)
        response = await openseaRequester.get(url="https://api.opensea.io/api/v1/events", dataDict=queryData)
        responseJson = response.json()
        for asset in responseJson['asset_events']:
            if asset['event_type']:
                print(asset['event_timestamp'])
                tokensToReprocess.append(asset['asset']['token_id'])
            
        #print('tokensToReprocess', tokensToReprocess)
        openseaListing = await tokenListingProcessor.get_opensea_listings_for_tokens(registryAddress=registryAddress, tokenIds=tokensToReprocess)
        #print(openseaListing)
        for listing in openseaListing:
            try:
                latestTokenListing = await retriever.get_latest_token_listing_by_registryAddress_token_id(registryAddress=listing.registryAddress, tokenId=listing.tokenId)
            except NotFoundException:
                latestTokenListing = None
            if not latestTokenListing:
                print('create',listing.tokenId)
                # await saver.create_latest_token_listing(retrievedTokenListings=listing, connection=connection)
            else:
                if listing.value < latestTokenListing.value:
                    print('delete',listing.tokenId)
                    #logging.info(f'Deleting existing listings')
                    # await saver.delete_latest_token_listing(latestTokenListingId=latestTokenListing.tokenListingId, connection=connection)
                    # logging.info(f'Saving listings')
                    # await saver.create_latest_token_listing(retrievedTokenListings=listing, connection=connection)
                    
            
        await asyncio.sleep(0.2)
        startHour =  date_util.datetime_from_datetime(startHour, minutes=5)
        


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
