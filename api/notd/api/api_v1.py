import datetime
from typing import Optional

from fastapi import APIRouter

from notd.api.endpoints_v1 import CalculateCommonOwnersRequest
from notd.api.endpoints_v1 import CalculateCommonOwnersResponse
from notd.api.endpoints_v1 import GetAccountTokensResponse
from notd.api.endpoints_v1 import GetCollectionDailyActivitiesResponse
from notd.api.endpoints_v1 import GetCollectionRecentSalesResponse
from notd.api.endpoints_v1 import GetCollectionRecentTransfersResponse
from notd.api.endpoints_v1 import GetCollectionResponse
from notd.api.endpoints_v1 import GetCollectionStatisticsResponse
from notd.api.endpoints_v1 import GetCollectionTokenOwnershipsResponse
from notd.api.endpoints_v1 import GetCollectionTokenRecentSalesResponse
from notd.api.endpoints_v1 import GetCollectionTokenResponse
from notd.api.endpoints_v1 import GetCollectionTransferValuesResponse
from notd.api.endpoints_v1 import GetTokenRecentTransfersResponse
from notd.api.endpoints_v1 import ListAccountDelegatedTokensResponse
from notd.api.endpoints_v1 import ListAllListingsForCollectionTokenResponse
from notd.api.endpoints_v1 import ListCollectionTokensByOwnerResponse
from notd.api.endpoints_v1 import ListCollectionTokensResponse
from notd.api.endpoints_v1 import ListUserOwnedCollectionsResponse
from notd.api.endpoints_v1 import ListUserRecentTransfersResponse
from notd.api.endpoints_v1 import ReceiveNewBlocksDeferredResponse
from notd.api.endpoints_v1 import RefreshAccountTokenOwnershipsResponse
from notd.api.endpoints_v1 import RefreshCollectionOverlapsDeferredResponse
from notd.api.endpoints_v1 import RefreshGalleryBadgeHoldersForAllCollectionsDeferredResponse
from notd.api.endpoints_v1 import RefreshLatestListingsAllCollectionsDeferredResponse
from notd.api.endpoints_v1 import RetrieveHeroTokensResponse
from notd.api.endpoints_v1 import RetrieveMintedTokenCountsResponse
from notd.api.endpoints_v1 import RetrieveTrendingCollectionsResponse
from notd.api.endpoints_v1 import SubscribeRequest
from notd.api.endpoints_v1 import SubscribeResponse
from notd.api.endpoints_v1 import UpdateActivityForAllCollectionsDeferredResponse
from notd.api.endpoints_v1 import UpdateAllTwitterUsersDeferredResponse
from notd.api.endpoints_v1 import UpdateCollectionResponse
from notd.api.endpoints_v1 import UpdateCollectionTokenResponse
from notd.api.endpoints_v1 import UpdateCollectionTokensResponse
from notd.api.endpoints_v1 import UpdateLatestListingsAllCollectionsDeferredResponse
from notd.api.endpoints_v1 import UpdateStakingsForAllCollectionsDeferredResponse
from notd.api.endpoints_v1 import UpdateTokenAttributesForAllCollectionsDeferredResponse
from notd.api.endpoints_v1 import UpdateTotalActivityForAllCollectionsDeferredResponse
from notd.api.response_builder import ResponseBuilder
from notd.manager import NotdManager


