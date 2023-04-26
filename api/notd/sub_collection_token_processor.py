from core.requester import Requester


class SubCollectionTokenProcessor:

    def __init__(self, requester: Requester) -> None:
        self.requester = requester

    async def retrieve_collection_name(self, registryAddress: str, tokenId: str) -> str:
        if registryAddress == '0x495f947276749Ce646f68AC8c248420045cb7b5e':
            headers = {'X-API-KEY': f'{OPENSEA_API_KEY'}
            tokenAssetUrl = f'https://api.opensea.io/api/v1/asset/{registryAddress}/{tokenId}/'
            tokenAssetResponse = await self.requester.get(url=tokenAssetUrl, timeout=10, headers=headers)
            tokenAssetDict = tokenAssetResponse.json()
        return tokenAssetDict.get('collection').get('slug')
