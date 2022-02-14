

import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiTokenTransfer
from notd.api.models_v1 import ApiTradedToken
from notd.api.models_v1 import ApiUiData


class RetrieveUiDataRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveUiDataResponse(BaseModel):
    uiData: ApiUiData

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
    token: ApiCollectionToken

class ReceiveNewBlocksDeferredRequest(BaseModel):
    pass

class ReceiveNewBlocksDeferredResponse(BaseModel):
    pass

class SubscribeRequest(BaseModel):
    email: str

class SubscribeResponse(BaseModel):
    pass

class GetCollectionRequest(BaseModel):
    address: str

class GetCollectionResponse(BaseModel):
    collection: ApiCollection

class GetHoldingRequest(BaseModel):
    registryAddress: str
    ownerAddress: str

class GetHoldingResponse(BaseModel):
    tokens: List[ApiCollectionToken]

class GetCollectionRecentSalesRequest(BaseModel):
    pass

class GetCollectionRecentSalesResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]

class GetCollectionTokenRequest(BaseModel):
    pass

class GetCollectionTokenResponse(BaseModel):
    token: ApiCollectionToken

class GetCollectionTokenRecentSalesRequest(BaseModel):
    pass

class GetCollectionTokenRecentSalesResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]
