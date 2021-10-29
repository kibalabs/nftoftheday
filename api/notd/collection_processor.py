import asyncio
import logging
from typing import Collection
from core.exceptions import NotFoundException
from core.requester import Requester, ResponseException


from notd.model import RetrievedCollection

class CollectionDoesNotExist(NotFoundException):
    pass

class CollectionProcessor:
    def __init__(self, requester: Requester):
        self.requester = requester

    async def retrieve_collection(self,address) -> RetrievedCollection:
        response = 0 
        retryCount = 0
        while not response:
            try:
                response = await self.requester.get(url=f'https://api.opensea.io/api/v1/asset_contract/{address}')
            except ResponseException as exception:
                if exception.statusCode == 404:
                    raise NotFoundException()
                if exception.statusCode != 429 or retryCount >= 3:
                    raise
                logging.info(f'Retrying due to: {str(exception)}')
                await asyncio.sleep(1.5)
                retryCount += 1
        responseJson = response.json()
        collection = responseJson.get('collection')
        if collection is None:
            raise CollectionDoesNotExist()
        
        retrievedCollection = RetrievedCollection(
            address=address,
            name=collection.get('name'),
            symbol=collection.get('symbol'),
            description=collection.get('description'),
            imageUrl=collection.get('image_url'),
            twitterUsername=collection.get('twitter_username'),
            instagramUsername=collection.get('instagram_username'),
            wikiUrl=collection.get('wiki_url'),
            openseaSlug=collection.get('slug'),
            url=collection.get('external_url'),
            discordUrl=collection.get('discord_url'),
            bannerImageUrl=collection.get('banner_image_url'),
        )
        logging.info(f'{retrievedCollection}')
        return retrievedCollection
