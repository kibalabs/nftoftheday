import datetime
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from notd.api.models_v1 import ApiAccountCollectionToken
from notd.api.models_v1 import ApiAccountGm
from notd.api.models_v1 import ApiAirdrop
from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionAttribute
from notd.api.models_v1 import ApiCollectionDailyActivity
from notd.api.models_v1 import ApiCollectionOverlap
from notd.api.models_v1 import ApiCollectionOverlapOwner
from notd.api.models_v1 import ApiCollectionOverlapSummary
from notd.api.models_v1 import ApiCollectionStatistics
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiGalleryOwnedCollection
from notd.api.models_v1 import ApiGalleryToken
from notd.api.models_v1 import ApiGalleryUser
from notd.api.models_v1 import ApiGalleryUserBadge
from notd.api.models_v1 import ApiGalleryUserRow
from notd.api.models_v1 import ApiGmAccountRow
from notd.api.models_v1 import ApiGmCollectionRow
from notd.api.models_v1 import ApiLatestAccountGm
from notd.api.models_v1 import ApiSponsoredToken
from notd.api.models_v1 import ApiTokenCustomization
from notd.api.models_v1 import ApiTokenListing
from notd.api.models_v1 import ApiTokenOwnership
from notd.api.models_v1 import ApiTokenTransfer
from notd.api.models_v1 import ApiTradedToken


class RetrieveHighestPriceTransferRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveHighestPriceTransferResponse(BaseModel):
    transfer: ApiTokenTransfer

class  RetrieveRandomTransferRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveRandomTransferResponse(BaseModel):
    transfer: ApiTokenTransfer

class  RetrieveTransactionCountRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveTransactionCountResponse(BaseModel):
    count: int

class  RetrieveMostTradedRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveMostTradedResponse(BaseModel):
    tradedToken: ApiTradedToken

class  RetrieveSponsoredTokenRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveSponsoredTokenResponse(BaseModel):
    sponsoredToken: ApiSponsoredToken

class ReceiveNewBlocksDeferredRequest(BaseModel):
    pass

class ReceiveNewBlocksDeferredResponse(BaseModel):
    pass

class RefreshViewsDeferredRequest(BaseModel):
    pass

class RefreshViewsDeferredResponse(BaseModel):
    pass

class RefreshCollectionOverlapsDeferredResponse(BaseModel):
    pass

class RefreshCollectionOverlapsDeferredRequest(BaseModel):
    pass

class UpdateLatestListingsAllCollectionsDeferredRequest(BaseModel):
    pass

class UpdateLatestListingsAllCollectionsDeferredResponse(BaseModel):
    pass

class RefreshLatestListingsAllCollectionsDeferredRequest(BaseModel):
    pass

class RefreshLatestListingsAllCollectionsDeferredResponse(BaseModel):
    pass

class UpdateActivityForAllCollectionsDeferredRequest(BaseModel):
    pass

class UpdateActivityForAllCollectionsDeferredResponse(BaseModel):
    pass

class UpdateTotalActivityForAllCollectionsDeferredRequest(BaseModel):
    pass

class UpdateTotalActivityForAllCollectionsDeferredResponse(BaseModel):
    pass

class SubscribeRequest(BaseModel):
    email: str

class SubscribeResponse(BaseModel):
    pass

class GetTokenRecentTransfersRequest(BaseModel):
    pass

class GetTokenRecentTransfersResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]

class GetCollectionRequest(BaseModel):
    address: str

class GetCollectionResponse(BaseModel):
    collection: ApiCollection

class UpdateCollectionRequest(BaseModel):
    userAddress: str

class UpdateCollectionResponse(BaseModel):
    pass

class UpdateCollectionTokensRequest(BaseModel):
    userAddress: str

class UpdateCollectionTokensResponse(BaseModel):
    pass

class ListCollectionTokensRequest(BaseModel):
    pass

class ListCollectionTokensResponse(BaseModel):
    tokens: List[ApiCollectionToken]

class ListCollectionTokensByOwnerRequest(BaseModel):
    pass

