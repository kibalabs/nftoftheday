from typing import Optional

from sqlalchemy import Table
from sqlalchemy.engine import RowMapping

from notd.model import AccountCollectionGm
from notd.model import AccountGm
from notd.model import Block
from notd.model import Collection
from notd.model import CollectionHourlyActivity
from notd.model import CollectionOverlap
from notd.model import CollectionTotalActivity
from notd.model import GalleryBadgeAssignment
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
from notd.model import TokenStaking
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
from notd.store.schema import GalleryBadgeAssignmentsTable
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
from notd.store.schema import TokenStakingsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import TwitterCredentialsTable
from notd.store.schema import TwitterProfilesTable
from notd.store.schema import UserInteractionsTable
from notd.store.schema import UserProfilesTable


def token_transfer_from_row(rowMapping: RowMapping) -> TokenTransfer:
    return TokenTransfer(
        tokenTransferId=rowMapping[TokenTransfersTable.c.tokenTransferId],
        transactionHash=rowMapping[TokenTransfersTable.c.transactionHash],
        registryAddress=rowMapping[TokenTransfersTable.c.registryAddress],
        tokenId=rowMapping[TokenTransfersTable.c.tokenId],
        fromAddress=rowMapping[TokenTransfersTable.c.fromAddress],
        toAddress=rowMapping[TokenTransfersTable.c.toAddress],
        operatorAddress=rowMapping[TokenTransfersTable.c.operatorAddress],
        contractAddress=rowMapping[TokenTransfersTable.c.contractAddress],
        value=rowMapping[TokenTransfersTable.c.value],
        amount=rowMapping[TokenTransfersTable.c.amount],
        gasLimit=rowMapping[TokenTransfersTable.c.gasLimit],
        gasPrice=rowMapping[TokenTransfersTable.c.gasPrice],
        blockNumber=rowMapping[TokenTransfersTable.c.blockNumber],
        tokenType=rowMapping[TokenTransfersTable.c.tokenType],
        isMultiAddress=rowMapping[TokenTransfersTable.c.isMultiAddress],
        isInterstitial=rowMapping[TokenTransfersTable.c.isInterstitial],
        isSwap=rowMapping[TokenTransfersTable.c.isSwap],
        isBatch=rowMapping[TokenTransfersTable.c.isBatch],
        isOutbound=rowMapping[TokenTransfersTable.c.isOutbound],
        blockDate=rowMapping[BlocksTable.c.blockDate],
        updatedDate=rowMapping[BlocksTable.c.updatedDate],
    )


def block_from_row(rowMapping: RowMapping) -> Block:
    return Block(
        blockId=rowMapping[BlocksTable.c.blockId],
        createdDate=rowMapping[BlocksTable.c.createdDate],
        updatedDate=rowMapping[BlocksTable.c.updatedDate],
        blockNumber=rowMapping[BlocksTable.c.blockNumber],
        blockHash=rowMapping[BlocksTable.c.blockHash],
        blockDate=rowMapping[BlocksTable.c.blockDate],
    )


def token_metadata_from_row(rowMapping: RowMapping) -> TokenMetadata:
    return TokenMetadata(
        tokenMetadataId=rowMapping[TokenMetadatasTable.c.tokenMetadataId],
        createdDate=rowMapping[TokenMetadatasTable.c.createdDate],
        updatedDate=rowMapping[TokenMetadatasTable.c.updatedDate],
        registryAddress=rowMapping[TokenMetadatasTable.c.registryAddress],
        tokenId=rowMapping[TokenMetadatasTable.c.tokenId],
        metadataUrl=rowMapping[TokenMetadatasTable.c.metadataUrl],
        name=rowMapping[TokenMetadatasTable.c.name],
        imageUrl=rowMapping[TokenMetadatasTable.c.imageUrl],
        resizableImageUrl=rowMapping[TokenMetadatasTable.c.resizableImageUrl],
        animationUrl=rowMapping[TokenMetadatasTable.c.animationUrl],
        youtubeUrl=rowMapping[TokenMetadatasTable.c.youtubeUrl],
        backgroundColor=rowMapping[TokenMetadatasTable.c.backgroundColor],
        frameImageUrl=rowMapping[TokenMetadatasTable.c.frameImageUrl],
        description=rowMapping[TokenMetadatasTable.c.description],
        attributes=rowMapping[TokenMetadatasTable.c.attributes],
    )


