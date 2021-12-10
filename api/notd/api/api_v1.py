import datetime
from typing import Optional

from core.api.kiba_router import KibaRouter
from core.util import date_util

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiMetadataToken
from notd.api.models_v1 import ApiRegistryToken
from notd.api.models_v1 import ApiUiData
from notd.api.models_v1 import ReceiveNewBlocksDeferredResponse
from notd.api.models_v1 import RetrieveRegistryTokenResponse
from notd.api.models_v1 import RetrieveCollectionResponse
from notd.api.models_v1 import RetrieveTokenMetadataResponse
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

    @router.get('/registries/{registryAddress}/tokens/{tokenId}', response_model=RetrieveRegistryTokenResponse)
    async def retrieve_registry_token(registryAddress: str, tokenId: str):  # request: RetrieveRegistryTokenRequest
        registryToken = await notdManager.retrieve_registry_token(registryAddress=registryAddress, tokenId=tokenId)
        return RetrieveRegistryTokenResponse(registryToken=ApiRegistryToken.from_model(model=registryToken))

    @router.get('/contract/{registryAddress}/tokens/{tokenId}', response_model=RetrieveTokenMetadataResponse)
    async def retrieve_token_metadata(registryAddress: str, tokenId: str):  # request: RetrieveRegistryTokenRequest
        retrievedTokenMetadata = await notdManager.retrieve_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
        return RetrieveTokenMetadataResponse(retrievedTokenMetadata=ApiMetadataToken.from_model(model=retrievedTokenMetadata))

    @router.get('/collections/{address}', response_model=RetrieveCollectionResponse)
    async def retrieve_collection(address: str):  # request: retrieveCollectionRequest
        retrievedCollection = await notdManager.retrieve_collection(address=address)
        return RetrieveCollectionResponse(retrievedCollection=ApiCollection.from_model(model=retrievedCollection))

    @router.post('/subscribe')
    async def create_newsletter_subscription(request: SubscribeRequest):
        email = request.email.lower()
        await notdManager.subscribe_email(email=email)
        return SubscribeResponse()

    return router