class ListCollectionTokensByOwnerResponse(BaseModel):
    tokens: List[ApiCollectionToken]

class GetCollectionRecentSalesRequest(BaseModel):
    pass

class GetCollectionRecentSalesResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]

class GetCollectionRecentTransfersRequest(BaseModel):
    pass

class GetCollectionRecentTransfersResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]

class GetCollectionTokenRequest(BaseModel):
    pass

class GetCollectionTokenResponse(BaseModel):
    token: ApiCollectionToken

class GetCollectionStatisticsRequest(BaseModel):
    pass

class GetCollectionStatisticsResponse(BaseModel):
    collectionStatistics: ApiCollectionStatistics

class UpdateCollectionTokenRequest(BaseModel):
    userAddress: str

class UpdateCollectionTokenResponse(BaseModel):
    pass

class GetCollectionTokenRecentSalesRequest(BaseModel):
    pass

class GetCollectionTokenRecentSalesResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]

class GetCollectionTokenOwnershipsRequest(BaseModel):
    pass

class GetCollectionTokenOwnershipsResponse(BaseModel):
    tokenOwnerships: List[ApiTokenOwnership]

class GetAccountTokensRequest(BaseModel):
    pass

class GetAccountTokensResponse(BaseModel):
    tokens: List[ApiCollectionToken]

class ListAccountDelegatedTokensRequest(BaseModel):
    pass

class ListAccountDelegatedTokensResponse(BaseModel):
    accountTokens: List[ApiAccountCollectionToken]

class RefreshAccountTokenOwnershipsRequest(BaseModel):
    pass

class RefreshAccountTokenOwnershipsResponse(BaseModel):
    pass

class GetCollectionDailyActivitiesRequest(BaseModel):
    pass

class GetCollectionDailyActivitiesResponse(BaseModel):
    collectionActivities: List[ApiCollectionDailyActivity]

class SubmitTreasureHuntForCollectionTokenRequest(BaseModel):
    userAddress: str
    signature: str

class SubmitTreasureHuntForCollectionTokenResponse(BaseModel):
    pass

class ListCollectionTokenAirdropsRequest(BaseModel):
    pass

class ListCollectionTokenAirdropsResponse(BaseModel):
    airdrops: List[ApiAirdrop]

class UpdateTokenAttributesForAllCollectionsDeferredRequest(BaseModel):
    pass

class UpdateTokenAttributesForAllCollectionsDeferredResponse(BaseModel):
    pass

class GetCollectionAttributesRequest(BaseModel):
    pass

class GetCollectionAttributesResponse(BaseModel):
    attributes: List[ApiCollectionAttribute]

class InQueryParam(BaseModel):
    fieldName: str
    values: List[str]

class QueryCollectionTokensRequest(BaseModel):
    limit: Optional[int]
    offset: Optional[int]
    minPrice: Optional[int]
    maxPrice: Optional[int]
    isListed: Optional[bool]
    tokenIdIn: Optional[List[str]]
    attributeFilters: Optional[List[InQueryParam]]
    ownerAddress: Optional[str]
    order: Optional[str]

class QueryCollectionTokensResponse(BaseModel):
    galleryTokens: List[ApiGalleryToken]

class CreateCustomizationForCollectionTokenRequest(BaseModel):
    creatorAddress: str
    signature: str
    blockNumber: int
    name: Optional[str]
    description: Optional[str]

class CreateCustomizationForCollectionTokenResponse(BaseModel):
    tokenCustomization: ApiTokenCustomization

class GetGalleryTokenRequest(BaseModel):
    pass

class GetGalleryTokenResponse(BaseModel):
    galleryToken: ApiGalleryToken

class TwitterLoginRequest(BaseModel):
    pass

class TwitterLoginResponse(BaseModel):
    pass

class TwitterLoginCallbackRequest(BaseModel):
    pass

class TwitterLoginCallbackResponse(BaseModel):
    pass

class GetGalleryCollectionUserRequest(BaseModel):
    pass