def collection_from_row(rowMapping: RowMapping) -> Collection:
    return Collection(
        collectionId=rowMapping[TokenCollectionsTable.c.collectionId],
        createdDate=rowMapping[TokenCollectionsTable.c.createdDate],
        updatedDate=rowMapping[TokenCollectionsTable.c.updatedDate],
        address=rowMapping[TokenCollectionsTable.c.address],
        name=rowMapping[TokenCollectionsTable.c.name],
        symbol=rowMapping[TokenCollectionsTable.c.symbol],
        description=rowMapping[TokenCollectionsTable.c.description],
        imageUrl=rowMapping[TokenCollectionsTable.c.imageUrl],
        twitterUsername=rowMapping[TokenCollectionsTable.c.twitterUsername],
        instagramUsername=rowMapping[TokenCollectionsTable.c.instagramUsername],
        wikiUrl=rowMapping[TokenCollectionsTable.c.wikiUrl],
        openseaSlug=rowMapping[TokenCollectionsTable.c.openseaSlug],
        url=rowMapping[TokenCollectionsTable.c.url],
        discordUrl=rowMapping[TokenCollectionsTable.c.discordUrl],
        bannerImageUrl=rowMapping[TokenCollectionsTable.c.bannerImageUrl],
        doesSupportErc721=rowMapping[TokenCollectionsTable.c.doesSupportErc721],
        doesSupportErc1155=rowMapping[TokenCollectionsTable.c.doesSupportErc1155],
    )


def token_ownership_from_row(rowMapping: RowMapping) -> TokenOwnership:
    return TokenOwnership(
        tokenOwnershipId=rowMapping[TokenOwnershipsTable.c.tokenOwnershipId],
        createdDate=rowMapping[TokenOwnershipsTable.c.createdDate],
        updatedDate=rowMapping[TokenOwnershipsTable.c.updatedDate],
        registryAddress=rowMapping[TokenOwnershipsTable.c.registryAddress],
        tokenId=rowMapping[TokenOwnershipsTable.c.tokenId],
        ownerAddress=rowMapping[TokenOwnershipsTable.c.ownerAddress],
        transferValue=rowMapping[TokenOwnershipsTable.c.transferValue],
        transferDate=rowMapping[TokenOwnershipsTable.c.transferDate],
        transferTransactionHash=rowMapping[TokenOwnershipsTable.c.transferTransactionHash],
    )


def token_multi_ownership_from_row(rowMapping: RowMapping) -> TokenMultiOwnership:
    return TokenMultiOwnership(
        tokenMultiOwnershipId=rowMapping[TokenMultiOwnershipsTable.c.tokenMultiOwnershipId.name] if TokenMultiOwnershipsTable.c.tokenMultiOwnershipId.name in rowMapping else -1,
        createdDate=rowMapping[TokenMultiOwnershipsTable.c.createdDate.name],
        updatedDate=rowMapping[TokenMultiOwnershipsTable.c.updatedDate.name],
        registryAddress=rowMapping[TokenMultiOwnershipsTable.c.registryAddress.name],
        tokenId=rowMapping[TokenMultiOwnershipsTable.c.tokenId.name],
        ownerAddress=rowMapping[TokenMultiOwnershipsTable.c.ownerAddress.name],
        quantity=rowMapping[TokenMultiOwnershipsTable.c.quantity.name],
        averageTransferValue=rowMapping[TokenMultiOwnershipsTable.c.averageTransferValue.name],
        latestTransferDate=rowMapping[TokenMultiOwnershipsTable.c.latestTransferDate.name],
        latestTransferTransactionHash=rowMapping[TokenMultiOwnershipsTable.c.latestTransferTransactionHash.name],
    )


def collection_activity_from_row(rowMapping: RowMapping) -> CollectionHourlyActivity:
    return CollectionHourlyActivity(
        collectionActivityId=rowMapping[CollectionHourlyActivitiesTable.c.collectionActivityId],
        createdDate=rowMapping[CollectionHourlyActivitiesTable.c.createdDate],
        updatedDate=rowMapping[CollectionHourlyActivitiesTable.c.updatedDate],
        address=rowMapping[CollectionHourlyActivitiesTable.c.address],
        date=rowMapping[CollectionHourlyActivitiesTable.c.date],
        transferCount=rowMapping[CollectionHourlyActivitiesTable.c.transferCount],
        saleCount=rowMapping[CollectionHourlyActivitiesTable.c.saleCount],
        totalValue=rowMapping[CollectionHourlyActivitiesTable.c.totalValue],
        minimumValue=rowMapping[CollectionHourlyActivitiesTable.c.minimumValue],
        maximumValue=rowMapping[CollectionHourlyActivitiesTable.c.maximumValue],
        averageValue=rowMapping[CollectionHourlyActivitiesTable.c.averageValue],
    )


