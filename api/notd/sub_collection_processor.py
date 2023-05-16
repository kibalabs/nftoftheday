# from typing import Optional

from core.exceptions import KibaException
from core.exceptions import NotFoundException
from core.requester import Requester

from notd.collection_manager import CollectionManager
from notd.model import OPENSEA_SHARED_STOREFRONT_ADDRESS
from notd.model import RetrievedSubCollection

# from notd.model import SubCollection


class SubCollectionDoesNotExist(NotFoundException):
    pass

class SubCollectionProcessor:

    def __init__(self, openseaRequester: Requester, collectionManager: CollectionManager) -> None:
        self.openseaRequester = openseaRequester
        self.collectionManager = collectionManager

    async def retrieve_sub_collection(self, registryAddress: str, externalId: str) -> RetrievedSubCollection:
        if registryAddress == OPENSEA_SHARED_STOREFRONT_ADDRESS:
            collection = await self.collectionManager.get_collection_by_address(address=registryAddress)
            collectionAssetUrl = f'https://api.opensea.io/api/v1/collection/{externalId}'
            collectionAssetResponse = await  self.openseaRequester.get(url=collectionAssetUrl, timeout=10)
            collectionAssetDict = collectionAssetResponse.json()
            return RetrievedSubCollection(
                registryAddress=registryAddress,
                externalId=collectionAssetDict.get('slug'),
                name=collectionAssetDict.get('name'),
                symbol=collectionAssetDict.get('symbol'),
                description=collectionAssetDict.get('description'),
                imageUrl=collectionAssetDict.get('image_url'),
                twitterUsername=collectionAssetDict.get('twitter_username'),
                instagramUsername=collectionAssetDict.get('instagram_username'),
                wikiUrl=collectionAssetDict.get('wiki_url'),
                openseaSlug=collectionAssetDict.get('slug'),
                url=collectionAssetDict.get('external_url'),
                discordUrl=collectionAssetDict.get('discord_url'),
                bannerImageUrl=collectionAssetDict.get('banner_image_url'),
                doesSupportErc721=collection.doesSupportErc721,
                doesSupportErc1155=collection.doesSupportErc1155,
            )
        raise KibaException(f"Unhandled registryAddress {registryAddress}")
