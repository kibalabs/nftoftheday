from typing import Optional

from fastapi import APIRouter

from notd.api.endpoints_v1 import CollectionAssignBadgeRequest
from notd.api.endpoints_v1 import CollectionAssignBadgeResponse
from notd.api.endpoints_v1 import CreateCustomizationForCollectionTokenRequest
from notd.api.endpoints_v1 import CreateCustomizationForCollectionTokenResponse
from notd.api.endpoints_v1 import FollowCollectionUserRequest
from notd.api.endpoints_v1 import FollowCollectionUserResponse
from notd.api.endpoints_v1 import GetCollectionAttributesResponse
from notd.api.endpoints_v1 import GetGalleryCollectionUserResponse
from notd.api.endpoints_v1 import GetGalleryTokenResponse
from notd.api.endpoints_v1 import GetGalleryUserOwnedCollectionsResponse
from notd.api.endpoints_v1 import ListCollectionTokenAirdropsResponse
from notd.api.endpoints_v1 import ListEntriesInSuperCollectionResponse
from notd.api.endpoints_v1 import ListGalleryCollectionOverlapOwnersResponse
from notd.api.endpoints_v1 import ListGalleryCollectionOverlapsResponse
from notd.api.endpoints_v1 import ListGalleryCollectionOverlapSummariesResponse
from notd.api.endpoints_v1 import ListGallerySuperCollectionOverlapsResponse
from notd.api.endpoints_v1 import ListGallerySuperCollectionOverlapSummariesResponse
from notd.api.endpoints_v1 import ListGalleryUserBadgesResponse
from notd.api.endpoints_v1 import QueryCollectionTokensRequest
from notd.api.endpoints_v1 import QueryCollectionTokensResponse
from notd.api.endpoints_v1 import QueryCollectionUsersRequest
from notd.api.endpoints_v1 import QueryCollectionUsersResponse
from notd.api.endpoints_v1 import QuerySuperCollectionUsersRequest
from notd.api.endpoints_v1 import QuerySuperCollectionUsersResponse
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
    async def list_collection_token_airdrops(registryAddress: str, tokenId: str) -> ListCollectionTokenAirdropsResponse:
        airdrops = await galleryManager.list_collection_token_airdrops(registryAddress=registryAddress, tokenId=tokenId)
        return ListCollectionTokenAirdropsResponse(airdrops=(await responseBuilder.airdrops_from_models(airdrops=airdrops)))

    @router.get('/collections/{registryAddress}/attributes', response_model=GetCollectionAttributesResponse)
    async def get_collection_attributes(registryAddress: str) -> GetCollectionAttributesResponse:
        collectionAttributes = await galleryManager.get_collection_attributes(registryAddress=registryAddress)
        return GetCollectionAttributesResponse(attributes=(await responseBuilder.collection_attributes_from_models(collectionAttributes=collectionAttributes)))

    # TODO(krishan711): make this a GET request once we understand complex query params
    @router.post('/collections/{registryAddress}/tokens/query')
    async def query_collection_tokens(registryAddress: str, request: QueryCollectionTokensRequest) -> QueryCollectionTokensResponse:
        limit = request.limit if request.limit is not None else 20
        offset = request.offset if request.offset is not None else 0
        galleryTokens = await galleryManager.query_collection_tokens(registryAddress=registryAddress, ownerAddress=request.ownerAddress, minPrice=request.minPrice, maxPrice=request.maxPrice, isListed=request.isListed, tokenIdIn=request.tokenIdIn, attributeFilters=request.attributeFilters, limit=limit, offset=offset, order=request.order)
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

    @router.get('/collections/{registryAddress}/users/{userAddress}/badges')
    async def list_gallery_user_badges(registryAddress: str, userAddress: str) -> ListGalleryUserBadgesResponse:
        galleryUserBadges = await galleryManager.list_gallery_user_badges(registryAddress=registryAddress, userAddress=userAddress)
        return ListGalleryUserBadgesResponse(galleryUserBadges=(await responseBuilder.gallery_user_badges_from_models(galleryBadgeHolders=galleryUserBadges)))

    @router.post('/collections/{registryAddress}/user/{userAddress}/badges/assign')
    async def assign_badge(registryAddress: str, userAddress: str, request: CollectionAssignBadgeRequest) -> CollectionAssignBadgeResponse:
        achievedDate = request.achievedDate.replace(tzinfo=None)
        await galleryManager.assign_badge(registryAddress=registryAddress, ownerAddress=userAddress, badgeKey=request.badgeKey, assignerAddress=request.assignerAddress, achievedDate=achievedDate, signature=request.signature)
        return CollectionAssignBadgeResponse()

    @router.post('/collections/{registryAddress}/users/{userAddress}/follow')
    async def follow_gallery_user(registryAddress: str, userAddress: str, request: FollowCollectionUserRequest) -> FollowCollectionUserResponse:
        await galleryManager.follow_gallery_user(registryAddress=registryAddress, userAddress=userAddress, account=request.account, signatureMessage=request.signatureMessage, signature=request.signature)
        return FollowCollectionUserResponse()

    @router.get('/collections/{registryAddress}/users/{userAddress}/owned-collections')
    async def get_gallery_user_owned_collections(registryAddress: str, userAddress: str) -> GetGalleryUserOwnedCollectionsResponse:
        ownedCollections = await galleryManager.get_gallery_user_owned_collections(registryAddress=registryAddress, userAddress=userAddress)
        return GetGalleryUserOwnedCollectionsResponse(ownedCollections=(await responseBuilder.owned_collections_from_models(ownedCollections=ownedCollections)))

    @router.get('/collections/{registryAddress}/overlap-summaries')
    async def list_gallery_collection_overlap_summaries(registryAddress: str) -> ListGalleryCollectionOverlapSummariesResponse:
        collectionOverlapSummaries = await galleryManager.list_gallery_collection_overlap_summaries(registryAddress=registryAddress)
        return ListGalleryCollectionOverlapSummariesResponse(collectionOverlapSummaries=(await responseBuilder.collection_overlap_summaries_from_models(collectionOverlapSummaries=collectionOverlapSummaries)))

    @router.get('/collections/{registryAddress}/overlaps')
    async def list_gallery_collection_overlaps(registryAddress: str, otherRegistryAddress: Optional[str]) -> ListGalleryCollectionOverlapsResponse:
        collectionOverlaps = await galleryManager.list_gallery_collection_overlaps(registryAddress=registryAddress, otherRegistryAddress=otherRegistryAddress)
        return ListGalleryCollectionOverlapsResponse(collectionOverlaps=(await responseBuilder.collection_overlaps_from_models(collectionOverlaps=collectionOverlaps)))

    @router.get('/collections/{registryAddress}/overlap-owners')
    async def list_gallery_collection_overlap_owners(registryAddress: str) -> ListGalleryCollectionOverlapOwnersResponse:
        collectionOverlapOwners = await galleryManager.list_gallery_collection_overlap_owners(registryAddress=registryAddress)
        return ListGalleryCollectionOverlapOwnersResponse(collectionOverlapOwners=(await responseBuilder.collection_overlap_owners_from_models(collectionOverlapOwners=collectionOverlapOwners)))

    @router.get('/super-collections/{superCollectionName}/entries')
    async def list_entries_in_super_collection(superCollectionName: str) -> ListEntriesInSuperCollectionResponse:
        superCollectionEntries = await galleryManager.list_entries_in_super_collection(superCollectionName=superCollectionName)
        return ListEntriesInSuperCollectionResponse(superCollectionEntries=(await responseBuilder.super_collection_entries_from_models(superCollectionEntries=superCollectionEntries)))

    @router.get('/super-collections/{superCollectionName}/overlap-summaries')
    async def list_gallery_super_collection_overlap_summaries(superCollectionName: str) -> ListGallerySuperCollectionOverlapSummariesResponse:
        collectionOverlapSummaries = await galleryManager.list_gallery_super_collection_overlap_summaries(superCollectionName=superCollectionName)
        return ListGallerySuperCollectionOverlapSummariesResponse(collectionOverlapSummaries=(await responseBuilder.collection_overlap_summaries_from_models(collectionOverlapSummaries=collectionOverlapSummaries)))

    @router.get('/super-collections/{superCollectionName}/overlaps')
    async def list_gallery_super_collection_overlaps(superCollectionName: str, otherRegistryAddress: str) -> ListGallerySuperCollectionOverlapsResponse:
        superCollectionOverlaps = await galleryManager.list_gallery_super_collection_overlaps(superCollectionName=superCollectionName, otherRegistryAddress=otherRegistryAddress)
        return ListGallerySuperCollectionOverlapsResponse(superCollectionOverlaps=(await responseBuilder.super_collection_overlaps_from_models(superCollectionOverlaps=superCollectionOverlaps)))

    @router.post('/super-collections/{superCollectionName}/users/query')
    async def query_super_collection_users(superCollectionName: str, request: QuerySuperCollectionUsersRequest) -> QuerySuperCollectionUsersResponse:
        limit = request.limit if request.limit is not None else 20
        offset = request.offset if request.offset is not None else 0
        gallerySuperCollectionUserRowListResponse = await galleryManager.query_super_collection_users(superCollectionName=superCollectionName, order=request.order, limit=limit, offset=offset)
        return QuerySuperCollectionUsersResponse(galleryUserRowListResponse=(await responseBuilder.gallery_super_collection_user_row_list_response_from_model(gallerySuperCollectionUserRowListResponse=gallerySuperCollectionUserRowListResponse)))

    return router
