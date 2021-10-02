import contextlib
from operator import and_
from typing import Optional

from core.store.saver import Saver as CoreSaver
from core.util import date_util

from notd.model import RetrievedTokenMetadata
from notd.model import RetrievedTokenTransfer
from notd.model import TokenMetadata
from notd.model import TokenTransfer
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
        except:
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

    async def create_token_metadata(self, retrievedTokenMetadata: RetrievedTokenMetadata) -> TokenMetadata:
        tokenMetadataId = await self._execute(query=TokenMetadataTable.insert(), values={  # pylint: disable=no-value-for-parameter
            TokenMetadataTable.c.createdDate.key: retrievedTokenMetadata.createdDate,
            TokenMetadataTable.c.updatedDate.key: retrievedTokenMetadata.updatedDate,
            TokenMetadataTable.c.registryAddress.key: retrievedTokenMetadata.registryAddress,
            TokenMetadataTable.c.tokenId.key: retrievedTokenMetadata.tokenId,
            TokenMetadataTable.c.metadataUrl.key: retrievedTokenMetadata.metadataUrl,
            TokenMetadataTable.c.imageUrl.key: retrievedTokenMetadata.imageUrl,
            TokenMetadataTable.c.name.key: retrievedTokenMetadata.name,
            TokenMetadataTable.c.description.key: retrievedTokenMetadata.description,
            TokenMetadataTable.c.attributes.key: retrievedTokenMetadata.attributes,
        })
        return TokenMetadata(
            tokenMetadataId=tokenMetadataId,
            createdDate=retrievedTokenMetadata.createdDate,
            updatedDate=retrievedTokenMetadata.updatedDate,
            registryAddress=retrievedTokenMetadata.registryAddress,
            tokenId=retrievedTokenMetadata.tokenId,
            metadataUrl=retrievedTokenMetadata.metadataUrl,
            imageUrl=retrievedTokenMetadata.imageUrl,
            name=retrievedTokenMetadata.name,
            description=retrievedTokenMetadata.description,
            attributes=retrievedTokenMetadata.attributes,
        )

    async def update_token_metadata_item(self, registryAddress: str, tokenId: str, metadataUrl: Optional[str] = None, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, name: Optional[str] = _EMPTY_STRING, attributes: Optional[str] = _EMPTY_OBJECT) -> None:
        query = TokenMetadataTable.update(and_(TokenMetadataTable.c.registryAddress == registryAddress,TokenMetadataTable.c.tokenId ==tokenId))
        values = {}
        if metadataUrl is not None:
            values[TokenMetadataTable.c.metadataUrl.key] = metadataUrl
        if imageUrl != _EMPTY_STRING:
            values[TokenMetadataTable.c.imageUrl.key] = imageUrl
        if description != _EMPTY_STRING:
            values[TokenMetadataTable.c.description.key] = description
        if name != _EMPTY_STRING:
            values[TokenMetadataTable.c.name.key] = name
        if attributes is not _EMPTY_OBJECT:
            values[TokenMetadataTable.c.attributes.key] = attributes
        if len(values) > 0:
            values[TokenMetadataTable.c.updatedDate.key] = date_util.datetime_from_now()
        await self.database.execute(query=query, values=values)
