from fastapi import APIRouter
from api.notd.api.endpoints_v1 import UpdateAttributeForAllTokensDeferredResponse

from notd.api.endpoints_v1 import ListCollectionTokenAirdropsResponse
from notd.api.response_builder import ResponseBuilder
from notd.gallery_manager import GalleryManager


def create_api(galleryManager: GalleryManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/airdrops', response_model=ListCollectionTokenAirdropsResponse)
    async def list_collection_token_airdrops(registryAddress: str, tokenId: str):
        airdrops = await galleryManager.list_collection_token_airdrops(registryAddress=registryAddress, tokenId=tokenId)
        return ListCollectionTokenAirdropsResponse(airdrops=(await responseBuilder.airdrops_from_models(airdrops=airdrops)))

    @router.post('/collections/update-activity-deferred', response_model=UpdateAttributeForAllTokensDeferredResponse)
    async def update_activity_for_all_collections_deferred():
        await galleryManager.update_activity_for_all_collections_deferred()
        return UpdateAttributeForAllTokensDeferredResponse()

    return router
