import datetime
from typing import Optional

from core.api.kiba_router import KibaRouter
from core.util import date_util

from notd.api.endpoints_v1 import GetAccountTokensResponse
from notd.api.endpoints_v1 import GetCollectionRecentSalesResponse
from notd.api.endpoints_v1 import GetCollectionResponse
from notd.api.endpoints_v1 import GetCollectionTokenRecentSalesResponse
from notd.api.endpoints_v1 import GetCollectionTokenResponse
from notd.api.endpoints_v1 import ListCollectionTokensByOwnerResponse
from notd.api.endpoints_v1 import ReceiveNewBlocksDeferredResponse
from notd.api.endpoints_v1 import RefreshAccountTokenOwnershipsResponse
from notd.api.endpoints_v1 import RetrieveHighestPriceTransferRequest
from notd.api.endpoints_v1 import RetrieveHighestPriceTransferResponse
from notd.api.endpoints_v1 import RetrieveMostTradedRequest
from notd.api.endpoints_v1 import RetrieveMostTradedResponse
from notd.api.endpoints_v1 import RetrieveRandomTransferRequest
from notd.api.endpoints_v1 import RetrieveRandomTransferResponse
from notd.api.endpoints_v1 import RetrieveSponsoredTokenResponse
from notd.api.endpoints_v1 import RetrieveTransactionCountRequest
from notd.api.endpoints_v1 import RetrieveTransactionCountResponse
from notd.api.endpoints_v1 import SubscribeRequest
from notd.api.endpoints_v1 import SubscribeResponse
from notd.api.endpoints_v1 import UpdateCollectionRequest
from notd.api.endpoints_v1 import UpdateCollectionResponse
from notd.api.endpoints_v1 import UpdateCollectionTokenRequest
from notd.api.endpoints_v1 import UpdateCollectionTokenResponse
from notd.api.endpoints_v1 import UpdateCollectionTokensRequest
from notd.api.endpoints_v1 import UpdateCollectionTokensResponse
from notd.api.endpoints_v1 import datetime
from notd.api.response_builder import ResponseBuilder
from notd.manager import NotdManager


