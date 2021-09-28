import datetime
from typing import Mapping

from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable


def token_transfer_from_row(row: Mapping) -> TokenTransfer:
    # NOTE(krishan711) these should be of the form row.id but https://github.com/encode/databases/issues/101
    return TokenTransfer(
        tokenTransferId=row[TokenTransfersTable.c.tokenTransferId],
        transactionHash=row[TokenTransfersTable.c.transactionHash],
        registryAddress=row[TokenTransfersTable.c.registryAddress],
        fromAddress=row[TokenTransfersTable.c.fromAddress],
        toAddress=row[TokenTransfersTable.c.toAddress],
        tokenId=row[TokenTransfersTable.c.tokenId],
        value=row[TokenTransfersTable.c.value],
        gasLimit=row[TokenTransfersTable.c.gasLimit],
        gasPrice=row[TokenTransfersTable.c.gasPrice],
        gasUsed=row[TokenTransfersTable.c.gasUsed],
        blockNumber=row[TokenTransfersTable.c.blockNumber],
        blockHash=row[TokenTransfersTable.c.blockHash],
        blockDate=row[TokenTransfersTable.c.blockDate].replace(tzinfo=datetime.timezone.utc),
    )
def token_metadata_from_row(row: Mapping) -> TokenMetadata:
    return TokenMetadata(
        tokenMetadataId=row[TokenMetadataTable.c.tokenMetadataId],
        createdDate=row[TokenMetadataTable.c.createdDate],
        updatedDate=row[TokenMetadataTable.c.updatedDate],
        registryAddress=row[TokenMetadataTable.c.registry_address],
        tokenId=row[TokenMetadataTable.c.tokenId],
        metadatatUrl=row[TokenMetadataTable.c.metadatUrl],
        imageUrl=row[TokenMetadataTable.c.imageUrl],
        name=row[TokenMetadataTable.c.name],
        description=row[TokenMetadataTable.c.description],
        attributes=row[TokenMetadataTable.c.attributes],
    )
