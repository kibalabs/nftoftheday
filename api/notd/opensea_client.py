import asyncio
import logging

from core.exceptions import NotFoundException
from core.requester import Requester
from core.requester import ResponseException
from core.util import date_util

from notd.model import RegistryToken


class OpenseaClient:

    def __init__(self, requester: Requester):
        self.requester = requester

    async def retreive_registry_token(self, registryAddress: str, tokenId: str) -> RegistryToken:
        response = None
        retryCount = 0
        while not response:
            try:
                response = await self.requester.get(url=f'https://api.opensea.io/api/v1/asset/{registryAddress}/{tokenId}')
            except ResponseException as exception:
                if exception.statusCode == 404:
                    raise NotFoundException()
                if exception.statusCode != 429 or retryCount >= 3:
                    raise
                logging.info(f'Retrying due to: {str(exception)}')
                await asyncio.sleep(1.5)
                retryCount += 1
        responseJson = response.json()
        registryToken = RegistryToken(
            registryAddress = registryAddress,
            tokenId = tokenId,
            name=responseJson.get('name') or f"{responseJson.get('collection', {}).get('name')} #{tokenId}",
            imageUrl=responseJson.get('animation_original_url') or responseJson.get('animation_url') or responseJson.get('image_url') or responseJson.get('original_image_url') or responseJson.get('image_original_url'),
            openSeaUrl=f"{responseJson['permalink']}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032",
            externalUrl=responseJson.get('external_link'),
            lastSaleDate=date_util.datetime_from_string(dateString=responseJson['last_sale']['created_date']) if responseJson.get('last_sale') else None,
            lastSalePrice=int(responseJson['last_sale']['total_price']) if responseJson.get('last_sale') else None,
            collectionName=responseJson.get('collection', {}).get('name'),
            collectionImageUrl=responseJson.get('collection', {}).get('large_image_url') or responseJson.get('collection', {}).get('image_url'),
            collectionOpenSeaUrl=f"{responseJson.get('collection', {}).get('permalink')}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032" if responseJson.get('collection', {}).get('permalink') else None,
            collectionExternalUrl=responseJson.get('collection', {}).get('external_url'),
        )
        return registryToken
