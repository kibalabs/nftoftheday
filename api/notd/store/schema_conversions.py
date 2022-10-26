from typing import TYPE_CHECKING, Any
from typing import Mapping
from typing import Optional
from typing import Union

from sqlalchemy import Column
from sqlalchemy import Table

from notd.model import AccountCollectionGm
from notd.model import AccountGm
from notd.model import Block
from notd.model import Collection
from notd.model import CollectionHourlyActivity
from notd.model import CollectionOverlap
from notd.model import CollectionTotalActivity
from notd.model import GalleryBadgeHolder
from notd.model import LatestUpdate
from notd.model import Lock
from notd.model import Signature
from notd.model import TokenAttribute
from notd.model import TokenCustomization
from notd.model import TokenListing
from notd.model import TokenMetadata
from notd.model import TokenMultiOwnership
from notd.model import TokenOwnership
from notd.model import TokenTransfer
from notd.model import TwitterCredential
from notd.model import TwitterProfile
from notd.model import UserInteraction
from notd.model import UserProfile
from notd.store.schema import AccountCollectionGmsTable
from notd.store.schema import AccountGmsTable
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import GalleryBadgeHoldersTable
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import LatestUpdatesTable
from notd.store.schema import LocksTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionOverlapsTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenCustomizationsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import TwitterCredentialsTable
from notd.store.schema import TwitterProfilesTable
from notd.store.schema import UserInteractionsTable
from notd.store.schema import UserProfilesTable

if TYPE_CHECKING:
    from sqlalchemy.engine import RowProxy
else:
    RowProxy = Any

RowType = Union[Mapping[Column[Any], Any], RowProxy]  # type: ignore[misc]


def token_transfer_from_row(row: RowType) -> TokenTransfer:
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


def block_from_row(row: RowType) -> Block:
    return Block(
        blockId=row[BlocksTable.c.blockId],
        createdDate=row[BlocksTable.c.createdDate],
        updatedDate=row[BlocksTable.c.updatedDate],
        blockNumber=row[BlocksTable.c.blockNumber],
        blockHash=row[BlocksTable.c.blockHash],
        blockDate=row[BlocksTable.c.blockDate],
    )


def token_metadata_from_row(row: RowType) -> TokenMetadata:
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


def collection_from_row(row: RowType) -> Collection:
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


def token_ownership_from_row(row: RowType) -> TokenOwnership:
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


def token_multi_ownership_from_row(row: RowType) -> TokenMultiOwnership:
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


def collection_activity_from_row(row: RowType) -> CollectionHourlyActivity:
    return CollectionHourlyActivity(
        collectionActivityId=row[CollectionHourlyActivitiesTable.c.collectionActivityId],
        createdDate=row[CollectionHourlyActivitiesTable.c.createdDate],
        updatedDate=row[CollectionHourlyActivitiesTable.c.updatedDate],
        address=row[CollectionHourlyActivitiesTable.c.address],
        date=row[CollectionHourlyActivitiesTable.c.date],
        transferCount=row[CollectionHourlyActivitiesTable.c.transferCount],
        saleCount=row[CollectionHourlyActivitiesTable.c.saleCount],
        totalValue=row[CollectionHourlyActivitiesTable.c.totalValue],
        minimumValue=row[CollectionHourlyActivitiesTable.c.minimumValue],
        maximumValue=row[CollectionHourlyActivitiesTable.c.maximumValue],
        averageValue=row[CollectionHourlyActivitiesTable.c.averageValue],
    )


