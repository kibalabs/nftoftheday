from typing import Mapping
from notd.model import TokenOwnership

from notd.model import Block
from notd.model import Collection
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.store.schema import BlocksTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenOwnershipTable
from notd.store.schema import TokenTransfersTable


def token_transfer_from_row(row: Mapping) -> TokenTransfer:
    return TokenTransfer(
        tokenTransferId=row[TokenTransfersTable.c.tokenTransferId],
        transactionHash=row[TokenTransfersTable.c.transactionHash],
        registryAddress=row[TokenTransfersTable.c.registryAddress],
        fromAddress=row[TokenTransfersTable.c.fromAddress],
        toAddress=row[TokenTransfersTable.c.toAddress],
        operatorAddress=row[TokenTransfersTable.c.operatorAddress],
        tokenId=row[TokenTransfersTable.c.tokenId],
        value=row[TokenTransfersTable.c.value],
        amount=row[TokenTransfersTable.c.amount],
        gasLimit=row[TokenTransfersTable.c.gasLimit],
        gasPrice=row[TokenTransfersTable.c.gasPrice],
        blockNumber=row[TokenTransfersTable.c.blockNumber],
        blockDate=row[BlocksTable.c.blockDate],
        tokenType=row[TokenTransfersTable.c.tokenType],
    )

def block_from_row(row: Mapping) -> Block:
    return Block(
        blockId=row[BlocksTable.c.blockId],
        createdDate=row[BlocksTable.c.createdDate],
        updatedDate=row[BlocksTable.c.updatedDate],
        blockNumber=row[BlocksTable.c.blockNumber],
        blockHash=row[BlocksTable.c.blockHash],
        blockDate=row[BlocksTable.c.blockDate],
    )

def token_metadata_from_row(row: Mapping) -> TokenMetadata:
    return TokenMetadata(
        tokenMetadataId=row[TokenMetadataTable.c.tokenMetadataId],
        createdDate=row[TokenMetadataTable.c.createdDate],
        updatedDate=row[TokenMetadataTable.c.updatedDate],
        registryAddress=row[TokenMetadataTable.c.registryAddress],
        tokenId=row[TokenMetadataTable.c.tokenId],
        metadataUrl=row[TokenMetadataTable.c.metadataUrl],
        name=row[TokenMetadataTable.c.name],
        imageUrl=row[TokenMetadataTable.c.imageUrl],
        animationUrl=row[TokenMetadataTable.c.animationUrl],
        youtubeUrl=row[TokenMetadataTable.c.youtubeUrl],
        backgroundColor=row[TokenMetadataTable.c.backgroundColor],
        description=row[TokenMetadataTable.c.description],
        attributes=row[TokenMetadataTable.c.attributes],
    )

def collection_from_row(row: Mapping) -> Collection:
    return Collection(
        collectionId=row[TokenCollectionsTable.c.collectionId],
        createdDate=row[TokenCollectionsTable.c.createdDate],
        updatedDate=row[TokenCollectionsTable.c.updatedDate],
        address=row[TokenCollectionsTable.c.address],
        name=row[TokenCollectionsTable.c.name],
        symbol=row[TokenCollectionsTable.c.symbol],
        description=row[TokenCollectionsTable.c.description],
        imageUrl=row[TokenCollectionsTable.c.imageUrl],
        twitterUsername=row[TokenCollectionsTable.c.twitterUsername],
        instagramUsername=row[TokenCollectionsTable.c.instagramUsername],
        wikiUrl=row[TokenCollectionsTable.c.wikiUrl],
        openseaSlug=row[TokenCollectionsTable.c.openseaSlug],
        url=row[TokenCollectionsTable.c.url],
        discordUrl=row[TokenCollectionsTable.c.discordUrl],
        bannerImageUrl=row[TokenCollectionsTable.c.bannerImageUrl],
        doesSupportErc721=row[TokenCollectionsTable.c.doesSupportErc721],
        doesSupportErc1155=row[TokenCollectionsTable.c.doesSupportErc1155],
    )

def token_ownership_from_row(row: Mapping) -> TokenOwnership:
    return TokenOwnership(
        ownerId=row[TokenOwnershipTable.c.ownerId],
        createdDate=row[TokenOwnershipTable.c.createdDate],
        updatedDate=row[TokenOwnershipTable.c.updatedDate],
        ownerAddress=row[TokenOwnershipTable.c.ownerAddress],
        registryAddress=row[TokenOwnershipTable.c.registryAddress],
        tokenId=row[TokenOwnershipTable.c.tokenId],
        purchasedDate=row[TokenOwnershipTable.c.purchasedDate],
        purchasedValue=row[TokenOwnershipTable.c.purchasedValue],
    )
