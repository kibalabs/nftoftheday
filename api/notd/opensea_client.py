from notd.core.requester import Requester
from notd.core.util import date_util
from notd.model import RegistryToken

class OpenseaClient:

    def __init__(self, requester: Requester):
        self.requester = requester

    async def retreive_registry_token(self, registryAddress: str, tokenId: str) -> RegistryToken:
        response = await self.requester.get(url=f'https://api.opensea.io/api/v1/asset/{registryAddress}/{tokenId}')
        responseJson = response.json()
        registryToken = RegistryToken(
            name=responseJson['name'],
            imageUrl=responseJson['animation_original_url'] or responseJson['animation_url'] or responseJson['image_url'] or responseJson['original_image_url'],
            openSeaUrl=f"{responseJson['permalink']}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032",
            externalUrl=responseJson['external_link'],
            lastSaleDate=date_util.datetime_from_string(dateString=responseJson['last_sale']['created_date']) if responseJson.get('last_sale') else None,
            lastSalePrice=int(responseJson['last_sale']['total_price']) if responseJson.get('last_sale') else None,
            collectionName=responseJson['collection']['name'],
            collectionImageUrl=responseJson['collection']['large_image_url'] or responseJson['collection']['image_url'],
            collectionOpenSeaUrl=f"{responseJson['collection']['permalink']}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032" if responseJson['collection'].get('permalink') else None,
            collectionExternalUrl=responseJson['collection']['external_url'],
        )
        return registryToken
