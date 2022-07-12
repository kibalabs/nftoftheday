from typing import Optional

from fastapi import APIRouter

from notd.api.endpoints_v1 import GetCollectionAttributesResponse
from notd.api.endpoints_v1 import GetTokensWithAttributeResponse
from notd.api.endpoints_v1 import ListCollectionTokenAirdropsResponse
from notd.api.response_builder import ResponseBuilder
from notd.gallery_manager import GalleryManager


def create_api(galleryManager: GalleryManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/airdrops', response_model=ListCollectionTokenAirdropsResponse)
    async def list_collection_token_airdrops(registryAddress: str, tokenId: str):
        airdrops = await galleryManager.list_collection_token_airdrops(registryAddress=registryAddress, tokenId=tokenId)
        return ListCollectionTokenAirdropsResponse(airdrops=(await responseBuilder.airdrops_from_models(airdrops=airdrops)))

    @router.get('/collections/{registryAddress}/attributes', response_model=GetCollectionAttributesResponse)
    async def get_collection_attributes(registryAddress: str):
        attributes = await galleryManager.get_collection_attributes(registryAddress=registryAddress)
        return GetCollectionAttributesResponse(attributes=(await responseBuilder.attributes_from_models(attributes=attributes)))

    @router.get('/collections/{registryAddress}/tokens', response_model=GetTokensWithAttributeResponse)
    async def get_tokens_with_attributes(registryAddress: str, attributeName: Optional[str], attributeValue: Optional[str],attributeName2: Optional[str], attributeValue2: Optional[str], limit: Optional[int] = None, offset: Optional[int] = None):
        limit = limit if limit is not None else 20
        offset = offset if offset is not None else 0
        tokens = await galleryManager.get_tokens_with_attributes(registryAddress=registryAddress, attributeName=attributeName, attributeValue=attributeValue,attributeName2=attributeName2, attributeValue2=attributeValue2, limit=limit, offset=offset)
        return GetTokensWithAttributeResponse(tokens=(await responseBuilder.collection_token_from_registry_addresses_token_ids(tokens=tokens)))
    return router
