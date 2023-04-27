from typing import Optional
from core.requester import Requester


class SubCollectionTokenProcessor:

    def __init__(self, openseaRequester: Requester) -> None:
        self.openseaRequester = openseaRequester

    async def retrieve_collection_name(self, registryAddress: str, tokenId: str) -> Optional[str]:
        collectionName = None
        if registryAddress == '0x495f947276749Ce646f68AC8c248420045cb7b5e':
            tokenAssetUrl = f'https://api.opensea.io/api/v1/asset/{registryAddress}/{tokenId}/'
            tokenAssetResponse = await self.openseaRequester.get(url=tokenAssetUrl, timeout=10)
            tokenAssetDict = tokenAssetResponse.json()
            collectionName = tokenAssetDict.get('collection', {}).get('slug', None)
        return collectionName
