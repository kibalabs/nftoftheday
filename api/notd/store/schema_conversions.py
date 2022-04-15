from typing import Mapping
from api.notd.model import TokenStatistics
from api.notd.store.schema import TokenStatisticsTable

from notd.model import Block
from notd.model import Collection
from notd.model import TokenMetadata
from notd.model import TokenMultiOwnership
from notd.model import TokenOwnership
from notd.model import TokenTransfer
from notd.store.schema import BlocksTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
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
        tokenType=row[TokenTransfersTable.c.tokenType],
        blockDate=row[BlocksTable.c.blockDate],
        updatedDate=row[BlocksTable.c.updatedDate],
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
        tokenMetadataId=row[TokenMetadatasTable.c.tokenMetadataId],
        createdDate=row[TokenMetadatasTable.c.createdDate],
        updatedDate=row[TokenMetadatasTable.c.updatedDate],
        registryAddress=row[TokenMetadatasTable.c.registryAddress],
        tokenId=row[TokenMetadatasTable.c.tokenId],
        metadataUrl=row[TokenMetadatasTable.c.metadataUrl],
        name=row[TokenMetadatasTable.c.name],
        imageUrl=row[TokenMetadatasTable.c.imageUrl],
        animationUrl=row[TokenMetadatasTable.c.animationUrl],
        youtubeUrl=row[TokenMetadatasTable.c.youtubeUrl],
        backgroundColor=row[TokenMetadatasTable.c.backgroundColor],
        frameImageUrl=row[TokenMetadatasTable.c.frameImageUrl],
        description=row[TokenMetadatasTable.c.description],
        attributes=row[TokenMetadatasTable.c.attributes],
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
        tokenOwnershipId=row[TokenOwnershipsTable.c.tokenOwnershipId],
        createdDate=row[TokenOwnershipsTable.c.createdDate],
        updatedDate=row[TokenOwnershipsTable.c.updatedDate],
        registryAddress=row[TokenOwnershipsTable.c.registryAddress],
        tokenId=row[TokenOwnershipsTable.c.tokenId],
        ownerAddress=row[TokenOwnershipsTable.c.ownerAddress],
        transferValue=row[TokenOwnershipsTable.c.transferValue],
        transferDate=row[TokenOwnershipsTable.c.transferDate],
        transferTransactionHash=row[TokenOwnershipsTable.c.transferTransactionHash],
    )

def token_multi_ownership_from_row(row: Mapping) -> TokenMultiOwnership:
    return TokenMultiOwnership(
        tokenMultiOwnershipId=row[TokenMultiOwnershipsTable.c.tokenMultiOwnershipId],
        createdDate=row[TokenMultiOwnershipsTable.c.createdDate],
        updatedDate=row[TokenMultiOwnershipsTable.c.updatedDate],
        registryAddress=row[TokenMultiOwnershipsTable.c.registryAddress],
        tokenId=row[TokenMultiOwnershipsTable.c.tokenId],
        ownerAddress=row[TokenMultiOwnershipsTable.c.ownerAddress],
        quantity=row[TokenMultiOwnershipsTable.c.quantity],
        averageTransferValue=row[TokenMultiOwnershipsTable.c.averageTransferValue],
        latestTransferDate=row[TokenMultiOwnershipsTable.c.latestTransferDate],
        latestTransferTransactionHash=row[TokenMultiOwnershipsTable.c.latestTransferTransactionHash],
    )

def token_statistics_from_row(row: Mapping) -> TokenStatistics:
    return TokenStatistics(
        tokenStatisticsId=row[TokenStatisticsTable.tokenStatisticsId],
        createdDate=row[TokenStatisticsTable.c.createdDate],
        updatedDate=row[TokenStatisticsTable.c.updatedDate],
        address=row[TokenStatisticsTable.address],
        date=row[TokenStatisticsTable.date],
        transferCount=row[TokenStatisticsTable.transferCount],
        totalVolume=row[TokenStatisticsTable.totalVolume],
        minimumValue=row[TokenStatisticsTable.minimumValue],
        maximumValue=row[TokenStatisticsTable.maximumValue],
        averageValue=row[TokenStatisticsTable.averageValue],
    )