def collection_total_activity_from_row(rowMapping: RowMapping) -> CollectionTotalActivity:
    return CollectionTotalActivity(
        collectionTotalActivityId=rowMapping[CollectionTotalActivitiesTable.c.collectionTotalActivityId],
        createdDate=rowMapping[CollectionTotalActivitiesTable.c.createdDate],
        updatedDate=rowMapping[CollectionTotalActivitiesTable.c.updatedDate],
        address=rowMapping[CollectionTotalActivitiesTable.c.address],
        transferCount=rowMapping[CollectionTotalActivitiesTable.c.transferCount],
        saleCount=rowMapping[CollectionTotalActivitiesTable.c.saleCount],
        totalValue=rowMapping[CollectionTotalActivitiesTable.c.totalValue],
        minimumValue=rowMapping[CollectionTotalActivitiesTable.c.minimumValue],
        maximumValue=rowMapping[CollectionTotalActivitiesTable.c.maximumValue],
        averageValue=rowMapping[CollectionTotalActivitiesTable.c.averageValue],
    )


def user_interaction_from_row(rowMapping: RowMapping) -> UserInteraction:
    return UserInteraction(
        userInteractionId=rowMapping[UserInteractionsTable.c.userInteractionId],
        createdDate=rowMapping[UserInteractionsTable.c.createdDate],
        updatedDate=rowMapping[UserInteractionsTable.c.updatedDate],
        date=rowMapping[UserInteractionsTable.c.date],
        userAddress=rowMapping[UserInteractionsTable.c.userAddress],
        command=rowMapping[UserInteractionsTable.c.command],
        signature=rowMapping[UserInteractionsTable.c.signature],
        message=rowMapping[UserInteractionsTable.c.message],
    )


def latest_update_from_row(rowMapping: RowMapping) -> LatestUpdate:
    return LatestUpdate(
        latestUpdateId=rowMapping[LatestUpdatesTable.c.latestUpdateId],
        createdDate=rowMapping[LatestUpdatesTable.c.createdDate],
        updatedDate=rowMapping[LatestUpdatesTable.c.updatedDate],
        key=rowMapping[LatestUpdatesTable.c.key],
        name=rowMapping[LatestUpdatesTable.c.name],
        date=rowMapping[LatestUpdatesTable.c.date],
    )


def token_listing_from_row(rowMapping: RowMapping, table: Optional[Table] = None) -> TokenListing:
    table = table if table is not None else LatestTokenListingsTable
    return TokenListing(
        tokenListingId=rowMapping[table.c.latestTokenListingId],
        createdDate=rowMapping[table.c.createdDate],
        updatedDate=rowMapping[table.c.updatedDate],
        registryAddress=rowMapping[table.c.registryAddress],
        tokenId=rowMapping[table.c.tokenId],
        offererAddress=rowMapping[table.c.offererAddress],
        startDate=rowMapping[table.c.startDate],
        endDate=rowMapping[table.c.endDate],
        isValueNative=rowMapping[table.c.isValueNative],
        value=rowMapping[table.c.value],
        source=rowMapping[table.c.source],
        sourceId=rowMapping[table.c.sourceId],
    )


def token_attribute_from_row(rowMapping: RowMapping) -> TokenAttribute:
    return TokenAttribute(
        tokenAttributeId=rowMapping[TokenAttributesTable.c.tokenAttributeId],
        createdDate=rowMapping[TokenAttributesTable.c.createdDate],
        updatedDate=rowMapping[TokenAttributesTable.c.updatedDate],
        registryAddress=rowMapping[TokenAttributesTable.c.registryAddress],
        tokenId=rowMapping[TokenAttributesTable.c.tokenId],
        name=rowMapping[TokenAttributesTable.c.name],
        value=rowMapping[TokenAttributesTable.c.value],
    )


