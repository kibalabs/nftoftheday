import asyncio
import logging
import os
import sys
import time


from core.requester import Requester
from core.util import date_util
from core.exceptions import NotFoundException
from core.store.database import Database
import pandas as pd



sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.schema import LatestTokenListingsTable
from notd.token_listing_processor import TokenListingProcessor
from notd.model import COLLECTION_SPRITE_CLUB_ADDRESS, COLLECTION_GOBLINTOWN_ADDRESS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
openseaApiKey = os.environ['OPENSEA_API_KEY']


async def test():
    startHour = date_util.start_of_day()
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    requester = Requester()
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester)
    registryAddress = COLLECTION_GOBLINTOWN_ADDRESS
    events = []
    queryData = {
        'asset_contract_address': registryAddress,
        'occurred_after': startHour,
        'event_type': ['transfer','successful','cancelled','created']
    }
    col =['Event timestamp', 'tokenId', 'event_type']
    data = []
    await database.connect()
    tokensToReprocess = set()
    while True:
        response = await openseaRequester.get(url="https://api.opensea.io/api/v1/events", dataDict=queryData, timeout=600)
        responseJson = response.json()
        print(f'Got {len(responseJson["asset_events"])} items')
        if len(responseJson['asset_events']) == 0:
            break
        for asset in responseJson['asset_events']:
            if asset['asset'] and asset.get('event_type') != 'bid_entered':
                    data.append([asset.get('event_timestamp'), asset.get('asset').get('token_id'),asset.get('event_type')])
                    tokensToReprocess.add(asset['asset']['token_id'])
        if responseJson['next'] is None:
            break
        queryData['cursor'] = responseJson['next']
        await asyncio.sleep(0.5)
        
    pd.DataFrame(data=data,columns=col).to_csv(f'{startHour}.csv')

    async with saver.create_transaction() as connection:
        query = (
            LatestTokenListingsTable.select()
                .with_only_columns([LatestTokenListingsTable.c.latestTokenListingId])
                .where(LatestTokenListingsTable.c.registryAddress == registryAddress)
                .where(LatestTokenListingsTable.c.tokenId.in_(tokensToReprocess))
        )
        result = await retriever.database.execute(query=query, connection=connection)
        latestTokenListingIdsToDelete = {row[0] for row in result}
        await saver.delete_latest_token_listings(latestTokenListingIds=latestTokenListingIdsToDelete, connection=connection)
        openseaListings = await tokenListingProcessor.get_opensea_listings_for_tokens(registryAddress=registryAddress, tokenIds=list(tokensToReprocess))
        await saver.create_latest_token_listings(retrievedTokenListings=openseaListings, connection=connection)
                    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