def collection_total_activity_from_row(row: RowType) -> CollectionTotalActivity:
    return CollectionTotalActivity(
        collectionTotalActivityId=row[CollectionTotalActivitiesTable.c.collectionTotalActivityId],
        createdDate=row[CollectionTotalActivitiesTable.c.createdDate],
        updatedDate=row[CollectionTotalActivitiesTable.c.updatedDate],
        address=row[CollectionTotalActivitiesTable.c.address],
        transferCount=row[CollectionTotalActivitiesTable.c.transferCount],
        saleCount=row[CollectionTotalActivitiesTable.c.saleCount],
        totalValue=row[CollectionTotalActivitiesTable.c.totalValue],
        minimumValue=row[CollectionTotalActivitiesTable.c.minimumValue],
        maximumValue=row[CollectionTotalActivitiesTable.c.maximumValue],
        averageValue=row[CollectionTotalActivitiesTable.c.averageValue],
    )


def user_interaction_from_row(row: RowType) -> UserInteraction:
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


def latest_update_from_row(row: RowType) -> LatestUpdate:
    return LatestUpdate(
        latestUpdateId=row[LatestUpdatesTable.c.latestUpdateId],
        createdDate=row[LatestUpdatesTable.c.createdDate],
        updatedDate=row[LatestUpdatesTable.c.updatedDate],
        key=row[LatestUpdatesTable.c.key],
        name=row[LatestUpdatesTable.c.name],
        date=row[LatestUpdatesTable.c.date],
    )


def token_listing_from_row(row: RowType, table: Optional[Table] = None) -> TokenListing:
    table = table if table is not None else LatestTokenListingsTable
    return TokenListing(
        tokenListingId=row[table.c.latestTokenListingId],
        createdDate=row[table.c.createdDate],
        updatedDate=row[table.c.updatedDate],
        registryAddress=row[table.c.registryAddress],
        tokenId=row[table.c.tokenId],
        offererAddress=row[table.c.offererAddress],
        startDate=row[table.c.startDate],
        endDate=row[table.c.endDate],
        isValueNative=row[table.c.isValueNative],
        value=row[table.c.value],
        source=row[table.c.source],
        sourceId=row[table.c.sourceId],
    )


def token_attribute_from_row(row: RowType) -> TokenAttribute:
    return TokenAttribute(
        tokenAttributeId=row[TokenAttributesTable.c.tokenAttributeId],
        createdDate=row[TokenAttributesTable.c.createdDate],
        updatedDate=row[TokenAttributesTable.c.updatedDate],
        registryAddress=row[TokenAttributesTable.c.registryAddress],
        tokenId=row[TokenAttributesTable.c.tokenId],
        name=row[TokenAttributesTable.c.name],
        value=row[TokenAttributesTable.c.value],
    )


def token_customization_from_row(row: RowType) -> TokenCustomization:
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


def lock_from_row(row: RowType) -> Lock:
    return Lock(
        lockId=row[LocksTable.c.lockId],
        createdDate=row[LocksTable.c.createdDate],
        updatedDate=row[LocksTable.c.updatedDate],
        name=row[LocksTable.c.name],
        expiryDate=row[LocksTable.c.expiryDate],
    )


def user_profile_from_row(row: RowType) -> UserProfile:
    return UserProfile(
        userProfileId=row[UserProfilesTable.c.userProfileId],
        createdDate=row[UserProfilesTable.c.createdDate],
        updatedDate=row[UserProfilesTable.c.updatedDate],
        address=row[UserProfilesTable.c.address],
        twitterId=row[UserProfilesTable.c.twitterId],
        discordId=row[UserProfilesTable.c.discordId],
        signature=Signature.from_dict(signatureDict=row[UserProfilesTable.c.signature]),
    )


def twitter_credential_from_row(row: RowType) -> TwitterCredential:
    return TwitterCredential(
        twitterCredentialId=row[TwitterCredentialsTable.c.twitterCredentialId],
        createdDate=row[TwitterCredentialsTable.c.createdDate],
        updatedDate=row[TwitterCredentialsTable.c.updatedDate],
        twitterId=row[TwitterCredentialsTable.c.twitterId],
        accessToken=row[TwitterCredentialsTable.c.accessToken],
        refreshToken=row[TwitterCredentialsTable.c.refreshToken],
        expiryDate=row[TwitterCredentialsTable.c.expiryDate],
    )


