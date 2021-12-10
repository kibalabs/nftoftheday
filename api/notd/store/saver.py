import contextlib
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from core.store.saver import Saver as CoreSaver
from core.util import date_util

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

    @contextlib.asynccontextmanager
    async def create_transaction(self):
        transaction = self.database.transaction()
        try:
            await transaction.start()
            yield None
        except Exception as exception:
            logging.info(f'Rolling back due to exception: {exception}')
            await transaction.rollback()
            raise
        else:
            await transaction.commit()

    async def create_token_transfer(self, retrievedTokenTransfer: RetrievedTokenTransfer) -> TokenTransfer:
        tokenTransferId = await self._execute(query=TokenTransfersTable.insert(), values={  # pylint: disable=no-value-for-parameter
            TokenTransfersTable.c.transactionHash.key: retrievedTokenTransfer.transactionHash,
            TokenTransfersTable.c.registryAddress.key: retrievedTokenTransfer.registryAddress,
            TokenTransfersTable.c.fromAddress.key: retrievedTokenTransfer.fromAddress,
            TokenTransfersTable.c.toAddress.key: retrievedTokenTransfer.toAddress,
            TokenTransfersTable.c.tokenId.key: retrievedTokenTransfer.tokenId,
            TokenTransfersTable.c.value.key: retrievedTokenTransfer.value,
            TokenTransfersTable.c.gasLimit.key: retrievedTokenTransfer.gasLimit,
            TokenTransfersTable.c.gasPrice.key: retrievedTokenTransfer.gasPrice,
            TokenTransfersTable.c.gasUsed.key: retrievedTokenTransfer.gasUsed,
            TokenTransfersTable.c.blockNumber.key: retrievedTokenTransfer.blockNumber,
            TokenTransfersTable.c.blockHash.key: retrievedTokenTransfer.blockHash,
            TokenTransfersTable.c.blockDate.key: retrievedTokenTransfer.blockDate,
        })
        return TokenTransfer(
            tokenTransferId=tokenTransferId,
            transactionHash=retrievedTokenTransfer.transactionHash,
            registryAddress=retrievedTokenTransfer.registryAddress,
            fromAddress=retrievedTokenTransfer.fromAddress,
            toAddress=retrievedTokenTransfer.toAddress,
            tokenId=retrievedTokenTransfer.tokenId,
            value=retrievedTokenTransfer.value,
            gasLimit=retrievedTokenTransfer.gasLimit,
            gasPrice=retrievedTokenTransfer.gasPrice,
            gasUsed=retrievedTokenTransfer.gasUsed,
            blockNumber=retrievedTokenTransfer.blockNumber,
            blockHash=retrievedTokenTransfer.blockHash,
            blockDate=retrievedTokenTransfer.blockDate,
        )

    async def create_token_metadata(self, tokenId: int, registryAddress: str, metadataUrl: str, imageUrl: Optional[str], name: Optional[str], description: Optional[str], attributes: Union[None, Dict, List]) -> TokenMetadata:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        tokenMetadataId = await self._execute(query=TokenMetadataTable.insert(), values={  # pylint: disable=no-value-for-parameter
            TokenMetadataTable.c.createdDate.key: createdDate,
            TokenMetadataTable.c.updatedDate.key: updatedDate,
            TokenMetadataTable.c.registryAddress.key: registryAddress,
            TokenMetadataTable.c.tokenId.key: tokenId,
            TokenMetadataTable.c.metadataUrl.key: metadataUrl,
            TokenMetadataTable.c.imageUrl.key: imageUrl,
            TokenMetadataTable.c.name.key: name,
            TokenMetadataTable.c.description.key: description,
            TokenMetadataTable.c.attributes.key: attributes,
        })
        return TokenMetadata(
            tokenMetadataId=tokenMetadataId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            imageUrl=imageUrl,
            name=name,
            description=description,
            attributes=attributes,
        )

    async def update_token_metadata(self, tokenMetadataId: int, metadataUrl: Optional[str] = None, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, name: Optional[str] = _EMPTY_STRING, attributes: Union[None, Dict, List] = _EMPTY_OBJECT) -> None:
        query = TokenMetadataTable.update(TokenMetadataTable.c.tokenMetadataId == tokenMetadataId)
        values = {}
        if metadataUrl is not None:
            values[TokenMetadataTable.c.metadataUrl.key] = metadataUrl
        if imageUrl != _EMPTY_STRING:
            values[TokenMetadataTable.c.imageUrl.key] = imageUrl
        if description != _EMPTY_STRING:
            values[TokenMetadataTable.c.description.key] = description
        if name != _EMPTY_STRING:
            values[TokenMetadataTable.c.name.key] = name
        if attributes != _EMPTY_OBJECT:
            values[TokenMetadataTable.c.attributes.key] = attributes
        if len(values) > 0:
            values[TokenMetadataTable.c.updatedDate.key] = date_util.datetime_from_now()
        await self.database.execute(query=query, values=values)

    async def create_collection(self, address: str, name: Optional[str], symbol: Optional[str], description: Optional[str], imageUrl: Optional[str] , twitterUsername: Optional[str], instagramUsername: Optional[str], wikiUrl: Optional[str], openseaSlug: Optional[str], url: Optional[str], discordUrl: Optional[str], bannerImageUrl: Optional[str]) -> Collection:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        collectionId = await self._execute(query=TokenCollectionsTable.insert(), values={  # pylint: disable=no-value-for-parameter
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

        })
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
        )

    async def update_collection(self, collectionId: int, name: Optional[str], symbol: Optional[str], description: Optional[str], imageUrl: Optional[str] , twitterUsername: Optional[str], instagramUsername: Optional[str], wikiUrl: Optional[str], openseaSlug: Optional[str], url: Optional[str], discordUrl: Optional[str], bannerImageUrl: Optional[str]) -> None:
        query = TokenCollectionsTable.update(TokenCollectionsTable.c.collectionId == collectionId)
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
            values[TokenCollectionsTable.c.bannerImageUrl.key] = openseaSlug
        if len(values) > 0:
            values[TokenCollectionsTable.c.updatedDate.key] = date_util.datetime_from_now()
        await self.database.execute(query=query, values=values)
