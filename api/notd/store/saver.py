import contextlib
from typing import Optional

from core.store.saver import Saver as CoreSaver
from core.util import date_util
from sqlalchemy.sql.expression import and_

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

    async def create_token_metadata(self, registryAddress: str, tokenId: str, metadataUrl: Optional[str] = None, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, name: Optional[str] = _EMPTY_STRING, attributes: Optional[str] = _EMPTY_OBJECT) -> TokenMetadata:
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

<<<<<<< HEAD
    async def update_token_metadata_item(self, tokenMetadataId: int, metadataUrl: Optional[str] = None, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, name: Optional[str] = _EMPTY_STRING, attributes: Optional[str] = _EMPTY_OBJECT) -> None:
        query = TokenMetadataTable.update(TokenMetadataTable.c.tokenMetadataId == tokenMetadataId)
=======
    async def update_token_metadata(self, registryAddress: str, tokenId: str, metadataUrl: Optional[str] = None, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, name: Optional[str] = _EMPTY_STRING, attributes: Optional[str] = _EMPTY_OBJECT) -> None:
        query = TokenMetadataTable.update(and_(TokenMetadataTable.c.registryAddress == registryAddress,TokenMetadataTable.c.tokenId ==tokenId))
>>>>>>> 415fd783a75d85756966cb9d5e68601436b22238
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