def twitter_profile_from_row(row: RowType) -> TwitterProfile:
    return TwitterProfile(
        twitterProfileId=row[TwitterProfilesTable.c.twitterProfileId],
        createdDate=row[TwitterProfilesTable.c.createdDate],
        updatedDate=row[TwitterProfilesTable.c.updatedDate],
        twitterId=row[TwitterProfilesTable.c.twitterId],
        username=row[TwitterProfilesTable.c.username],
        name=row[TwitterProfilesTable.c.name],
        description=row[TwitterProfilesTable.c.description],
        isVerified=row[TwitterProfilesTable.c.isVerified],
        pinnedTweetId=row[TwitterProfilesTable.c.pinnedTweetId],
        followerCount=row[TwitterProfilesTable.c.followerCount],
        followingCount=row[TwitterProfilesTable.c.followingCount],
        tweetCount=row[TwitterProfilesTable.c.tweetCount],
    )


def account_gm_from_row(row: RowType) -> AccountGm:
    return AccountGm(
        accountGmId=row[AccountGmsTable.c.accountGmId],
        createdDate=row[AccountGmsTable.c.createdDate],
        updatedDate=row[AccountGmsTable.c.updatedDate],
        address=row[AccountGmsTable.c.address],
        date=row[AccountGmsTable.c.date],
        streakLength=row[AccountGmsTable.c.streakLength],
        collectionCount=row[AccountGmsTable.c.collectionCount],
        signatureMessage=row[AccountGmsTable.c.signatureMessage],
        signature=row[AccountGmsTable.c.signature],
    )


def account_collection_gm_from_row(row: RowType) -> AccountCollectionGm:
    return AccountCollectionGm(
        accountCollectionGmId=row[AccountCollectionGmsTable.c.accountCollectionGmId],
        createdDate=row[AccountCollectionGmsTable.c.createdDate],
        updatedDate=row[AccountCollectionGmsTable.c.updatedDate],
        registryAddress=row[AccountCollectionGmsTable.c.registryAddress],
        accountAddress=row[AccountCollectionGmsTable.c.accountAddress],
        date=row[AccountCollectionGmsTable.c.date],
        signatureMessage=row[AccountCollectionGmsTable.c.signatureMessage],
        signature=row[AccountCollectionGmsTable.c.signature],
    )


def collection_overlap_from_row(row: RowType) -> CollectionOverlap:
    return CollectionOverlap(
        collectionOverlapId=row[TokenCollectionOverlapsTable.c.collectionOverlapId],
        createdDate=row[TokenCollectionOverlapsTable.c.createdDate],
        updatedDate=row[TokenCollectionOverlapsTable.c.updatedDate],
        registryAddress=row[TokenCollectionOverlapsTable.c.registryAddress],
        otherRegistryAddress=row[TokenCollectionOverlapsTable.c.otherRegistryAddress],
        ownerAddress=row[TokenCollectionOverlapsTable.c.ownerAddress],
        registryTokenCount=row[TokenCollectionOverlapsTable.c.registryTokenCount],
        otherRegistryTokenCount=row[TokenCollectionOverlapsTable.c.otherRegistryTokenCount],
    )


def gallery_badge_holder_from_row(row: RowType) -> GalleryBadgeHolder:
    return GalleryBadgeHolder(
        galleryBadgeHolderId=row[GalleryBadgeHoldersTable.c.galleryBadgeHolderId],
        createdDate=row[GalleryBadgeHoldersTable.c.createdDate],
        updatedDate=row[GalleryBadgeHoldersTable.c.updatedDate],
        registryAddress=row[GalleryBadgeHoldersTable.c.registryAddress],
        ownerAddress=row[GalleryBadgeHoldersTable.c.ownerAddress],
        badgeKey=row[GalleryBadgeHoldersTable.c.badgeKey],
        achievedDate=row[GalleryBadgeHoldersTable.c.achievedDate],
    )
