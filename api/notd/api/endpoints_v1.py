

import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiTokenTransfer


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
    tokenTransfers: List[ApiTokenTransfer]

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

class RetrieveCollectionTokenRequest(BaseModel):
    pass

class RetrieveCollectionTokenResponse(BaseModel):
    token: ApiCollectionToken

class GetCollectionRecentSalesRequest(BaseModel):
    pass

class GetCollectionRecentSalesResponse(BaseModel):
    tokenTransfers: List[ApiTokenTransfer]

class RetrieveCollectionRequest(BaseModel):
    address: str

class RetrieveCollectionResponse(BaseModel):
    collection: ApiCollection
