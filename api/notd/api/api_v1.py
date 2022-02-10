import datetime
from typing import Optional

from core.api.kiba_router import KibaRouter
from core.util import date_util

from notd.api.endpoints_v1 import GetCollectionRecentSalesResponse
from notd.api.endpoints_v1 import ReceiveNewBlocksDeferredResponse
from notd.api.endpoints_v1 import RetrieveCollectionResponse
from notd.api.endpoints_v1 import RetrieveCollectionTokenResponse
from notd.api.endpoints_v1 import RetrieveUiDataRequest
from notd.api.endpoints_v1 import RetrieveUiDataResponse
from notd.api.endpoints_v1 import SubscribeRequest
from notd.api.endpoints_v1 import SubscribeResponse
from notd.api.endpoints_v1 import datetime
from notd.api.models_v1 import ApiUiData
from notd.api.response_builder import ResponseBuilder
from notd.manager import NotdManager


def create_api(notdManager: NotdManager, responseBuilder: ResponseBuilder) -> KibaRouter:
    router = KibaRouter()

    @router.post('/retrieve-ui-data', response_model=RetrieveUiDataResponse)
    async def retrieve_ui_data(request: RetrieveUiDataRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        uiData = await notdManager.retrieve_ui_data(startDate=startDate, endDate=endDate)
        return RetrieveUiDataResponse(uiData=ApiUiData.from_model(model=uiData))

    @router.post('/receive-new-blocks-deferred', response_model=ReceiveNewBlocksDeferredResponse)
    async def receive_new_blocks_deferred():  # request: ReceiveNewBlocksDeferredRequest
        await notdManager.receive_new_blocks_deferred()
        return ReceiveNewBlocksDeferredResponse()

    @router.get('/collections/{registryAddress}', response_model=RetrieveCollectionResponse)
    async def get_collection_by_address(registryAddress: str):  # request: RetreiveCollectionRequest
        collection = await notdManager.get_collection_by_address(address=registryAddress)
        return RetrieveCollectionResponse(collection=(await responseBuilder.collection_from_model(collection=collection)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}', response_model=RetrieveCollectionTokenResponse)
    async def retrieve_collection_token(registryAddress: str, tokenId: str):  # request: RetreiveCollectionTokenResponse
        tokenMetadata = await notdManager.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return RetrieveCollectionTokenResponse(token=(await responseBuilder.collection_token_from_model(tokenMetadata=tokenMetadata)))

    @router.get('/collections/{registryAddress}/recent-sales', response_model=GetCollectionRecentSalesResponse)
    async def get_collection_recent_sales(registryAddress: str):  # request: GetCollectionRecentSalesRequest
        tokenTransfers = await notdManager.get_collection_recent_sales(registryAddress=registryAddress)
        return GetCollectionRecentSalesResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.post('/subscribe')
    async def subscribe_email(request: SubscribeRequest):
        await notdManager.subscribe_email(email=request.email)
        return SubscribeResponse()

    return router
