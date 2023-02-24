from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import StreamingResponse

from notd.api.endpoints_v1 import CreateAnonymousGmResponse
from notd.api.endpoints_v1 import CreateGmRequest
from notd.api.endpoints_v1 import CreateGmResponse
from notd.api.endpoints_v1 import GetLatestGmForAccountResponse
from notd.api.endpoints_v1 import ListGmAccountRowsResponse
from notd.api.endpoints_v1 import ListGmCollectionRowsResponse
from notd.api.response_builder import ResponseBuilder
from notd.gm_manager import GmManager


def create_api(gmManager: GmManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.post('/gm', response_model=CreateGmResponse)
    async def create_gm(request: CreateGmRequest) -> CreateGmResponse:
        accountGm = await gmManager.create_gm(account=request.account, signatureMessage=request.signatureMessage, signature=request.signature)
        return CreateGmResponse(accountGm=(await responseBuilder.account_gm_from_model(accountGm=accountGm)))

    @router.post('/anonymous-gm', response_model=CreateAnonymousGmResponse)
    async def create_anonymous_gm() -> CreateAnonymousGmResponse:
        await gmManager.create_anonymous_gm()
        return CreateAnonymousGmResponse()

    @router.get('/account-rows', response_model=ListGmAccountRowsResponse)
    async def list_gm_account_rows() -> ListGmAccountRowsResponse:
        gmAccountRows = await gmManager.list_gm_account_rows()
        return ListGmAccountRowsResponse(accountRows=(await responseBuilder.gm_account_rows_from_models(gmAccountRows=gmAccountRows)))

    @router.get('/collection-rows', response_model=ListGmCollectionRowsResponse)
    async def list_gm_collection_rows() -> ListGmCollectionRowsResponse:
        gmCollectionRows = await gmManager.list_gm_collection_rows()
        return ListGmCollectionRowsResponse(collectionRows=(await responseBuilder.gm_collection_rows_from_models(gmCollectionRows=gmCollectionRows)))

    @router.route('/generate-gms')
    async def sse(rawRequest: Request) -> StreamingResponse:  # pylint: disable=unused-argument
        sseHeaders = {
            'Content-type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
        # TODO(krishan711): gmManager shouldn't be dealing with the structure of the response
        return StreamingResponse(gmManager.generate_gms(), headers=sseHeaders)

    @router.get('/accounts/{address}/latest-gm')
    async def get_latest_gm_for_account(address: str) -> GetLatestGmForAccountResponse:
        latestAccountGm = await gmManager.get_latest_gm_for_account(address=address)
        return GetLatestGmForAccountResponse(latestAccountGm=(await responseBuilder.latest_account_gm_from_model(latestAccountGm=latestAccountGm)))

    return router
