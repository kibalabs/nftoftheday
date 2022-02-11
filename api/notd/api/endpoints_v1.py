

import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from notd.api.models_v1 import ApiCollectionStatistics

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiTokenTransfer
from notd.api.models_v1 import ApiUiData


class RetrieveUiDataRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveUiDataResponse(BaseModel):
    uiData: ApiUiData

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

class GetCollectionStatisticsRequest(BaseModel):
    pass

class GetCollectionStatisticsResponse(BaseModel):
    collectionStatistics: ApiCollectionStatistics

class RetrieveCollectionRequest(BaseModel):
    address: str

class RetrieveCollectionResponse(BaseModel):
    collection: ApiCollection
