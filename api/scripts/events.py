import asyncio
import logging
import os
import sys


from core.requester import Requester
from core.util import date_util
from core.store.database import Database


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.token_listing_processor import TokenListingProcessor
from notd.store.schema import LatestTokenListingsTable
from notd.token_listing_processor import TokenListingProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver


async def test():
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    retriever = Retriever(database=database)
    saver = Saver(database=database)
    requester = Requester()
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=None)
    looksrareListing = await tokenListingProcessor.get_looks_rare_listings_for_collection(registryAddress='0xbce3781ae7ca1a5e050bd9c4c77369867ebc307e')
    # print(looksrareListing, len(looksrareListing))
    registryAddress = '0xbCe3781ae7Ca1a5e050Bd9C4c77369867eBc307e'
    endDate = date_util.datetime_from_now(minutes=-5)
    queryData = {
        'isOrderAsk': 'true',
        'collection': registryAddress,
        'status[]': ["EXPIRED", "CANCELLED", "EXECUTED", "VALID"],
        'pagination[first]': 150,
        'sort': "NEWEST"
    }
    looksrareTokensToReprocess = set()
    while True:
        response = await requester.get(url='https://api.looksrare.org/api/v1/orders', dataDict=queryData)
        responseJson = response.json()
        logging.info(f"Retrieved {len(responseJson['data'])} looksrareListings")
        if len(responseJson['data']) == 0:
            break
        for event in responseJson['data']:
            if event['startTime'] >=  int(endDate.timestamp()):
                looksrareTokensToReprocess.add((event['collectionAddress'], event['tokenId']))
        queryData['pagination[cursor]'] = event['hash']
    
    looksrareListing = await tokenListingProcessor.get_looksrare_listings_for_collection_tokens(registryAddress=registryAddress, tokenIds=list(looksrareTokensToReprocess))
    async with saver.create_transaction() as connection:
        existingLooksrareListingsQuery = (
            LatestTokenListingsTable.select()
                .with_only_columns([LatestTokenListingsTable.c.latestTokenListingId])
                .where(LatestTokenListingsTable.c.registryAddress == registryAddress)
                .where(LatestTokenListingsTable.c.tokenId.in_(looksrareTokensToReprocess))
                .where(LatestTokenListingsTable.c.source == 'looksrare')
        )
        existingLooksrareListingsResult = await retriever.database.execute(query=existingLooksrareListingsQuery, connection=connection)
        looksrareListingIdsToDelete = {row[0] for row in existingLooksrareListingsResult}
        await saver.delete_latest_token_listings(latestTokenListingIds=looksrareListingIdsToDelete, connection=connection)
        await saver.create_latest_token_listings(retrievedTokenListings=looksrareListing, connection=connection)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
