
import asyncio
from typing import List
from typing import Sequence

from core.exceptions import NotFoundException

from notd.api.models_v1 import ApiAirdrop
from notd.api.models_v1 import ApiCollection
from notd.api.models_v1 import ApiCollectionAttribute
from notd.api.models_v1 import ApiCollectionDailyActivity
from notd.api.models_v1 import ApiCollectionStatistics
from notd.api.models_v1 import ApiCollectionToken
from notd.api.models_v1 import ApiGalleryToken
from notd.api.models_v1 import ApiSponsoredToken
from notd.api.models_v1 import ApiTokenCustomization
from notd.api.models_v1 import ApiTokenListing
from notd.api.models_v1 import ApiTokenTransfer
from notd.api.models_v1 import ApiTradedToken
from notd.model import Airdrop
from notd.model import Collection
from notd.model import CollectionAttribute
from notd.model import CollectionDailyActivity
from notd.model import CollectionStatistics
from notd.model import GalleryToken
from notd.model import SponsoredToken
from notd.model import Token
from notd.model import TokenCustomization
from notd.model import TokenListing
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.model import TradedToken
from notd.store.retriever import Retriever
from notd.token_metadata_processor import TokenMetadataProcessor

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

    async def collection_token_from_token_key(self, tokenKey: Token) -> ApiCollectionToken:
        return await self.collection_token_from_registry_address_token_id(registryAddress=tokenKey.registryAddress, tokenId=tokenKey.tokenId)

    async def collection_token_from_model(self, tokenMetadata: TokenMetadata) -> ApiCollectionToken:
        attributes = [{key: value for (key, value) in attribute.items() if key in VALID_ATTRIBUTE_FIELDS} for attribute in tokenMetadata.attributes] if isinstance(tokenMetadata.attributes, list) else []
        return ApiCollectionToken(
            registryAddress=tokenMetadata.registryAddress,
            tokenId=tokenMetadata.tokenId,
            metadataUrl=tokenMetadata.metadataUrl,
            name=tokenMetadata.name,
            description=tokenMetadata.description,
            imageUrl=tokenMetadata.imageUrl,
            resizableImageUrl=tokenMetadata.resizableImageUrl,
            frameImageUrl=tokenMetadata.frameImageUrl,
            attributes=attributes,
        )

    async def collection_tokens_from_models(self, tokenMetadatas: Sequence[TokenMetadata]) -> Sequence[ApiCollectionToken]:
        return await asyncio.gather(*[self.collection_token_from_model(tokenMetadata=tokenMetadata) for tokenMetadata in tokenMetadatas])

    async def collection_tokens_from_token_keys(self, tokenKeys: Sequence[Token]) -> Sequence[ApiCollectionToken]:
        return await asyncio.gather(*[self.collection_token_from_token_key(tokenKey=tokenKey) for tokenKey in tokenKeys])

    async def collection_token_from_registry_addresses_token_ids(self, tokens: Sequence[Token]) -> List[ApiCollectionToken]:
        tokenMetadatas = []
        for token in tokens:
            try:
                tokenMetadatas += [await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=token.registryAddress, tokenId=token.tokenId)]
            except NotFoundException:
                tokenMetadatas += [TokenMetadataProcessor.get_default_token_metadata(registryAddress=token.registryAddress, tokenId=token.tokenId)]
        return await self.collection_tokens_from_models(tokenMetadatas=tokenMetadatas)

    async def token_transfer_from_model(self, tokenTransfer: TokenTransfer) -> ApiTokenTransfer:
        return ApiTokenTransfer(
            tokenTransferId=tokenTransfer.tokenTransferId,
            transactionHash=tokenTransfer.transactionHash,
            registryAddress=tokenTransfer.registryAddress,
            fromAddress=tokenTransfer.fromAddress,
            toAddress=tokenTransfer.toAddress,
            contractAddress=tokenTransfer.contractAddress,
            tokenId=tokenTransfer.tokenId,
            value=str(tokenTransfer.value),
            gasLimit=tokenTransfer.gasLimit,
            gasPrice=tokenTransfer.gasPrice,
            tokenType=tokenTransfer.tokenType,
            blockNumber=tokenTransfer.blockNumber,
            blockDate=tokenTransfer.blockDate,
            isMultiAddress=tokenTransfer.isMultiAddress,
            isInterstitial=tokenTransfer.isInterstitial,
            isSwap=tokenTransfer.isSwap,
            isBatch=tokenTransfer.isBatch,
            isOutbound=tokenTransfer.isOutbound,
            collection=(await self.collection_from_address(address=tokenTransfer.registryAddress)),
            token=(await self.collection_token_from_registry_address_token_id(registryAddress=tokenTransfer.registryAddress, tokenId=tokenTransfer.tokenId)),
        )

    async def token_transfers_from_models(self, tokenTransfers: Sequence[TokenTransfer]) -> Sequence[TokenTransfer]:
        return await asyncio.gather(*[self.token_transfer_from_model(tokenTransfer=tokenTransfer) for tokenTransfer in tokenTransfers])

    async def get_collection_statistics(self, collectionStatistics: CollectionStatistics) -> ApiCollectionStatistics:
        return ApiCollectionStatistics(
            itemCount=collectionStatistics.itemCount,
            holderCount=collectionStatistics.holderCount,
            transferCount=str(collectionStatistics.transferCount),
            saleCount=str(collectionStatistics.saleCount),
            totalTradeVolume=str(collectionStatistics.totalTradeVolume),
            lowestSaleLast24Hours=str(collectionStatistics.lowestSaleLast24Hours),
            highestSaleLast24Hours=str(collectionStatistics.highestSaleLast24Hours),
            tradeVolume24Hours=str(collectionStatistics.tradeVolume24Hours),
        )

    async def traded_token_from_model(self, tradedToken: TradedToken) -> ApiTradedToken:
        return ApiTradedToken(
            token=await self.collection_token_from_registry_address_token_id(registryAddress=tradedToken.latestTransfer.registryAddress, tokenId=tradedToken.latestTransfer.tokenId),
            collection=await self.collection_from_address(address=tradedToken.latestTransfer.registryAddress),
            latestTransfer=await self.token_transfer_from_model(tokenTransfer=tradedToken.latestTransfer),
            transferCount=str(tradedToken.transferCount),
        )

    async def sponsored_token_from_model(self, sponsoredToken: SponsoredToken) -> ApiSponsoredToken:
        return ApiSponsoredToken(
            token=await self.collection_token_from_token_key(tokenKey=sponsoredToken.token),
            collection=await self.collection_from_address(address=sponsoredToken.token.registryAddress),
            latestTransfer=await self.token_transfer_from_model(tokenTransfer=sponsoredToken.latestTransfer) if sponsoredToken.latestTransfer else None,
            date=sponsoredToken.date,
        )

    async def collection_activities_from_models(self, collectionActivities: Sequence[CollectionDailyActivity]) -> Sequence[ApiCollectionDailyActivity]:
        return [ApiCollectionDailyActivity(
            date=collectionActivity.date,
            totalValue=str(collectionActivity.totalValue),
            transferCount=str(collectionActivity.transferCount),
            saleCount=str(collectionActivity.saleCount),
            minimumValue=str(collectionActivity.minimumValue),
            maximumValue=str(collectionActivity.maximumValue),
            averageValue=str(collectionActivity.averageValue)
        ) for collectionActivity in collectionActivities]

    async def airdrops_from_models(self, airdrops: Sequence[Airdrop]) -> Sequence[ApiAirdrop]:
        return [ApiAirdrop(
            token=await self.collection_token_from_token_key(tokenKey=airdrop.tokenKey),
            name=airdrop.name,
            isClaimed=airdrop.isClaimed,
            claimToken=await self.collection_token_from_token_key(tokenKey=airdrop.claimTokenKey),
            claimUrl=airdrop.claimUrl,
        ) for airdrop in airdrops]

    async def collection_attributes_from_models(self, collectionAttributes: Sequence[CollectionAttribute]) -> Sequence[ApiCollectionAttribute]:
        return [ApiCollectionAttribute(
            name=attribute.name,
            values=attribute.values
        ) for attribute in collectionAttributes]

    async def get_token_customization_for_collection_token(self, registryAddress: str, tokenId: str) -> ApiTokenCustomization:
        tokenCustomization = await self.retriever.get_token_customization_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        return await self.token_customization_from_model(tokenCustomization=tokenCustomization)

    async def token_customization_from_model(self, tokenCustomization: TokenCustomization) -> ApiTokenCustomization:
        return ApiTokenCustomization(
            tokenCustomizationId=tokenCustomization.tokenCustomizationId,
            createdDate=tokenCustomization.createdDate,
            updatedDate=tokenCustomization.updatedDate,
            registryAddress=tokenCustomization.registryAddress,
            tokenId=tokenCustomization.tokenId,
            creatorAddress=tokenCustomization.creatorAddress,
            blockNumber=tokenCustomization.blockNumber,
            signature=tokenCustomization.signature,
            name=tokenCustomization.name,
            description=tokenCustomization.description,
        )

    async def token_listing_from_model(self, tokenListing: TokenListing) -> ApiTokenListing:
        return ApiTokenListing(
            tokenListingId=tokenListing.tokenListingId,
            createdDate=tokenListing.createdDate,
            updatedDate=tokenListing.updatedDate,
            registryAddress=tokenListing.registryAddress,
            tokenId=tokenListing.tokenId,
            offererAddress=tokenListing.offererAddress,
            startDate=tokenListing.startDate,
            endDate=tokenListing.endDate,
            isValueNative=tokenListing.isValueNative,
            value=tokenListing.value,
            source=tokenListing.source,
            sourceId=tokenListing.sourceId,
        )

    async def gallery_token_from_model(self, galleryToken: GalleryToken) -> ApiGalleryToken:
        return ApiGalleryToken(
            collectionToken=(await self.collection_token_from_model(tokenMetadata=galleryToken.tokenMetadata)),
            tokenCustomization=(await self.token_customization_from_model(tokenCustomization=galleryToken.tokenCustomization) if galleryToken.tokenCustomization else None),
            tokenListing=(await self.token_listing_from_model(tokenListing=galleryToken.tokenListing) if galleryToken.tokenListing else None)
        )

    async def gallery_tokens_from_models(self, galleryTokens: Sequence[GalleryToken]) -> Sequence[ApiGalleryToken]:
        return await asyncio.gather(*[self.gallery_token_from_model(galleryToken=galleryToken) for galleryToken in galleryTokens])
