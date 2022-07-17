import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel

from notd.api.models_v1 import ApiAirdrop
from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionAttribute
from notd.api.models_v1 import ApiCollectionDailyActivity
from notd.api.models_v1 import ApiCollectionStatistics
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiSponsoredToken
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

class UpdateLatestListingsAllCollectionsDeferredRequest(BaseModel):
    pass

class UpdateLatestListingsAllCollectionsDeferredResponse(BaseModel):
    pass

class UpdateActivityForAllCollectionsDeferredRequest(BaseModel):
    pass

class UpdateActivityForAllCollectionsDeferredResponse(BaseModel):
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

class GetAccountTokensRequest(BaseModel):
    pass

class GetAccountTokensResponse(BaseModel):
    tokens: List[ApiCollectionToken]

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

class GetCollectionTokensRequest(BaseModel):
    limit: Optional[int]
    offset: Optional[int]
    minPrice: Optional[int]
    maxPrice: Optional[int]
    isListed: Optional[bool]
    tokenIdIn: Optional[List[str]]
    attributeFilters: Optional[List[InQueryParam]]

class GetCollectionTokensResponse(BaseModel):
    tokens: List[ApiCollectionToken]
