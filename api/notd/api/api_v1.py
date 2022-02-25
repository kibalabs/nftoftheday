import datetime
from typing import Optional

from core.api.kiba_router import KibaRouter
from core.util import date_util

from notd.api.endpoints_v1 import GetCollectionStatisticsResponse
from notd.api.endpoints_v1 import GetCollectionRecentSalesResponse
from notd.api.endpoints_v1 import GetCollectionResponse
from notd.api.endpoints_v1 import GetCollectionTokenRecentSalesResponse
from notd.api.endpoints_v1 import GetCollectionTokenResponse
from notd.api.endpoints_v1 import ListCollectionTokensByOwnerResponse
from notd.api.endpoints_v1 import ReceiveNewBlocksDeferredResponse
from notd.api.endpoints_v1 import RetrieveHighestPriceTransferRequest
from notd.api.endpoints_v1 import RetrieveHighestPriceTransferResponse
from notd.api.endpoints_v1 import RetrieveMostTradedRequest
from notd.api.endpoints_v1 import RetrieveMostTradedResponse
from notd.api.endpoints_v1 import RetrieveRandomTransferRequest
from notd.api.endpoints_v1 import RetrieveRandomTransferResponse
from notd.api.endpoints_v1 import RetrieveSponsoredTokenResponse
from notd.api.endpoints_v1 import RetrieveTransactionCountRequest
from notd.api.endpoints_v1 import RetrieveTransactionCountResponse
from notd.api.endpoints_v1 import RetrieveUiDataRequest
from notd.api.endpoints_v1 import RetrieveUiDataResponse
from notd.api.endpoints_v1 import SubscribeRequest
from notd.api.endpoints_v1 import SubscribeResponse
from notd.api.endpoints_v1 import datetime
from notd.api.response_builder import ResponseBuilder
from notd.manager import NotdManager


def create_api(notdManager: NotdManager, responseBuilder: ResponseBuilder) -> KibaRouter:
    router = KibaRouter()

    @router.post('/retrieve-ui-data', response_model=RetrieveUiDataResponse)
    async def retrieve_ui_data(request: RetrieveUiDataRequest):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        uiData = await notdManager.retrieve_ui_data(startDate=startDate, endDate=endDate)
        return RetrieveUiDataResponse(uiData=(await responseBuilder.retrieve_ui_data(uiData=uiData)))

    @router.post('/retrieve-highest-price-transfer', response_model=RetrieveHighestPriceTransferResponse)
    async def retrieve_highest_price_transfer(request: RetrieveHighestPriceTransferRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        transfer = await notdManager.retrieve_highest_priced_transfer(startDate=startDate, endDate=endDate)
        return RetrieveHighestPriceTransferResponse(transfer=(await responseBuilder.token_transfer_from_model(tokenTransfer=transfer)))

    @router.post('/retrieve-most-traded-token-transfers', response_model=RetrieveMostTradedResponse)
    async def retrieve_most_traded_token_transfer(request: RetrieveMostTradedRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        mostTradedToken = await notdManager.retrieve_most_traded_token_transfer(startDate=startDate, endDate=endDate)
        return RetrieveMostTradedResponse(tradedToken=(await responseBuilder.retrieve_most_traded_token_transfer(tradedToken=mostTradedToken)))

    @router.post('/retrieve-random-token-transfer', response_model=RetrieveRandomTransferResponse)
    async def retrieve_random_transfer(request: RetrieveRandomTransferRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        randomTokenTransfer = await notdManager.retrieve_random_transfer(startDate=startDate, endDate=endDate)
        return RetrieveRandomTransferResponse(transfer=(await responseBuilder.token_transfer_from_model(tokenTransfer=randomTokenTransfer)))

    @router.post('/retrieve-sponsored-token', response_model=RetrieveSponsoredTokenResponse)
    async def get_sponsored_token():
        sponsoredToken = notdManager.get_sponsored_token()
        return RetrieveSponsoredTokenResponse(token=(await responseBuilder.collection_token_from_registry_address_token_id(registryAddress=sponsoredToken.registryAddress, tokenId=sponsoredToken.tokenId)))

    @router.post('/retrieve-transfer-count', response_model=RetrieveTransactionCountResponse)
    async def get_transfer_count(request: RetrieveTransactionCountRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        count = await notdManager.get_transfer_count(startDate=startDate, endDate=endDate)
        return RetrieveTransactionCountResponse(count=count)

    @router.post('/receive-new-blocks-deferred', response_model=ReceiveNewBlocksDeferredResponse)
    async def receive_new_blocks_deferred():
        await notdManager.receive_new_blocks_deferred()
        await notdManager.reprocess_old_blocks_deferred()
        return ReceiveNewBlocksDeferredResponse()

    @router.get('/collections/{registryAddress}', response_model=GetCollectionResponse)
    async def get_collection_by_address(registryAddress: str):  # request: RetreiveCollectionRequest
        collection = await notdManager.get_collection_by_address(address=registryAddress)
        return GetCollectionResponse(collection=(await responseBuilder.collection_from_model(collection=collection)))

    @router.get('/collections/{registryAddress}/tokens/owner/{ownerAddress}', response_model=ListCollectionTokensByOwnerResponse)
    async def list_collection_tokens_by_owner(registryAddress: str, ownerAddress: str):  # request: ListHoldingsForCollectionRequest
        tokens = await notdManager.list_collection_tokens_by_owner(address=registryAddress, ownerAddress=ownerAddress)
        return ListCollectionTokensByOwnerResponse(tokens=(await responseBuilder.collection_token_from_registry_addresses_token_ids(tokens=tokens)))

    @router.get('/collections/{registryAddress}/recent-sales', response_model=GetCollectionRecentSalesResponse)
    async def get_collection_recent_sales(registryAddress: str, limit: Optional[int] = None, offset: Optional[int] = None):
        limit = limit if limit is not None else 10
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.get_collection_recent_sales(registryAddress=registryAddress, limit=limit, offset=offset)
        return GetCollectionRecentSalesResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.get('/collections/{registryAddress}/statistics', response_model=GetCollectionStatisticsResponse)
    async def get_collection_statistics(registryAddress: str):  # request: GetCollectionStatisticsRequest
        collectionStatistics = await notdManager.get_collection_statistics(address=registryAddress)
        return GetCollectionStatisticsResponse(collectionStatistics=(await responseBuilder.get_collection_statistics(collectionStatistics=collectionStatistics)))

    @router.post('/subscribe')
    async def subscribe_email(request: SubscribeRequest):
        await notdManager.subscribe_email(email=request.email)
        return SubscribeResponse()

    return router
