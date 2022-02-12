import datetime
from typing import Optional

from core.api.kiba_router import KibaRouter
from core.util import date_util

from notd.api.endpoints_v1 import GetCollectionRecentSalesResponse
from notd.api.endpoints_v1 import ReceiveNewBlocksDeferredResponse
from notd.api.endpoints_v1 import RetrieveCollectionResponse
from notd.api.endpoints_v1 import RetrieveCollectionTokenResponse
from notd.api.endpoints_v1 import RetrievedHighestPriceTransferRequest
from notd.api.endpoints_v1 import RetrievedHighestPriceTransferResponse
from notd.api.endpoints_v1 import RetrievedMostTradedRequest
from notd.api.endpoints_v1 import RetrievedMostTradedResponse
from notd.api.endpoints_v1 import RetrievedRandomTransferRequest
from notd.api.endpoints_v1 import RetrievedRandomTransferResponse
from notd.api.endpoints_v1 import RetrievedSponsoredTokenResponse
from notd.api.endpoints_v1 import RetrievedTransactionCountRequest
from notd.api.endpoints_v1 import RetrievedTransactionCountResponse
from notd.api.endpoints_v1 import SubscribeRequest
from notd.api.endpoints_v1 import SubscribeResponse
from notd.api.endpoints_v1 import datetime
from notd.api.response_builder import ResponseBuilder
from notd.manager import NotdManager


def create_api(notdManager: NotdManager, responseBuilder: ResponseBuilder) -> KibaRouter:
    router = KibaRouter()

    @router.post('/retrieve-highest-price-transfer', response_model=RetrievedHighestPriceTransferResponse)
    async def retrieve_highest_price_transfer(request: RetrievedHighestPriceTransferRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        transfer = await notdManager.retrieve_highest_priced_transfer(startDate=startDate, endDate=endDate)
        return RetrievedHighestPriceTransferResponse(transfer=(await responseBuilder.retrieve_highest_priced_transfer(transfer=transfer)))

    @router.post('/retrieve-most-traded-token-transfers', response_model=RetrievedMostTradedResponse)
    async def retrieve_most_traded_token_transfer(request: RetrievedMostTradedRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        mostTradedTokenTransfers = await notdManager.retrieve_most_traded_token_transfer(startDate=startDate, endDate=endDate)
        return RetrievedMostTradedResponse(tokenTransfers=(await responseBuilder.retrieve_most_traded_token_transfer(mostTradedTokenTransfers=mostTradedTokenTransfers)))

    @router.post('/retrieve-random-token-transfer', response_model=RetrievedRandomTransferResponse)
    async def retrieve_random_transfer(request: RetrievedRandomTransferRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        randomTokenTransfer = await notdManager.retrieve_random_transfer(startDate=startDate, endDate=endDate)
        return RetrievedRandomTransferResponse(transfer=(await responseBuilder.retrieve_random_transfer(randomTokenTransfer=randomTokenTransfer)))

    @router.get('/retrieve-sponsored-token', response_model=RetrievedSponsoredTokenResponse)
    async def get_sponsored_token():
        sponsoredToken = notdManager.get_sponsored_token()
        return RetrievedSponsoredTokenResponse(token=(await responseBuilder.retrieve_sponsored_token(sponsoredToken=sponsoredToken)))

    @router.post('/retrieve-transfer-count', response_model=RetrievedTransactionCountResponse)
    async def get_transaction_count(request: RetrievedTransactionCountRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day(dt=datetime.datetime.now())
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        count = await notdManager.get_transaction_count(startDate=startDate, endDate=endDate)
        return RetrievedTransactionCountResponse(count=count)

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