def create_api(notdManager: NotdManager, responseBuilder: ResponseBuilder) -> KibaRouter:
    router = KibaRouter()

    @router.post('/retrieve-highest-price-transfer', response_model=RetrieveHighestPriceTransferResponse)
    async def retrieve_highest_price_transfer(request: RetrieveHighestPriceTransferRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day()
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        transfer = await notdManager.retrieve_highest_priced_transfer(startDate=startDate, endDate=endDate)
        return RetrieveHighestPriceTransferResponse(transfer=(await responseBuilder.token_transfer_from_model(tokenTransfer=transfer)))

    @router.post('/retrieve-most-traded-token', response_model=RetrieveMostTradedResponse)
    async def retrieve_most_traded_token_transfer(request: RetrieveMostTradedRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day()
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        mostTradedToken = await notdManager.retrieve_most_traded_token_transfer(startDate=startDate, endDate=endDate)
        return RetrieveMostTradedResponse(tradedToken=(await responseBuilder.traded_token_from_model(tradedToken=mostTradedToken)))

    @router.post('/retrieve-random-token-transfer', response_model=RetrieveRandomTransferResponse)
    async def retrieve_random_transfer(request: RetrieveRandomTransferRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day()
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        randomTokenTransfer = await notdManager.retrieve_random_transfer(startDate=startDate, endDate=endDate)
        return RetrieveRandomTransferResponse(transfer=(await responseBuilder.token_transfer_from_model(tokenTransfer=randomTokenTransfer)))

    @router.post('/retrieve-sponsored-token', response_model=RetrieveSponsoredTokenResponse)
    async def get_sponsored_token():
        sponsoredToken = await notdManager.get_sponsored_token()
        return RetrieveSponsoredTokenResponse(sponsoredToken=(await responseBuilder.sponsored_token_from_model(sponsoredToken=sponsoredToken)))

    @router.post('/retrieve-transfer-count', response_model=RetrieveTransactionCountResponse)
    async def get_transfer_count(request: RetrieveTransactionCountRequest, startDate: Optional[datetime.datetime] = None, endDate: Optional[datetime.datetime] = None):
        startDate = request.startDate.replace(tzinfo=None) if request.startDate else date_util.start_of_day()
        endDate = request.endDate.replace(tzinfo=None) if request.endDate else date_util.start_of_day(dt=date_util.datetime_from_datetime(dt=startDate, days=1))
        count = await notdManager.get_transfer_count(startDate=startDate, endDate=endDate)
        return RetrieveTransactionCountResponse(count=count)

    @router.post('/receive-new-blocks-deferred', response_model=ReceiveNewBlocksDeferredResponse)
    async def receive_new_blocks_deferred():
        await notdManager.receive_new_blocks_deferred()
        await notdManager.reprocess_old_blocks_deferred()
        return ReceiveNewBlocksDeferredResponse()

    @router.get('/collections/{registryAddress}', response_model=GetCollectionResponse)
    async def get_collection_by_address(registryAddress: str):
        collection = await notdManager.get_collection_by_address(address=registryAddress)
        return GetCollectionResponse(collection=(await responseBuilder.collection_from_model(collection=collection)))

    @router.post('/collections/{registryAddress}/update', response_model=UpdateCollectionResponse)
    async def update_collection(registryAddress: str, request: UpdateCollectionRequest):  # pylint: disable=unused-argument
        await notdManager.update_collection_deferred(address=registryAddress)
        return UpdateCollectionResponse()

    @router.post('/collections/{registryAddress}/update-tokens', response_model=UpdateCollectionTokensResponse)
    async def update_collections_tokens(registryAddress: str, request: UpdateCollectionTokensRequest):  # pylint: disable=unused-argument
        await notdManager.update_collections_tokens_deferred(address=registryAddress)
        return UpdateCollectionTokensResponse()

    @router.get('/collections/{registryAddress}/tokens/owner/{ownerAddress}', response_model=ListCollectionTokensByOwnerResponse)
    async def list_collection_tokens_by_owner(registryAddress: str, ownerAddress: str):
        tokens = await notdManager.list_collection_tokens_by_owner(address=registryAddress, ownerAddress=ownerAddress)
        return ListCollectionTokensByOwnerResponse(tokens=(await responseBuilder.collection_token_from_registry_addresses_token_ids(tokens=tokens)))

    @router.get('/collections/{registryAddress}/recent-sales', response_model=GetCollectionRecentSalesResponse)
    async def get_collection_recent_sales(registryAddress: str, limit: Optional[int] = None, offset: Optional[int] = None):
        limit = limit if limit is not None else 20
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.get_collection_recent_sales(registryAddress=registryAddress, limit=limit, offset=offset)
        return GetCollectionRecentSalesResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.get('/collections/{registryAddress}/tokens/{tokenId}', response_model=GetCollectionTokenResponse)
    async def get_token_metadata_by_registry_address_token_id(registryAddress: str, tokenId: str):
        tokenMetadata = await notdManager.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return GetCollectionTokenResponse(token=(await responseBuilder.collection_token_from_model(tokenMetadata=tokenMetadata)))

    @router.post('/collections/{registryAddress}/tokens/{tokenId}/update', response_model=UpdateCollectionTokenResponse)
    async def update_token(registryAddress: str, request: UpdateCollectionTokenRequest):  # pylint: disable=unused-argument
        await notdManager.update_token_deferred(address=registryAddress)
        return UpdateCollectionTokenResponse()

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/recent-sales', response_model=GetCollectionTokenRecentSalesResponse)
    async def get_collection_token_recent_sales(registryAddress: str, tokenId: str, limit: Optional[int] = None, offset: Optional[int] = None):
        limit = limit if limit is not None else 20
        offset = offset if offset is not None else 0
        tokenTransfers = await notdManager.get_collection_token_recent_sales(registryAddress=registryAddress, tokenId=tokenId, limit=limit, offset=offset)
        return GetCollectionTokenRecentSalesResponse(tokenTransfers=(await responseBuilder.token_transfers_from_models(tokenTransfers=tokenTransfers)))

    @router.get('/accounts/{accountAddress}/tokens', response_model=GetAccountTokensResponse)
    async def list_account_tokens(accountAddress: str, limit: Optional[int] = None, offset: Optional[int] = None):
        limit = limit if limit is not None else 100
        offset = offset if offset is not None else 0
        tokenKeys = await notdManager.list_account_tokens(accountAddress=accountAddress, limit=limit, offset=offset)
        return GetAccountTokensResponse(tokens=(await responseBuilder.collection_tokens_from_token_keys(tokenKeys=tokenKeys)))

    @router.post('/accounts/{accountAddress}/refresh-token-ownerships', response_model=RefreshAccountTokenOwnershipsResponse)
    async def refresh_owner_token_ownerships(accountAddress: str):
        await notdManager.reprocess_owner_token_ownerships(accountAddress=accountAddress)
        return RefreshAccountTokenOwnershipsResponse()

    @router.post('/subscribe')
    async def subscribe_email(request: SubscribeRequest):
        await notdManager.subscribe_email(email=request.email)
        return SubscribeResponse()

    return router
