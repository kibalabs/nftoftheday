from typing import Optional

from fastapi import APIRouter

from notd.api.endpoints_v1 import CreateCustomizationForCollectionTokenRequest
from notd.api.endpoints_v1 import CreateCustomizationForCollectionTokenResponse
from notd.api.endpoints_v1 import GetCollectionAttributesResponse
from notd.api.endpoints_v1 import GetGalleryCollectionUserResponse
from notd.api.endpoints_v1 import GetGalleryTokenResponse
from notd.api.endpoints_v1 import ListCollectionTokenAirdropsResponse
from notd.api.endpoints_v1 import QueryCollectionTokensRequest
from notd.api.endpoints_v1 import QueryCollectionTokensResponse
from notd.api.endpoints_v1 import QueryCollectionUsersRequest
from notd.api.endpoints_v1 import QueryCollectionUsersResponse
from notd.api.endpoints_v1 import SubmitTreasureHuntForCollectionTokenRequest
from notd.api.endpoints_v1 import SubmitTreasureHuntForCollectionTokenResponse
from notd.api.endpoints_v1 import TwitterLoginCallbackResponse
from notd.api.endpoints_v1 import TwitterLoginResponse
from notd.api.response_builder import ResponseBuilder
from notd.gallery_manager import GalleryManager


def create_api(galleryManager: GalleryManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.get('/twitter-login')
    async def twitter_login(account: str, signatureJson: str, initialUrl: str) -> TwitterLoginResponse:
        await galleryManager.twitter_login(account=account, signatureJson=signatureJson, initialUrl=initialUrl)
        return TwitterLoginResponse()

    @router.get('/twitter-login-callback')
    async def twitter_login_callback(state: str, code: Optional[str] = None, error: Optional[str] = None) -> TwitterLoginCallbackResponse:
        await galleryManager.twitter_login_callback(state=state, code=code, error=error)
        return TwitterLoginCallbackResponse()

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
        return QueryCollectionTokensResponse(galleryTokens=(await responseBuilder.gallery_tokens_from_models(galleryTokens=galleryTokens)))

    @router.post('/collections/{registryAddress}/tokens/{tokenId}/submit-treasure-hunt')
    async def submit_treasure_hunt_for_collection_token(registryAddress: str, tokenId: str, request: SubmitTreasureHuntForCollectionTokenRequest) -> SubmitTreasureHuntForCollectionTokenResponse:
        await galleryManager.submit_treasure_hunt_for_collection_token(registryAddress=registryAddress, tokenId=tokenId, userAddress=request.userAddress, signature=request.signature)
        return SubmitTreasureHuntForCollectionTokenResponse()

    @router.post('/collections/{registryAddress}/tokens/{tokenId}/customizations')
    async def create_customization_for_collection_token(registryAddress: str, tokenId: str, request: CreateCustomizationForCollectionTokenRequest) -> CreateCustomizationForCollectionTokenResponse:
        tokenCustomization = await galleryManager.create_customization_for_collection_token(registryAddress=registryAddress, tokenId=tokenId, creatorAddress=request.creatorAddress, signature=request.signature, blockNumber=request.blockNumber,name=request.name, description=request.description)
        return CreateCustomizationForCollectionTokenResponse(tokenCustomization=(await responseBuilder.token_customization_from_model(tokenCustomization=tokenCustomization)))

    # TODO(krishan711): make this a GET request once we understand complex query params
    @router.post('/collections/{registryAddress}/users/query')
    async def query_collection_users(registryAddress: str, request: QueryCollectionUsersRequest) -> QueryCollectionUsersResponse:
        limit = request.limit if request.limit is not None else 20
        offset = request.offset if request.offset is not None else 0
        galleryUserRowListResponse = await galleryManager.query_collection_users(registryAddress=registryAddress, order=request.order, limit=limit, offset=offset)
        return QueryCollectionUsersResponse(galleryUserRowListResponse=(await responseBuilder.gallery_user_row_list_response_from_model(galleryUserRowListResponse=galleryUserRowListResponse)))

    @router.get('/collections/{registryAddress}/users/{userAddress}')
    async def get_gallery_user(registryAddress: str, userAddress: str) -> GetGalleryCollectionUserResponse:
        galleryUser = await galleryManager.get_gallery_user(registryAddress=registryAddress, userAddress=userAddress)
        return GetGalleryCollectionUserResponse(galleryUser=(await responseBuilder.gallery_user_from_model(galleryUser=galleryUser)))

    return router
