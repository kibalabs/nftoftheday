

import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiTokenTransfer
from notd.api.models_v1 import ApiTradedToken


class  RetrievedHighestPriceTransferRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrievedHighestPriceTransferResponse(BaseModel):
    transfer: ApiTokenTransfer

class  RetrievedRandomTransferRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrievedRandomTransferResponse(BaseModel):
    transfer: ApiTokenTransfer

class  RetrievedTransactionCountRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrievedTransactionCountResponse(BaseModel):
    count: int

class  RetrievedMostTradedRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrievedMostTradedResponse(BaseModel):
    tradedToken: ApiTradedToken

class  RetrievedSponsoredTokenRequest(BaseModel):
    pass

class RetrievedSponsoredTokenResponse(BaseModel):
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