class GetGalleryCollectionUserResponse(BaseModel):
    galleryUser: ApiGalleryUser

class ListGalleryUserBadgeRequest(BaseModel):
    pass

class ListGalleryUserBadgesResponse(BaseModel):
    galleryUserBadges: List[ApiGalleryUserBadge]

class FollowCollectionUserRequest(BaseModel):
    account: str
    signatureMessage: str
    signature: str

class FollowCollectionUserResponse(BaseModel):
    pass

class GetGalleryUserOwnedCollectionsRequest(BaseModel):
    pass

class GetGalleryUserOwnedCollectionsResponse(BaseModel):
    ownedCollections: List[ApiGalleryOwnedCollection]

ApiListResponseItemType = TypeVar("ApiListResponseItemType")  # pylint: disable=invalid-name

class ApiListResponse(GenericModel, Generic[ApiListResponseItemType]):
    items: List[ApiListResponseItemType]
    totalCount: int

class QueryCollectionUsersRequest(BaseModel):
    order: Optional[str]
    limit: Optional[int]
    offset: Optional[int]

class QueryCollectionUsersResponse(BaseModel):
    galleryUserRowListResponse: ApiListResponse[ApiGalleryUserRow]

class UpdateAllTwitterUsersDeferredRequest(BaseModel):
    pass

class UpdateAllTwitterUsersDeferredResponse(BaseModel):
    pass

class CreateGmRequest(BaseModel):
    account: str
    signatureMessage: str
    signature: str

class CreateGmResponse(BaseModel):
    accountGm: ApiAccountGm

class CreateAnonymousGmRequest(BaseModel):
    pass

class CreateAnonymousGmResponse(BaseModel):
    pass

class ListGmAccountRowsRequest(BaseModel):
    pass

class ListGmAccountRowsResponse(BaseModel):
    accountRows: List[ApiGmAccountRow]

class ListGmCollectionRowsRequest(BaseModel):
    pass

class ListGmCollectionRowsResponse(BaseModel):
    collectionRows: List[ApiGmCollectionRow]

class GetLatestGmForAccountRequest(BaseModel):
    pass

class GetLatestGmForAccountResponse(BaseModel):
    latestAccountGm: ApiLatestAccountGm

class ListGalleryCollectionOverlapsRequest(BaseModel):
    pass

class ListGalleryCollectionOverlapsResponse(BaseModel):
    collectionOverlaps: List[ApiCollectionOverlap]

class ListGalleryCollectionOverlapSummariesRequest(BaseModel):
    pass

class ListGalleryCollectionOverlapSummariesResponse(BaseModel):
    collectionOverlapSummaries: List[ApiCollectionOverlapSummary]

class ListGalleryCollectionOverlapOwnersRequest(BaseModel):
    pass

class ListGalleryCollectionOverlapOwnersResponse(BaseModel):
    collectionOverlapOwners: List[ApiCollectionOverlapOwner]

class ListAllListingsForCollectionTokenRequest(BaseModel):
    pass

class ListAllListingsForCollectionTokenResponse(BaseModel):
    tokenListings: List[ApiTokenListing]

class RefreshGalleryBadgeHoldersForAllCollectionsDeferredRequest(BaseModel):
    pass

class RefreshGalleryBadgeHoldersForAllCollectionsDeferredResponse(BaseModel):
    pass

class CollectionAssignBadgeRequest(BaseModel):
    badgeKey: str
    achievedDate: datetime.datetime
    assignerAddress: str
    signature: str

class CollectionAssignBadgeResponse(BaseModel):
    pass

class CalculateCommonOwnersRequest(BaseModel):
    registryAddresses: List[str]
    tokenIds: List[str]
    date: Optional[datetime.datetime]

class CalculateCommonOwnersResponse(BaseModel):
    ownerAddresses: List[str]

class UpdateStakingsForAllCollectionsDeferredRequest(BaseModel):
    pass

class UpdateStakingsForAllCollectionsDeferredResponse(BaseModel):
    pass