def token_customization_from_row(rowMapping: RowMapping) -> TokenCustomization:
    return TokenCustomization(
        tokenCustomizationId=rowMapping[TokenCustomizationsTable.c.tokenCustomizationId],
        createdDate=rowMapping[TokenCustomizationsTable.c.createdDate],
        updatedDate=rowMapping[TokenCustomizationsTable.c.updatedDate],
        registryAddress=rowMapping[TokenCustomizationsTable.c.registryAddress],
        tokenId=rowMapping[TokenCustomizationsTable.c.tokenId],
        creatorAddress=rowMapping[TokenCustomizationsTable.c.creatorAddress],
        signature=rowMapping[TokenCustomizationsTable.c.signature],
        blockNumber=rowMapping[TokenCustomizationsTable.c.blockNumber],
        name=rowMapping[TokenCustomizationsTable.c.name],
        description=rowMapping[TokenCustomizationsTable.c.description],
    )


def lock_from_row(rowMapping: RowMapping) -> Lock:
    return Lock(
        lockId=rowMapping[LocksTable.c.lockId],
        createdDate=rowMapping[LocksTable.c.createdDate],
        updatedDate=rowMapping[LocksTable.c.updatedDate],
        name=rowMapping[LocksTable.c.name],
        expiryDate=rowMapping[LocksTable.c.expiryDate],
    )


def user_profile_from_row(rowMapping: RowMapping) -> UserProfile:
    return UserProfile(
        userProfileId=rowMapping[UserProfilesTable.c.userProfileId],
        createdDate=rowMapping[UserProfilesTable.c.createdDate],
        updatedDate=rowMapping[UserProfilesTable.c.updatedDate],
        address=rowMapping[UserProfilesTable.c.address],
        twitterId=rowMapping[UserProfilesTable.c.twitterId],
        discordId=rowMapping[UserProfilesTable.c.discordId],
        signature=Signature.from_dict(signatureDict=rowMapping[UserProfilesTable.c.signature]),
    )


def twitter_credential_from_row(rowMapping: RowMapping) -> TwitterCredential:
    return TwitterCredential(
        twitterCredentialId=rowMapping[TwitterCredentialsTable.c.twitterCredentialId],
        createdDate=rowMapping[TwitterCredentialsTable.c.createdDate],
        updatedDate=rowMapping[TwitterCredentialsTable.c.updatedDate],
        twitterId=rowMapping[TwitterCredentialsTable.c.twitterId],
        accessToken=rowMapping[TwitterCredentialsTable.c.accessToken],
        refreshToken=rowMapping[TwitterCredentialsTable.c.refreshToken],
        expiryDate=rowMapping[TwitterCredentialsTable.c.expiryDate],
    )


def twitter_profile_from_row(rowMapping: RowMapping) -> TwitterProfile:
    return TwitterProfile(
        twitterProfileId=rowMapping[TwitterProfilesTable.c.twitterProfileId],
        createdDate=rowMapping[TwitterProfilesTable.c.createdDate],
        updatedDate=rowMapping[TwitterProfilesTable.c.updatedDate],
        twitterId=rowMapping[TwitterProfilesTable.c.twitterId],
        username=rowMapping[TwitterProfilesTable.c.username],
        name=rowMapping[TwitterProfilesTable.c.name],
        description=rowMapping[TwitterProfilesTable.c.description],
        isVerified=rowMapping[TwitterProfilesTable.c.isVerified],
        pinnedTweetId=rowMapping[TwitterProfilesTable.c.pinnedTweetId],
        followerCount=rowMapping[TwitterProfilesTable.c.followerCount],
        followingCount=rowMapping[TwitterProfilesTable.c.followingCount],
        tweetCount=rowMapping[TwitterProfilesTable.c.tweetCount],
    )


def account_gm_from_row(rowMapping: RowMapping) -> AccountGm:
    return AccountGm(
        accountGmId=rowMapping[AccountGmsTable.c.accountGmId],
        createdDate=rowMapping[AccountGmsTable.c.createdDate],
        updatedDate=rowMapping[AccountGmsTable.c.updatedDate],
        address=rowMapping[AccountGmsTable.c.address],
        delegateAddress=rowMapping[AccountGmsTable.c.delegateAddress],
        date=rowMapping[AccountGmsTable.c.date],
        streakLength=rowMapping[AccountGmsTable.c.streakLength],
        collectionCount=rowMapping[AccountGmsTable.c.collectionCount],
        signatureMessage=rowMapping[AccountGmsTable.c.signatureMessage],
        signature=rowMapping[AccountGmsTable.c.signature],
    )


