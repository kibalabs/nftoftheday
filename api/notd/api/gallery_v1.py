from typing import Optional
from fastapi import APIRouter

from notd.api.endpoints_v1 import CreateCustomizationForCollectionTokenRequest, TwitterLoginCallbackResponse, TwitterLoginResponse
from notd.api.endpoints_v1 import CreateCustomizationForCollectionTokenResponse
from notd.api.endpoints_v1 import GetCollectionAttributesResponse
from notd.api.endpoints_v1 import GetGalleryTokenResponse
from notd.api.endpoints_v1 import ListCollectionTokenAirdropsResponse
from notd.api.endpoints_v1 import QueryCollectionTokensRequest
from notd.api.endpoints_v1 import QueryCollectionTokensResponse
from notd.api.endpoints_v1 import SubmitTreasureHuntForCollectionTokenRequest
from notd.api.endpoints_v1 import SubmitTreasureHuntForCollectionTokenResponse
from notd.api.response_builder import ResponseBuilder
from notd.gallery_manager import GalleryManager


def create_api(galleryManager: GalleryManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.get('/twitter-login')
    async def twitter_login(initialUrl: str, randomStateValue: str) -> TwitterLoginResponse:
        await galleryManager.twitter_login(initialUrl=initialUrl, randomStateValue=randomStateValue)
        return TwitterLoginResponse()

    @router.get('/twitter-login-callback')
    async def twitter_login_callback(state: str, code: Optional[str] = None, error: Optional[str] = None) -> TwitterLoginCallbackResponse:
        await galleryManager.twitter_login_callback(state=state, code=code, error=error)
        return TwitterLoginCallbackResponse()

# http://localhost:5000/gallery/v1/twitter-login-callback?state=eyJpbml0aWFsVXJsIjogImh0dHA6Ly9sb2NhbGhvc3Q6MzAwMC9hY2NvdW50cy8weDE4MDkwY0RBNDlCMjFkRUFmZkMyMWI0Rjg4NmFlZDNlQjc4N2QwMzIiLCAicmFuZG9tU3RhdGVWYWx1ZSI6ICJiMGM3Njc2Mi00ZGM0LTRlNjYtYTIyNi0yNjk5M2Y5OTI0ZTQifQ%3D%3D&code=SWZMY3JmVmFjb3NRUHdtdHBSdGJRS2JZLWVJMlFXYy1qN0k2aXFrMnAzdm1zOjE2NjA2MzkwODA1Nzk6MTowOmFjOjE

    @router.get('/collections/{registryAddress}/tokens/{tokenId}')
    async def get_gallery_token(registryAddress: str, tokenId: str) -> GetGalleryTokenResponse:
        galleryToken = await galleryManager.get_gallery_token(registryAddress=registryAddress, tokenId=tokenId)
        return GetGalleryTokenResponse(galleryToken=(await responseBuilder.gallery_token_from_model(galleryToken=galleryToken)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/airdrops', response_model=ListCollectionTokenAirdropsResponse)
    async def list_collection_token_airdrops(registryAddress: str, tokenId: str):
        airdrops = await galleryManager.list_collection_token_airdrops(registryAddress=registryAddress, tokenId=tokenId)
        return ListCollectionTokenAirdropsResponse(airdrops=(await responseBuilder.airdrops_from_models(airdrops=airdrops)))

    @router.get('/collections/{registryAddress}/attributes', response_model=GetCollectionAttributesResponse)
    async def get_collection_attributes(registryAddress: str):
        collectionAttributes = await galleryManager.get_collection_attributes(registryAddress=registryAddress)
        return GetCollectionAttributesResponse(attributes=(await responseBuilder.collection_attributes_from_models(collectionAttributes=collectionAttributes)))

    # TODO(krishan711): make this a GET request once we understand complex query params
    @router.post('/collections/{registryAddress}/tokens/query')
    async def query_collection_tokens(registryAddress: str, request: QueryCollectionTokensRequest) -> QueryCollectionTokensResponse:
        limit = request.limit if request.limit is not None else 20
        offset = request.offset if request.offset is not None else 0
        galleryTokens = await galleryManager.query_collection_tokens(registryAddress=registryAddress, ownerAddress=request.ownerAddress, minPrice=request.minPrice, maxPrice=request.maxPrice, isListed=request.isListed, tokenIdIn=request.tokenIdIn, attributeFilters=request.attributeFilters, limit=limit, offset=offset)
        # NOTE(krishan711): remove tokens once gallery is updated
        return QueryCollectionTokensResponse(
            tokens=(await responseBuilder.collection_tokens_from_models(tokenMetadatas=[galleryToken.tokenMetadata for galleryToken in galleryTokens])),
            galleryTokens=(await responseBuilder.gallery_tokens_from_models(galleryTokens=galleryTokens)),
        )

    @router.post('/collections/{registryAddress}/tokens/{tokenId}/submit-treasure-hunt')
    async def submit_treasure_hunt_for_collection_token(registryAddress: str, tokenId: str, request: SubmitTreasureHuntForCollectionTokenRequest) -> SubmitTreasureHuntForCollectionTokenResponse:
        await galleryManager.submit_treasure_hunt_for_collection_token(registryAddress=registryAddress, tokenId=tokenId, userAddress=request.userAddress, signature=request.signature)
        return SubmitTreasureHuntForCollectionTokenResponse()

    @router.post('/collections/{registryAddress}/tokens/{tokenId}/customizations')
    async def create_customization_for_collection_token(registryAddress: str, tokenId: str, request: CreateCustomizationForCollectionTokenRequest) -> CreateCustomizationForCollectionTokenResponse:
        tokenCustomization = await galleryManager.create_customization_for_collection_token(registryAddress=registryAddress, tokenId=tokenId, creatorAddress=request.creatorAddress, signature=request.signature, blockNumber=request.blockNumber,name=request.name, description=request.description)
        return CreateCustomizationForCollectionTokenResponse(tokenCustomization=(await responseBuilder.token_customization_from_model(tokenCustomization=tokenCustomization)))

    return router
