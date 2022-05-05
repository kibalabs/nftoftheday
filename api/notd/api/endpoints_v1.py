import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionActivity
from notd.api.models_v1 import ApiCollectionStatistics
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiSponsoredToken
from notd.api.models_v1 import ApiTokenTransfer
from notd.api.models_v1 import ApiTradedToken


class  RetrieveHighestPriceTransferRequest(BaseModel):
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

class UpdateCollectionActivityRequest(BaseModel):
    pass

class UpdateCollectionActivityResponse(BaseModel):
    pass

class SubscribeRequest(BaseModel):
    email: str

class SubscribeResponse(BaseModel):
    pass

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

class ListCollectionTokensByOwnerRequest(BaseModel):
    pass

class ListCollectionTokensByOwnerResponse(BaseModel):
    tokens: List[ApiCollectionToken]

class GetCollectionRecentSalesRequest(BaseModel):
    pass

class GetCollectionRecentSalesResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]

class GetCollectionStatisticsRequest(BaseModel):
    pass

class GetCollectionStatisticsResponse(BaseModel):
    collectionStatistics: ApiCollectionStatistics

class RetrieveCollectionRequest(BaseModel):
    address: str

class GetCollectionTokenResponse(BaseModel):
    token: ApiCollectionToken

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

class GetCollectionActivityRequest(BaseModel):
    pass

class GetCollectionActivityResponse(BaseModel):
    collectionActivities: List[ApiCollectionActivity]
