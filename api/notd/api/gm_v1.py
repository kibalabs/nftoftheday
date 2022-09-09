from fastapi import APIRouter

from notd.api.endpoints_v1 import CreateGmRequest
from notd.api.endpoints_v1 import CreateGmResponse
from notd.api.endpoints_v1 import ListGmAccountRowsResponse
from notd.api.endpoints_v1 import ListGmCollectionRowsResponse
from notd.api.response_builder import ResponseBuilder
from notd.gm_manager import GmManager


def create_api(gmManager: GmManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.post('/gm', response_model=CreateGmResponse)
    async def create_gm(request: CreateGmRequest) -> CreateGmResponse:
        await gmManager.create_gm(account=request.account, signatureMessage=request.signatureMessage, signature=request.signature)
        return CreateGmResponse()

    @router.get('/account-rows', response_model=ListGmAccountRowsResponse)
    async def list_gm_account_rows() -> ListGmAccountRowsResponse:
        gmAccountRows = await gmManager.list_gm_account_rows()
        return ListGmAccountRowsResponse(accountRows=(await responseBuilder.gm_account_rows_from_models(gmAccountRows=gmAccountRows)))

    @router.get('/collection-rows', response_model=ListGmCollectionRowsResponse)
    async def list_gm_collection_rows() -> ListGmCollectionRowsResponse:
        gmCollectionRows = await gmManager.list_gm_collection_rows()
        return ListGmCollectionRowsResponse(collectionRows=(await responseBuilder.gm_collection_rows_from_models(gmCollectionRows=gmCollectionRows)))

    return router
