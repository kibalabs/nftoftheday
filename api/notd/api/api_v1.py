import datetime
from typing import Optional

from core.api.kiba_router import KibaRouter
from core.util import date_util

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionStatistics
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiUiData
from notd.api.models_v1 import ReceiveNewBlocksDeferredResponse
from notd.api.models_v1 import RetrieveCollectionResponse
from notd.api.models_v1 import RetrieveCollectionStatisticsResponse
from notd.api.models_v1 import RetrieveCollectionTokenResponse
from notd.api.models_v1 import RetrieveUiDataRequest
from notd.api.models_v1 import RetrieveUiDataResponse
from notd.api.models_v1 import SubscribeRequest
from notd.api.models_v1 import SubscribeResponse
from notd.api.models_v1 import datetime
from notd.manager import NotdManager


def create_api(notdManager: NotdManager) -> KibaRouter:
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
        return RetrieveCollectionResponse(collection=ApiCollection.from_model(model=collection))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}', response_model=RetrieveCollectionTokenResponse)
    async def retrieve_collection_token(registryAddress: str, tokenId: str):  # request: RetreiveRegistryTokenRequest
        token = await notdManager.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return RetrieveCollectionTokenResponse(token=ApiCollectionToken.from_model(model=token))

    @router.get('/collections/{registryAddress}/statistics', response_model=RetrieveCollectionStatisticsResponse)
    async def get_collection_statistics(registryAddress: str):  # request: GetCollectionStatisticsRequest
        collectionStatistics = await notdManager.get_collection_statistics(address=registryAddress)
        return RetrieveCollectionStatisticsResponse(collectionStatistics=ApiCollectionStatistics.from_model(model=collectionStatistics))

    @router.post('/subscribe')
    async def create_newsletter_subscription(request: SubscribeRequest):
        email = request.email.lower()
        await notdManager.subscribe_email(email=email)
        return SubscribeResponse()

    return router
