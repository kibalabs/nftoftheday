from typing import Mapping

from notd.model import Block
from notd.model import Collection
from notd.model import CollectionHourlyActivity
from notd.model import LatestUpdate
from notd.model import TokenAttribute
from notd.model import TokenCustomization
from notd.model import TokenListing
from notd.model import TokenMetadata
from notd.model import TokenMultiOwnership
from notd.model import TokenOwnership
from notd.model import TokenTransfer
from notd.model import UserInteraction
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import LatestUpdatesTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenCustomizationsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import UserInteractionsTable


def token_transfer_from_row(row: Mapping) -> TokenTransfer:
    return TokenTransfer(
        tokenTransferId=row[TokenTransfersTable.c.tokenTransferId],
        transactionHash=row[TokenTransfersTable.c.transactionHash],
        registryAddress=row[TokenTransfersTable.c.registryAddress],
        tokenId=row[TokenTransfersTable.c.tokenId],
        fromAddress=row[TokenTransfersTable.c.fromAddress],
        toAddress=row[TokenTransfersTable.c.toAddress],
        operatorAddress=row[TokenTransfersTable.c.operatorAddress],
        contractAddress=row[TokenTransfersTable.c.contractAddress],
        value=row[TokenTransfersTable.c.value],
        amount=row[TokenTransfersTable.c.amount],
        gasLimit=row[TokenTransfersTable.c.gasLimit],
        gasPrice=row[TokenTransfersTable.c.gasPrice],
        blockNumber=row[TokenTransfersTable.c.blockNumber],
        tokenType=row[TokenTransfersTable.c.tokenType],
        isMultiAddress=row[TokenTransfersTable.c.isMultiAddress],
        isInterstitial=row[TokenTransfersTable.c.isInterstitial],
        isSwap=row[TokenTransfersTable.c.isSwap],
        isBatch=row[TokenTransfersTable.c.isBatch],
        isOutbound=row[TokenTransfersTable.c.isOutbound],
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
        resizableImageUrl=row[TokenMetadatasTable.c.resizableImageUrl],
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


def collection_activity_from_row(row: Mapping) -> CollectionHourlyActivity:
    return CollectionHourlyActivity(
        collectionActivityId=row[CollectionHourlyActivityTable.c.collectionActivityId],
        createdDate=row[CollectionHourlyActivityTable.c.createdDate],
        updatedDate=row[CollectionHourlyActivityTable.c.updatedDate],
        address=row[CollectionHourlyActivityTable.c.address],
        date=row[CollectionHourlyActivityTable.c.date],
        transferCount=row[CollectionHourlyActivityTable.c.transferCount],
        saleCount=row[CollectionHourlyActivityTable.c.saleCount],
        totalValue=row[CollectionHourlyActivityTable.c.totalValue],
        minimumValue=row[CollectionHourlyActivityTable.c.minimumValue],
        maximumValue=row[CollectionHourlyActivityTable.c.maximumValue],
        averageValue=row[CollectionHourlyActivityTable.c.averageValue],
    )


def user_interaction_from_row(row: Mapping) -> UserInteraction:
    return UserInteraction(
        userInteractionId=row[UserInteractionsTable.c.userInteractionId],
        createdDate=row[UserInteractionsTable.c.createdDate],
        updatedDate=row[UserInteractionsTable.c.updatedDate],
        date=row[UserInteractionsTable.c.date],
        userAddress=row[UserInteractionsTable.c.userAddress],
        command=row[UserInteractionsTable.c.command],
        signature=row[UserInteractionsTable.c.signature],
        message=row[UserInteractionsTable.c.message],
    )


def latest_update_from_row(row: Mapping) -> LatestUpdate:
    return LatestUpdate(
        latestUpdateId=row[LatestUpdatesTable.c.latestUpdateId],
        createdDate=row[LatestUpdatesTable.c.createdDate],
        updatedDate=row[LatestUpdatesTable.c.updatedDate],
        key=row[LatestUpdatesTable.c.key],
        name=row[LatestUpdatesTable.c.name],
        date=row[LatestUpdatesTable.c.date],
    )


def token_listing_from_row(row: Mapping) -> TokenListing:
    return TokenListing(
        tokenListingId=row[LatestTokenListingsTable.c.latestTokenListingId],
        createdDate=row[LatestTokenListingsTable.c.createdDate],
        updatedDate=row[LatestTokenListingsTable.c.updatedDate],
        registryAddress=row[LatestTokenListingsTable.c.registryAddress],
        tokenId=row[LatestTokenListingsTable.c.tokenId],
        offererAddress=row[LatestTokenListingsTable.c.offererAddress],
        startDate=row[LatestTokenListingsTable.c.startDate],
        endDate=row[LatestTokenListingsTable.c.endDate],
        isValueNative=row[LatestTokenListingsTable.c.isValueNative],
        value=row[LatestTokenListingsTable.c.value],
        source=row[LatestTokenListingsTable.c.source],
        sourceId=row[LatestTokenListingsTable.c.sourceId],
    )


def token_attribute_from_row(row: Mapping) -> TokenAttribute:
    return TokenAttribute(
        tokenAttributeId=row[TokenAttributesTable.c.tokenAttributeId],
        createdDate=row[TokenAttributesTable.c.createdDate],
        updatedDate=row[TokenAttributesTable.c.updatedDate],
        registryAddress=row[TokenAttributesTable.c.registryAddress],
        tokenId=row[TokenAttributesTable.c.tokenId],
        name=row[TokenAttributesTable.c.name],
        value=row[TokenAttributesTable.c.value],
    )


def token_customization_from_row(row: Mapping) -> TokenCustomization:
    return TokenCustomization(
        tokenCustomizationId=row[TokenCustomizationsTable.c.tokenCustomizationId],
        createdDate=row[TokenCustomizationsTable.c.createdDate],
        updatedDate=row[TokenCustomizationsTable.c.updatedDate],
        registryAddress=row[TokenCustomizationsTable.c.registryAddress],
        tokenId=row[TokenCustomizationsTable.c.tokenId],
        creatorAddress=row[TokenCustomizationsTable.c.creatorAddress],
        signature=row[TokenCustomizationsTable.c.signature],
        blockNumber=row[TokenCustomizationsTable.c.blockNumber],
        name=row[TokenCustomizationsTable.c.name],
        description=row[TokenCustomizationsTable.c.description],
    )
