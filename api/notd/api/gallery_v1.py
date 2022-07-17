import re
from typing import Dict, List, Optional

from fastapi import APIRouter
from fastapi import Request
from pydantic import BaseModel
import pydantic

from notd.api.endpoints_v1 import GetCollectionAttributesResponse, GetCollectionTokensRequest
from notd.api.endpoints_v1 import GetCollectionTokenRecentSalesResponse
from notd.api.endpoints_v1 import GetCollectionTokensResponse
from notd.api.endpoints_v1 import ListCollectionTokenAirdropsResponse
from notd.api.response_builder import ResponseBuilder
from notd.gallery_manager import GalleryManager
from notd.model import QueryParam


def create_api(galleryManager: GalleryManager, responseBuilder: ResponseBuilder) -> APIRouter:
    router = APIRouter()

    @router.get('/collections/{registryAddress}/tokens/{tokenId}/airdrops', response_model=ListCollectionTokenAirdropsResponse)
    async def list_collection_token_airdrops(registryAddress: str, tokenId: str):
        airdrops = await galleryManager.list_collection_token_airdrops(registryAddress=registryAddress, tokenId=tokenId)
        return ListCollectionTokenAirdropsResponse(airdrops=(await responseBuilder.airdrops_from_models(airdrops=airdrops)))

    @router.get('/collections/{registryAddress}/attributes', response_model=GetCollectionAttributesResponse)
    async def get_collection_attributes(registryAddress: str):
        collectionAttributes = await galleryManager.get_collection_attributes(registryAddress=registryAddress)
        return GetCollectionAttributesResponse(attributes=(await responseBuilder.collection_attributes_from_models(collectionAttributes=collectionAttributes)))

    def process_query_params(queryParts: Dict[str, str]) -> QueryParam:
        queryParams = []
        for name, value in queryParts.items():
            match = re.compile('([A-Z]+)\[(.*)\]').match(value)
            if match:
                print(match)
                queryParams.append(QueryParam(fieldName=name, operator=match.group(1), value=match.group(2)))
            else:
                queryParams.append(QueryParam(fieldName=name, operator='EQ', value=value))
        return queryParams

    # TODO(krishan711): make this a GET request once we understand complex query params
    @router.post('/collections/{registryAddress}/tokens')
    async def get_collection_tokens(registryAddress: str, request: GetCollectionTokensRequest) -> GetCollectionTokensResponse:
        limit = request.limit if request.limit is not None else 20
        offset = request.offset if request.offset is not None else 0
        tokenMetadatas = await galleryManager.get_collection_tokens(registryAddress=registryAddress, minPrice=request.minPrice, maxPrice=request.maxPrice, isListed=request.isListed, tokenIdIn=request.tokenIdIn, attributeFilters=request.attributeFilters, limit=limit, offset=offset)
        return GetCollectionTokensResponse(tokens=(await responseBuilder.collection_tokens_from_models(tokenMetadatas=tokenMetadatas)))
    return router
