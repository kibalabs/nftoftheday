from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from core.store.saver import Saver as CoreSaver
from core.store.database import DatabaseConnection
from core.util import date_util
from core.util import list_util

from notd.model import Collection
from notd.model import RetrievedTokenTransfer
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable

_EMPTY_STRING = '_EMPTY_STRING'
_EMPTY_OBJECT = '_EMPTY_OBJECT'

class Saver(CoreSaver):

    @staticmethod
    def _get_create_token_transfer_values(retrievedTokenTransfer: RetrievedTokenTransfer) -> Dict[str, Union[str, int, float, None, bool]]:
        return {
            TokenTransfersTable.c.transactionHash.key: retrievedTokenTransfer.transactionHash,
            TokenTransfersTable.c.registryAddress.key: retrievedTokenTransfer.registryAddress,
            TokenTransfersTable.c.fromAddress.key: retrievedTokenTransfer.fromAddress,
            TokenTransfersTable.c.toAddress.key: retrievedTokenTransfer.toAddress,
            TokenTransfersTable.c.operatorAddress.key: retrievedTokenTransfer.operatorAddress,
            TokenTransfersTable.c.tokenId.key: retrievedTokenTransfer.tokenId,
            TokenTransfersTable.c.value.key: retrievedTokenTransfer.value,
            TokenTransfersTable.c.amount.key: retrievedTokenTransfer.amount,
            TokenTransfersTable.c.gasLimit.key: retrievedTokenTransfer.gasLimit,
            TokenTransfersTable.c.gasPrice.key: retrievedTokenTransfer.gasPrice,
            TokenTransfersTable.c.gasUsed.key: retrievedTokenTransfer.gasUsed,
            TokenTransfersTable.c.blockNumber.key: retrievedTokenTransfer.blockNumber,
            TokenTransfersTable.c.blockHash.key: retrievedTokenTransfer.blockHash,
            TokenTransfersTable.c.blockDate.key: retrievedTokenTransfer.blockDate,
            TokenTransfersTable.c.tokenType.key: retrievedTokenTransfer.tokenType,
        }

    @staticmethod
    def _token_transfer_from_retrieved(tokenTransferId: int, retrievedTokenTransfer: RetrievedTokenTransfer) -> TokenTransfer:
        return TokenTransfer(
            tokenTransferId=tokenTransferId,
            transactionHash=retrievedTokenTransfer.transactionHash,
            registryAddress=retrievedTokenTransfer.registryAddress,
            fromAddress=retrievedTokenTransfer.fromAddress,
            toAddress=retrievedTokenTransfer.toAddress,
            operatorAddress=retrievedTokenTransfer.operatorAddress,
            tokenId=retrievedTokenTransfer.tokenId,
            value=retrievedTokenTransfer.value,
            amount=retrievedTokenTransfer.amount,
            gasLimit=retrievedTokenTransfer.gasLimit,
            gasPrice=retrievedTokenTransfer.gasPrice,
            gasUsed=retrievedTokenTransfer.gasUsed,
            blockNumber=retrievedTokenTransfer.blockNumber,
            blockHash=retrievedTokenTransfer.blockHash,
            blockDate=retrievedTokenTransfer.blockDate,
            tokenType=retrievedTokenTransfer.tokenType
        )

    async def create_token_transfer(self, retrievedTokenTransfer: RetrievedTokenTransfer, connection: Optional[DatabaseConnection] = None) -> TokenTransfer:
        values = self._get_create_token_transfer_values(retrievedTokenTransfer=retrievedTokenTransfer)
        query = TokenTransfersTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        tokenTransferId = result.inserted_primary_key[0]
        return self._token_transfer_from_retrieved(tokenTransferId=tokenTransferId, retrievedTokenTransfer=retrievedTokenTransfer)

    async def create_token_transfers(self, retrievedTokenTransfers: List[RetrievedTokenTransfer], connection: Optional[DatabaseConnection] = None) -> List[TokenTransfer]:
        if len(retrievedTokenTransfers) == 0:
            return
        tokenTransferIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenTransfers, chunkSize=100):
            values = [self._get_create_token_transfer_values(retrievedTokenTransfer=retrievedTokenTransfer) for retrievedTokenTransfer in chunk]
            query = TokenTransfersTable.insert().values(values).returning(TokenTransfersTable.c.tokenTransferId)
            rows = await self._execute(query=query, connection=connection)
            tokenTransferIds += [row[0] for row in rows]
        return [self._token_transfer_from_retrieved(tokenTransferId=tokenTransferId, retrievedTokenTransfer=retrievedTokenTransfer) for tokenTransferId, retrievedTokenTransfer in zip(tokenTransferIds, retrievedTokenTransfers)]

    async def delete_token_transfer(self, tokenTransferId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = TokenTransfersTable.delete().where(TokenTransfersTable.c.tokenTransferId == tokenTransferId)
        await self._execute(query=query, connection=connection)

    async def delete_token_transfers(self, tokenTransferIds: List[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(tokenTransferIds) == 0:
            return
        query = TokenTransfersTable.delete().where(TokenTransfersTable.c.tokenTransferId.in_(tokenTransferIds))
        await self._execute(query=query, connection=connection)

    async def create_token_metadata(self, tokenId: int, registryAddress: str, metadataUrl: str, imageUrl: Optional[str], animationUrl: Optional[str], youtubeUrl: Optional[str], backgroundColor: Optional[str], name: Optional[str], description: Optional[str], attributes: Union[None, Dict, List], connection: Optional[DatabaseConnection] = None) -> TokenMetadata:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            TokenMetadataTable.c.createdDate.key: createdDate,
            TokenMetadataTable.c.updatedDate.key: updatedDate,
            TokenMetadataTable.c.registryAddress.key: registryAddress,
            TokenMetadataTable.c.tokenId.key: tokenId,
            TokenMetadataTable.c.metadataUrl.key: metadataUrl,
            TokenMetadataTable.c.imageUrl.key: imageUrl,
            TokenMetadataTable.c.animationUrl.key: animationUrl,
            TokenMetadataTable.c.youtubeUrl.key: youtubeUrl,
            TokenMetadataTable.c.backgroundColor.key: backgroundColor,
            TokenMetadataTable.c.name.key: name,
            TokenMetadataTable.c.description.key: description,
            TokenMetadataTable.c.attributes.key: attributes,
        }
        query = TokenMetadataTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        tokenMetadataId = result.inserted_primary_key[0]
        return TokenMetadata(
            tokenMetadataId=tokenMetadataId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            imageUrl=imageUrl,
            animationUrl=animationUrl,
            youtubeUrl=youtubeUrl,
            backgroundColor=backgroundColor,
            name=name,
            description=description,
            attributes=attributes,
        )

    async def update_token_metadata(self, tokenMetadataId: int, metadataUrl: Optional[str] = None, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, animationUrl: Optional[str] = _EMPTY_STRING, youtubeUrl: Optional[str] = _EMPTY_STRING, backgroundColor: Optional[str] = _EMPTY_STRING, name: Optional[str] = _EMPTY_STRING, attributes: Union[None, Dict, List] = _EMPTY_OBJECT, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
        if metadataUrl is not None:
            values[TokenMetadataTable.c.metadataUrl.key] = metadataUrl
        if imageUrl != _EMPTY_STRING:
            values[TokenMetadataTable.c.imageUrl.key] = imageUrl
        if animationUrl != _EMPTY_STRING:
            values[TokenMetadataTable.c.animationUrl.key] = animationUrl
        if youtubeUrl != _EMPTY_STRING:
            values[TokenMetadataTable.c.youtubeUrl.key] = youtubeUrl
        if backgroundColor != _EMPTY_STRING:
            values[TokenMetadataTable.c.backgroundColor.key] = backgroundColor
        if description != _EMPTY_STRING:
            values[TokenMetadataTable.c.description.key] = description
        if name != _EMPTY_STRING:
            values[TokenMetadataTable.c.name.key] = name
        if attributes != _EMPTY_OBJECT:
            values[TokenMetadataTable.c.attributes.key] = attributes
        if len(values) > 0:
            values[TokenMetadataTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TokenMetadataTable.update(TokenMetadataTable.c.tokenMetadataId == tokenMetadataId).values(values)
        await self._execute(query=query, connection=connection)

    async def create_collection(self, address: str, name: Optional[str], symbol: Optional[str], description: Optional[str], imageUrl: Optional[str] , twitterUsername: Optional[str], instagramUsername: Optional[str], wikiUrl: Optional[str], openseaSlug: Optional[str], url: Optional[str], discordUrl: Optional[str], bannerImageUrl: Optional[str], doesSupportErc721: bool, doesSupportErc1155: bool, connection: Optional[DatabaseConnection] = None) -> Collection:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            TokenCollectionsTable.c.createdDate.key: createdDate,
            TokenCollectionsTable.c.updatedDate.key: updatedDate,
            TokenCollectionsTable.c.address.key: address,
            TokenCollectionsTable.c.name.key: name,
            TokenCollectionsTable.c.symbol.key: symbol,
            TokenCollectionsTable.c.description.key: description,
            TokenCollectionsTable.c.imageUrl.key: imageUrl,
            TokenCollectionsTable.c.twitterUsername.key: twitterUsername,
            TokenCollectionsTable.c.instagramUsername.key: instagramUsername,
            TokenCollectionsTable.c.wikiUrl.key: wikiUrl,
            TokenCollectionsTable.c.openseaSlug.key: openseaSlug,
            TokenCollectionsTable.c.url.key: url,
            TokenCollectionsTable.c.discordUrl.key: discordUrl,
            TokenCollectionsTable.c.bannerImageUrl.key: bannerImageUrl,
            TokenCollectionsTable.c.doesSupportErc721.key: doesSupportErc721,
            TokenCollectionsTable.c.doesSupportErc1155.key: doesSupportErc1155,
        }
        query = TokenCollectionsTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        collectionId = result.inserted_primary_key[0]
        return Collection(
            collectionId=collectionId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            address=address,
            name=name,
            symbol=symbol,
            description=description,
            imageUrl=imageUrl,
            twitterUsername=twitterUsername,
            instagramUsername=instagramUsername,
            wikiUrl=wikiUrl,
            openseaSlug=openseaSlug,
            url=url,
            discordUrl=discordUrl,
            bannerImageUrl=bannerImageUrl,
            doesSupportErc721=doesSupportErc721,
            doesSupportErc1155=doesSupportErc1155,
        )

    async def update_collection(self, collectionId: int, name: Optional[str], symbol: Optional[str], description: Optional[str], imageUrl: Optional[str] , twitterUsername: Optional[str], instagramUsername: Optional[str], wikiUrl: Optional[str], openseaSlug: Optional[str], url: Optional[str], discordUrl: Optional[str], bannerImageUrl: Optional[str], doesSupportErc721: Optional[bool], doesSupportErc1155: Optional[bool], connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
        if name != _EMPTY_STRING:
            values[TokenCollectionsTable.c.name.key] = name
        if symbol != _EMPTY_STRING:
            values[TokenCollectionsTable.c.symbol.key] = symbol
        if description != _EMPTY_STRING:
            values[TokenCollectionsTable.c.description.key] = description
        if imageUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.imageUrl.key] = imageUrl
        if twitterUsername != _EMPTY_STRING:
            values[TokenCollectionsTable.c.twitterUsername.key] = twitterUsername
        if instagramUsername != _EMPTY_STRING:
            values[TokenCollectionsTable.c.instagramUsername.key] = instagramUsername
        if wikiUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.wikiUrl.key] = wikiUrl
        if openseaSlug != _EMPTY_STRING:
            values[TokenCollectionsTable.c.openseaSlug.key] = openseaSlug
        if url != _EMPTY_STRING:
            values[TokenCollectionsTable.c.url.key] = url
        if discordUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.discordUrl.key] = discordUrl
        if bannerImageUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.bannerImageUrl.key] = bannerImageUrl
        if doesSupportErc721 is not None:
            values[TokenCollectionsTable.c.doesSupportErc721.key] = doesSupportErc721
        if doesSupportErc1155 is not None:
            values[TokenCollectionsTable.c.doesSupportErc1155.key] = doesSupportErc1155
        if len(values) > 0:
            values[TokenCollectionsTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TokenCollectionsTable.update(TokenCollectionsTable.c.collectionId == collectionId).values(values)
        await self._execute(query=query, connection=connection)
