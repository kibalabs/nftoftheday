
from core.requester import Requester

from notd.model import OPENSEA_SHARED_STOREFRONT_ADDRESS
from notd.model import SubCollectionKey


class SubCollectionTokenProcessor:

    def __init__(self, openseaRequester: Requester) -> None:
        self.openseaRequester = openseaRequester

    async def retrieve_sub_collection_name(self, registryAddress: str, tokenId: str) -> SubCollectionKey:
        collectionName = None
        if registryAddress == OPENSEA_SHARED_STOREFRONT_ADDRESS:
            tokenAssetUrl = f'https://api.opensea.io/api/v1/asset/{registryAddress}/{tokenId}/'
            tokenAssetResponse = await self.openseaRequester.get(url=tokenAssetUrl, timeout=10)
            tokenAssetDict = tokenAssetResponse.json()
            collectionName = tokenAssetDict.get('collection', {}).get('slug', None)
            return SubCollectionKey(registryAddress=registryAddress, externalId=collectionName)
        return