def account_collection_gm_from_row(rowMapping: RowMapping) -> AccountCollectionGm:
    return AccountCollectionGm(
        accountCollectionGmId=rowMapping[AccountCollectionGmsTable.c.accountCollectionGmId],
        createdDate=rowMapping[AccountCollectionGmsTable.c.createdDate],
        updatedDate=rowMapping[AccountCollectionGmsTable.c.updatedDate],
        registryAddress=rowMapping[AccountCollectionGmsTable.c.registryAddress],
        accountAddress=rowMapping[AccountCollectionGmsTable.c.accountAddress],
        accountDelegateAddress=rowMapping[AccountCollectionGmsTable.c.accountDelegateAddress],
        date=rowMapping[AccountCollectionGmsTable.c.date],
        signatureMessage=rowMapping[AccountCollectionGmsTable.c.signatureMessage],
        signature=rowMapping[AccountCollectionGmsTable.c.signature],
    )


def collection_overlap_from_row(rowMapping: RowMapping) -> CollectionOverlap:
    return CollectionOverlap(
        collectionOverlapId=rowMapping[TokenCollectionOverlapsTable.c.collectionOverlapId],
        createdDate=rowMapping[TokenCollectionOverlapsTable.c.createdDate],
        updatedDate=rowMapping[TokenCollectionOverlapsTable.c.updatedDate],
        registryAddress=rowMapping[TokenCollectionOverlapsTable.c.registryAddress],
        otherRegistryAddress=rowMapping[TokenCollectionOverlapsTable.c.otherRegistryAddress],
        ownerAddress=rowMapping[TokenCollectionOverlapsTable.c.ownerAddress],
        registryTokenCount=rowMapping[TokenCollectionOverlapsTable.c.registryTokenCount],
        otherRegistryTokenCount=rowMapping[TokenCollectionOverlapsTable.c.otherRegistryTokenCount],
    )


def gallery_badge_holder_from_row(rowMapping: RowMapping) -> GalleryBadgeHolder:
    return GalleryBadgeHolder(
        # NOTE(krishan711): update this
        galleryBadgeHolderId=rowMapping['id'],
        createdDate=rowMapping['createdDate'],
        updatedDate=rowMapping['updatedDate'],
        registryAddress=rowMapping['registryAddress'],
        ownerAddress=rowMapping['ownerAddress'],
        badgeKey=rowMapping['badgeKey'],
        achievedDate=rowMapping['achievedDate'],
    )


def gallery_badge_assignment_from_row(rowMapping: RowMapping) -> GalleryBadgeAssignment:
    return GalleryBadgeAssignment(
        galleryBadgeAssignmentId=rowMapping[GalleryBadgeAssignmentsTable.c.galleryBadgeAssignmentId],
        createdDate=rowMapping[GalleryBadgeAssignmentsTable.c.createdDate],
        updatedDate=rowMapping[GalleryBadgeAssignmentsTable.c.updatedDate],
        registryAddress=rowMapping[GalleryBadgeAssignmentsTable.c.registryAddress],
        ownerAddress=rowMapping[GalleryBadgeAssignmentsTable.c.ownerAddress],
        badgeKey=rowMapping[GalleryBadgeAssignmentsTable.c.badgeKey],
        achievedDate=rowMapping[GalleryBadgeAssignmentsTable.c.achievedDate],
        assignerAddress=rowMapping[GalleryBadgeAssignmentsTable.c.assignerAddress],
        signatureMessage=rowMapping[GalleryBadgeAssignmentsTable.c.signatureMessage],
        signature=rowMapping[GalleryBadgeAssignmentsTable.c.signature],
    )


def token_staking_from_row(rowMapping: RowMapping) -> TokenStaking:
    return TokenStaking(
        tokenStakingId=rowMapping[TokenStakingsTable.c.tokenStakingId],
        createdDate=rowMapping[TokenStakingsTable.c.createdDate],
        updatedDate=rowMapping[TokenStakingsTable.c.updatedDate],
        stakingAddress=rowMapping[TokenStakingsTable.c.stakingAddress],
        ownerAddress=rowMapping[TokenStakingsTable.c.ownerAddress],
        registryAddress=rowMapping[TokenStakingsTable.c.registryAddress],
        tokenId=rowMapping[TokenStakingsTable.c.tokenId],
        stakingDate=rowMapping[TokenStakingsTable.c.stakingDate],
    )