def create_api(notdManager: NotdManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.post('/receive-new-blocks-deferred', response_model=ReceiveNewBlocksDeferredResponse)
    async def receive_new_blocks_deferred() -> ReceiveNewBlocksDeferredResponse:
        await notdManager.receive_new_blocks_deferred()
        await notdManager.reprocess_old_blocks_deferred()
        return ReceiveNewBlocksDeferredResponse()

    @router.post('/update-all-twitter-users-deferred')
    async def update_all_twitter_users() -> UpdateAllTwitterUsersDeferredResponse:
        await notdManager.update_all_twitter_users_deferred()
        return UpdateAllTwitterUsersDeferredResponse()

    @router.post('/refresh-views-deferred', response_model=ReceiveNewBlocksDeferredResponse)
    async def refresh_views_deferred() -> ReceiveNewBlocksDeferredResponse:
        await notdManager.refresh_views_deferred()
        return ReceiveNewBlocksDeferredResponse()

    @router.post('/collections/update-total-activity-deferred', response_model=UpdateTotalActivityForAllCollectionsDeferredResponse)
    async def update_total_activity_for_all_collections_deferred() -> UpdateTotalActivityForAllCollectionsDeferredResponse:
        await notdManager.update_total_activity_for_all_collections_deferred()
        return UpdateTotalActivityForAllCollectionsDeferredResponse()

    @router.post('/collections/update-latest-listings-deferred', response_model=UpdateLatestListingsAllCollectionsDeferredResponse)
    async def update_latest_listings_for_all_collections_deferred() -> UpdateLatestListingsAllCollectionsDeferredResponse:
        await notdManager.update_latest_listings_for_all_collections_deferred()
        return UpdateLatestListingsAllCollectionsDeferredResponse()

    @router.post('/collections/refresh-latest-listings-deferred', response_model=RefreshLatestListingsAllCollectionsDeferredResponse)
    async def refresh_latest_listings_for_all_collections_deferred() -> RefreshLatestListingsAllCollectionsDeferredResponse:
        await notdManager.refresh_latest_listings_for_all_collections_deferred()
        return RefreshLatestListingsAllCollectionsDeferredResponse()

    @router.post('/collections/update-stakings-deferred', response_model=UpdateStakingsForAllCollectionsDeferredResponse)
    async def update_token_stakings_for_all_collections_deferred() -> UpdateStakingsForAllCollectionsDeferredResponse:
        await notdManager.update_token_stakings_for_all_collections_deferred()
        return UpdateStakingsForAllCollectionsDeferredResponse()

    @router.post('/collections/update-activity-deferred', response_model=UpdateActivityForAllCollectionsDeferredResponse)
    async def update_activity_for_all_collections_deferred() -> UpdateActivityForAllCollectionsDeferredResponse:
        await notdManager.update_activity_for_all_collections_deferred()
        return UpdateActivityForAllCollectionsDeferredResponse()

    @router.post('/collections/update-token-attributes-deferred', response_model=UpdateTokenAttributesForAllCollectionsDeferredResponse)
    async def update_token_attributes_for_all_collections_deferred() -> UpdateTokenAttributesForAllCollectionsDeferredResponse:
        await notdManager.update_token_attributes_for_all_collections_deferred()
        return UpdateTokenAttributesForAllCollectionsDeferredResponse()

    @router.post('/collections/refresh-overlaps-deferred', response_model=RefreshCollectionOverlapsDeferredResponse)
    async def refresh_overlaps_for_all_collections_deferred() -> RefreshCollectionOverlapsDeferredResponse:
        await notdManager.refresh_overlaps_for_all_collections_deferred()
        return RefreshCollectionOverlapsDeferredResponse()

    @router.post('/collections/refresh-gallery-badge-holders-deferred', response_model=RefreshGalleryBadgeHoldersForAllCollectionsDeferredResponse)
    async def refresh_gallery_badge_holders_for_all_collections_deferred() -> RefreshGalleryBadgeHoldersForAllCollectionsDeferredResponse:
        await notdManager.refresh_gallery_badge_holders_for_all_collections_deferred()
        return RefreshGalleryBadgeHoldersForAllCollectionsDeferredResponse()

    @router.get('/collections/trending', response_model=RetrieveTrendingCollectionsResponse)
    async def retrieve_trending_collections(currentDate: Optional[datetime.datetime] = None, duration: Optional[str] = None, limit: Optional[int] = None, order: Optional[str] = None) -> RetrieveTrendingCollectionsResponse:
        currentDate = currentDate.replace(tzinfo=None) if currentDate else None
        trendingCollections = await notdManager.retrieve_trending_collections(currentDate=currentDate, duration=duration, limit=limit, order=order)
        return RetrieveTrendingCollectionsResponse(trendingCollections=(await responseBuilder.trending_collections_from_models(trendingCollections=trendingCollections)))

    @router.get('/collections/{registryAddress}', response_model=GetCollectionResponse)
    async def get_collection_by_address(registryAddress: str) -> GetCollectionResponse:
        collection = await notdManager.get_collection_by_address(address=registryAddress)
        return GetCollectionResponse(collection=(await responseBuilder.collection_from_model(collection=collection)))

    @router.post('/collections/{registryAddress}/update', response_model=UpdateCollectionResponse)
    async def update_collection(registryAddress: str) -> UpdateCollectionResponse:
        await notdManager.update_collection_deferred(address=registryAddress)
        return UpdateCollectionResponse()

    @router.post('/collections/{registryAddress}/update-tokens', response_model=UpdateCollectionTokensResponse)
    async def update_collection_tokens(registryAddress: str) -> UpdateCollectionTokensResponse:
        await notdManager.update_collection_tokens_deferred(address=registryAddress)
        return UpdateCollectionTokensResponse()

    @router.get('/collections/{registryAddress}/tokens', response_model=ListCollectionTokensResponse)
    async def list_collection_tokens(registryAddress: str) -> ListCollectionTokensResponse:
        tokenMetadatas = await notdManager.list_collection_tokens(address=registryAddress)
        return ListCollectionTokensResponse(tokens=(await responseBuilder.collection_tokens_from_models(tokenMetadatas=tokenMetadatas)))

    @router.get('/collections/{registryAddress}/tokens/owner/{ownerAddress}', response_model=ListCollectionTokensByOwnerResponse)
    async def list_collection_tokens_by_owner(registryAddress: str, ownerAddress: str) -> ListCollectionTokensByOwnerResponse:
        tokens = await notdManager.list_collection_tokens_by_owner(address=registryAddress, ownerAddress=ownerAddress)
        return ListCollectionTokensByOwnerResponse(tokens=(await responseBuilder.collection_token_from_registry_addresses_token_ids(tokens=tokens)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/recent-transfers', response_model=GetTokenRecentTransfersResponse)
    async def get_collection_token_recent_transfers(registryAddress: str, tokenId: str, limit: Optional[int] = None, offset: Optional[int] = None) -> GetTokenRecentTransfersResponse:
        limit = limit if limit is not None else 20
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.get_collection_token_recent_transfers(registryAddress=registryAddress, tokenId=tokenId, limit=limit, offset=offset)
        return GetTokenRecentTransfersResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/recent-sales', response_model=GetCollectionTokenRecentSalesResponse)
    async def get_collection_token_recent_sales(registryAddress: str, tokenId: str, limit: Optional[int] = None, offset: Optional[int] = None) -> GetCollectionTokenRecentSalesResponse:
        limit = limit if limit is not None else 20
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.get_collection_token_recent_sales(registryAddress=registryAddress, tokenId=tokenId, limit=limit, offset=offset)
        return GetCollectionTokenRecentSalesResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/ownerships', response_model=GetCollectionTokenOwnershipsResponse)
    async def get_collection_token_owners(registryAddress: str, tokenId: str) -> GetCollectionTokenOwnershipsResponse:
        tokenMultiOwnerships = await notdManager.get_collection_token_owners(registryAddress=registryAddress, tokenId=tokenId)
        return GetCollectionTokenOwnershipsResponse(tokenOwnerships=(await responseBuilder.token_ownerships_from_models(tokenMultiOwnerships=tokenMultiOwnerships)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/listings')
    async def list_all_listings_for_collection_token(registryAddress: str, tokenId: str) -> ListAllListingsForCollectionTokenResponse:
        tokenListings = await notdManager.list_all_listings_for_collection_token(registryAddress=registryAddress, tokenId=tokenId)
        return ListAllListingsForCollectionTokenResponse(tokenListings=(await responseBuilder.token_listings_from_models(tokenListings=tokenListings)))

    @router.get('/collections/{registryAddress}/recent-transfers', response_model=GetCollectionRecentTransfersResponse)
    async def get_collection_recent_transfers(registryAddress: str, userAddress: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> GetCollectionRecentTransfersResponse:
        limit = limit if limit is not None else 50
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.get_collection_recent_transfers(registryAddress=registryAddress, userAddress=userAddress, limit=limit, offset=offset)
        return GetCollectionRecentTransfersResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.get('/collections/{registryAddress}/token-transfer-values', response_model=GetCollectionTransferValuesResponse)
    async def get_collection_token_transfer_values(registryAddress: str, minDate: Optional[datetime.datetime] = None, maxDate: Optional[datetime.datetime] = None, minValue: Optional[int] = None) -> GetCollectionTransferValuesResponse:
        minDate = minDate.replace(tzinfo=None) if minDate else None
        maxDate = maxDate.replace(tzinfo=None) if maxDate else None
        tokenTransferValues = await notdManager.get_collection_token_transfer_values(registryAddress=registryAddress, minDate=minDate, maxDate=maxDate, minValue=minValue)
        return GetCollectionTransferValuesResponse(tokenTransferValues=(await responseBuilder.token_transfer_values_from_models(tokenTransferValues=tokenTransferValues)))

    @router.get('/collections/{registryAddress}/recent-sales', response_model=GetCollectionRecentSalesResponse)
    async def get_collection_recent_sales(registryAddress: str, limit: Optional[int] = None, offset: Optional[int] = None) -> GetCollectionRecentSalesResponse:
        limit = limit if limit is not None else 50
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.get_collection_recent_sales(registryAddress=registryAddress, limit=limit, offset=offset)
        return GetCollectionRecentSalesResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}', response_model=GetCollectionTokenResponse)
    async def get_token_metadata_by_registry_address_token_id(registryAddress: str, tokenId: str) -> GetCollectionTokenResponse:
        tokenMetadata = await notdManager.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return GetCollectionTokenResponse(token=(await responseBuilder.collection_token_from_model(tokenMetadata=tokenMetadata)))

    @router.post('/collections/{registryAddress}/tokens/{tokenId}/update', response_model=UpdateCollectionTokenResponse)
    async def update_token(registryAddress: str, tokenId: str) -> UpdateCollectionTokenResponse:
        await notdManager.update_token_deferred(registryAddress=registryAddress, tokenId=tokenId)
        return UpdateCollectionTokenResponse()

    @router.get('/collections/{registryAddress}/statistics', response_model=GetCollectionStatisticsResponse)
    async def get_collection_statistics(registryAddress: str) -> GetCollectionStatisticsResponse:
        collectionStatistics = await notdManager.get_collection_statistics(address=registryAddress)
        return GetCollectionStatisticsResponse(collectionStatistics=(await responseBuilder.get_collection_statistics(collectionStatistics=collectionStatistics)))

    @router.get('/collections/{registryAddress}/daily-activities', response_model=GetCollectionDailyActivitiesResponse)
    async def get_collection_daily_activities(registryAddress: str) -> GetCollectionDailyActivitiesResponse:
        collectionActivities = await notdManager.get_collection_daily_activities(address=registryAddress)
        return GetCollectionDailyActivitiesResponse(collectionActivities=(await responseBuilder.collection_activities_from_models(collectionActivities=collectionActivities)))

    @router.get('/accounts/{accountAddress}/tokens', response_model=GetAccountTokensResponse)
    async def list_account_tokens(accountAddress: str, limit: Optional[int] = None, offset: Optional[int] = None) -> GetAccountTokensResponse:
        limit = limit if limit is not None else 100
        offset = offset if offset is not None else 0
        tokenKeys = await notdManager.list_account_tokens(accountAddress=accountAddress, limit=limit, offset=offset)
        return GetAccountTokensResponse(tokens=(await responseBuilder.collection_tokens_from_token_keys(tokenKeys=tokenKeys)))

    @router.get('/accounts/{accountAddress}/delegated-tokens', response_model=ListAccountDelegatedTokensResponse)
    async def list_account_delegated_tokens(accountAddress: str, limit: Optional[int] = None, offset: Optional[int] = None) -> ListAccountDelegatedTokensResponse:
        limit = limit if limit is not None else 100
        offset = offset if offset is not None else 0
        accountTokenKeys = await notdManager.list_account_delegated_tokens(accountAddress=accountAddress, limit=limit, offset=offset)
        return ListAccountDelegatedTokensResponse(accountTokens=(await responseBuilder.collection_tokens_from_account_token_keys(accountTokenKeys=accountTokenKeys)))

    @router.post('/accounts/{accountAddress}/refresh-token-ownerships', response_model=RefreshAccountTokenOwnershipsResponse)
    async def refresh_owner_token_ownerships(accountAddress: str) -> RefreshAccountTokenOwnershipsResponse:
        await notdManager.reprocess_owner_token_ownerships(accountAddress=accountAddress)
        return RefreshAccountTokenOwnershipsResponse()

    @router.get('/accounts/{userAddress}/owned-collections')
    async def list_user_owned_collections(userAddress: str) -> ListUserOwnedCollectionsResponse:
        ownedCollections = await notdManager.list_user_owned_collections(userAddress=userAddress)
        return ListUserOwnedCollectionsResponse(ownedCollections=(await responseBuilder.owned_collections_from_models(ownedCollections=ownedCollections)))

    @router.get('/accounts/{userAddress}/recent-transfers', response_model=ListUserRecentTransfersResponse)
    async def list_user_recent_transfers(userAddress: str, limit: Optional[int] = None, offset: Optional[int] = None) -> ListUserRecentTransfersResponse:
        limit = limit if limit is not None else 50
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.list_user_recent_transfers(userAddress=userAddress, limit=limit, offset=offset)
        return ListUserRecentTransfersResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.post('/calculate-common-owners', response_model=CalculateCommonOwnersResponse)
    async def calculate_common_owners(request: CalculateCommonOwnersRequest) -> CalculateCommonOwnersResponse:
        date = request.date.replace(tzinfo=None) if request.date else None
        ownerAddresses = await notdManager.calculate_common_owners(registryAddresses=request.registryAddresses, tokenIds=request.tokenIds, date=date)
        return CalculateCommonOwnersResponse(ownerAddresses=ownerAddresses)

    @router.get('/minted-token-counts', response_model=RetrieveMintedTokenCountsResponse)
    async def retrieve_minted_token_counts(currentDate: Optional[datetime.datetime] = None, duration: Optional[str] = None) -> RetrieveMintedTokenCountsResponse:
        currentDate = currentDate.replace(tzinfo=None) if currentDate else None
        mintedTokenCounts = await notdManager.retrieve_minted_token_counts(currentDate=currentDate, duration=duration)
        return RetrieveMintedTokenCountsResponse(mintedTokenCounts=(await responseBuilder.minted_token_counts_from_models(mintedTokenCounts=mintedTokenCounts)))

    @router.get('/hero-tokens', response_model=RetrieveHeroTokensResponse)
    async def retrieve_hero_tokens(currentDate: Optional[datetime.datetime] = None, limit: Optional[int] = None) -> RetrieveHeroTokensResponse:
        currentDate = currentDate.replace(tzinfo=None) if currentDate else None
        tokens = await notdManager.retrieve_hero_tokens(currentDate=currentDate, limit=limit)
        return RetrieveHeroTokensResponse(tokens=(await responseBuilder.collection_tokens_from_token_keys(tokenKeys=tokens)))

    @router.post('/subscribe', response_model=SubscribeResponse)
    async def subscribe_email(request: SubscribeRequest) -> SubscribeResponse:
        await notdManager.subscribe_email(email=request.email)
        return SubscribeResponse()

    return router
