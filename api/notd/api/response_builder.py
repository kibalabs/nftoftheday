
import asyncio
from typing import Sequence

from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiToken
from notd.api.models_v1 import ApiTokenTransfer
from notd.api.models_v1 import ApiTradedToken
from notd.api.models_v1 import ApiUiData
from notd.model import Collection
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.model import TradedToken
from notd.model import UiData
from notd.store.retriever import Retriever

VALID_ATTRIBUTE_FIELDS = {'trait_type', 'value'}


class ResponseBuilder:

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    async def collection_from_address(self, address: str) -> ApiCollection:
        collection = await self.retriever.get_collection_by_address(address=address)
        return await self.collection_from_model(collection=collection)

    async def collection_from_model(self, collection: Collection) -> ApiCollection:
        return ApiCollection(
            address=collection.address,
            name=collection.name,
            symbol=collection.symbol,
            description=collection.description,
            imageUrl=collection.imageUrl,
            twitterUsername=collection.twitterUsername,
            instagramUsername=collection.instagramUsername,
            wikiUrl=collection.wikiUrl,
            openseaSlug=collection.openseaSlug,
            url=collection.url,
            discordUrl=collection.discordUrl,
            bannerImageUrl=collection.bannerImageUrl
        )

    async def collection_token_from_registry_address_token_id(self, registryAddress: str, tokenId: str) -> ApiCollectionToken:
        tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return await self.collection_token_from_model(tokenMetadata=tokenMetadata)

    async def collection_token_from_model(self, tokenMetadata: TokenMetadata) -> ApiCollectionToken:
        attributes = [{key: value for (key, value) in attribute.items() if key in VALID_ATTRIBUTE_FIELDS} for attribute in tokenMetadata.attributes]
        return ApiCollectionToken(
            registryAddress=tokenMetadata.registryAddress,
            tokenId=tokenMetadata.tokenId,
            metadataUrl=tokenMetadata.metadataUrl,
            imageUrl=tokenMetadata.imageUrl,
            name=tokenMetadata.name,
            description=tokenMetadata.description,
            attributes=attributes,
        )
    async def collection_tokens_from_models(self, tokens: Sequence[TokenTransfer]) -> Sequence[TokenTransfer]:
        return await asyncio.gather(*[self.collection_from_model(TokenMetadata=token) for token in tokens])

    async def token_transfer_from_model(self, tokenTransfer: TokenTransfer) -> ApiTokenTransfer:
        return ApiTokenTransfer(
            tokenTransferId=tokenTransfer.tokenTransferId,
            transactionHash=tokenTransfer.transactionHash,
            registryAddress=tokenTransfer.registryAddress,
            fromAddress=tokenTransfer.fromAddress,
            toAddress=tokenTransfer.toAddress,
            tokenId=tokenTransfer.tokenId,
            value=tokenTransfer.value,
            gasLimit=tokenTransfer.gasLimit,
            gasPrice=tokenTransfer.gasPrice,
            gasUsed=tokenTransfer.gasUsed,
            blockNumber=tokenTransfer.blockNumber,
            blockHash=tokenTransfer.blockHash,
            blockDate=tokenTransfer.blockDate,
            collection=(await self.collection_from_address(address=tokenTransfer.registryAddress)),
            token=(await self.collection_token_from_registry_address_token_id(registryAddress=tokenTransfer.registryAddress, tokenId=tokenTransfer.tokenId)),
        )

    async def token_transfers_from_models(self, tokenTransfers: Sequence[TokenTransfer]) -> Sequence[TokenTransfer]:
        return await asyncio.gather(*[self.token_transfer_from_model(tokenTransfer=tokenTransfer) for tokenTransfer in tokenTransfers])

    async def retrieve_ui_data(self, uiData: UiData) -> ApiUiData:
        return ApiUiData(
            highestPricedTokenTransfer=(await self.token_transfer_from_model(tokenTransfer=uiData.highestPricedTokenTransfer)),
            mostTradedTokenTransfers=(await self.token_transfers_from_models(tokenTransfers=uiData.mostTradedTokenTransfers)),
            randomTokenTransfer=(await self.token_transfer_from_model(tokenTransfer=uiData.randomTokenTransfer)),
            sponsoredToken=ApiToken.from_model(model=uiData.sponsoredToken),
            transactionCount=uiData.transactionCount,
         )

    async def retrieve_most_traded_token_transfer(self, tradedToken: TradedToken) -> ApiTradedToken:
        return ApiTradedToken(
            collectionToken=await self.collection_token_from_registry_address_token_id(registryAddress=tradedToken.collectionToken.registryAddress, tokenId=tradedToken.collectionToken.tokenId),
            latestTransfer=await self.token_transfer_from_model(tokenTransfer=tradedToken.latestTransfer),
            transferCount=tradedToken.transferCount
        )
