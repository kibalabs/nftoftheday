from __future__ import annotations

import dataclasses
import datetime
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from core.util import date_util
from core.util.typing_util import JSON

WRAPPED_ETHER_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

COLLECTION_SPRITE_CLUB_ADDRESS = '0x2744fE5e7776BCA0AF1CDEAF3bA3d1F5cae515d3'
COLLECTION_GOBLINTOWN_ADDRESS = '0xbCe3781ae7Ca1a5e050Bd9C4c77369867eBc307e'
COLLECTION_MDTP_ADDRESS = '0x8e720F90014fA4De02627f4A4e217B7e3942d5e8'
COLLECTION_RUDEBOYS_ADDRESS = '0x5351105753Bdbc3Baa908A0c04F1468535749c3D'
COLLECTION_CREEPZ_ADDRESS = '0xfE8C6d19365453D26af321D0e8c910428c23873F'
COLLECTION_CREEPZ_SHAPESHIFTER_ADDRESS = '0xF1083e064F92db0561fd540F982Cbf73A4e2F8f6'
COLLECTION_CREEPZ_MEGA_SHAPESHIFTER_ADDRESS = '0xD6D80461b1875A8679Fe789db689156F42B7f86B'
COLLECTION_CREEPZ_ARMOURIES_ADDRESS = '0x5f4a54E29ccb8a02CDF7D7BFa8a0999A8330CCeD'
COLLECTION_CREEPZ_VAULTS_ADDRESS = '0xA63673Fd80E67aaeAb5489C61760a490476a748a'

OPENSEA_SEAPORT_11_ADDRESS = '0x00000000006c3852cbEf3e08E8dF289169EdE581'
OPENSEA_SEAPORT_12_ADDRESS = '0x00000000000006c7676171937C444f6BDe3D6282'
OPENSEA_SEAPORT_13_ADDRESS = '0x0000000000000aD24e80fd803C6ac37206a45f15'
OPENSEA_SEAPORT_14_ADDRESS = '0x00000000000001ad428e4906aE43D8F9852d0dD6'
OPENSEA_WYVERN_1_ADDRESS = '0x7Be8076f4EA4A4AD08075C2508e481d6C946D12b'
OPENSEA_WYVERN_2_ADDRESS = '0x7f268357A8c2552623316e2562D90e642bB538E5'
LOOKSRARE_MARKETPLACE_ADDRESS = '0x59728544B08AB483533076417FbBB2fD0B17CE3a'
BLUR_2_ADDRESS = '0x39da41747a83aeE658334415666f3EF92DD0D541'

CREEPZ_STAKING_ADDRESS = '0xC3503192343EAE4B435E4A1211C5d28BF6f6a696'

MARKETPLACE_ADDRESSES = {
    OPENSEA_SEAPORT_11_ADDRESS,
    OPENSEA_SEAPORT_12_ADDRESS,
    OPENSEA_SEAPORT_13_ADDRESS,
    OPENSEA_SEAPORT_14_ADDRESS,
    OPENSEA_WYVERN_1_ADDRESS,
    OPENSEA_WYVERN_2_ADDRESS,
    LOOKSRARE_MARKETPLACE_ADDRESS,
    BLUR_2_ADDRESS,
}

GALLERY_COLLECTIONS = {
    COLLECTION_SPRITE_CLUB_ADDRESS,
    COLLECTION_GOBLINTOWN_ADDRESS,
    COLLECTION_MDTP_ADDRESS,
    COLLECTION_RUDEBOYS_ADDRESS,
    COLLECTION_CREEPZ_ADDRESS,
    COLLECTION_CREEPZ_SHAPESHIFTER_ADDRESS,
    COLLECTION_CREEPZ_MEGA_SHAPESHIFTER_ADDRESS,
    COLLECTION_CREEPZ_ARMOURIES_ADDRESS,
    COLLECTION_CREEPZ_VAULTS_ADDRESS,
}

GALLERY_COLLECTION_ADMINS = {
    COLLECTION_RUDEBOYS_ADDRESS: [
        '0xCE11D6fb4f1e006E5a348230449Dc387fde850CC',
    ],
}

STAKING_ADDRESSES = [
    CREEPZ_STAKING_ADDRESS,
]

SUPER_COLLECTIONS = {
    'creepz': [
        COLLECTION_CREEPZ_ADDRESS,
        COLLECTION_CREEPZ_SHAPESHIFTER_ADDRESS,
        COLLECTION_CREEPZ_MEGA_SHAPESHIFTER_ADDRESS,
        COLLECTION_CREEPZ_ARMOURIES_ADDRESS,
        COLLECTION_CREEPZ_VAULTS_ADDRESS,
    ],
}

ListResponseItemType = TypeVar("ListResponseItemType") # pylint: disable=invalid-name


@dataclasses.dataclass
class ListResponse(Generic[ListResponseItemType]):
    items: List[ListResponseItemType]
    totalCount: int



@dataclasses.dataclass
class RetrievedCollection:
    address: str
    name: Optional[str]
    symbol: Optional[str]
    description: Optional[str]
    imageUrl: Optional[str]
    twitterUsername: Optional[str]
    instagramUsername: Optional[str]
    wikiUrl: Optional[str]
    openseaSlug: Optional[str]
    url: Optional[str]
    discordUrl: Optional[str]
    bannerImageUrl: Optional[str]
    doesSupportErc721: bool
    doesSupportErc1155: bool


@dataclasses.dataclass
class Collection(RetrievedCollection):
    collectionId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class RetrievedTokenMetadata:
    registryAddress: str
    tokenId: str
    metadataUrl: Optional[str]
    name: Optional[str]
    description: Optional[str]
    imageUrl: Optional[str]
    resizableImageUrl: Optional[str]
    animationUrl: Optional[str]
    youtubeUrl: Optional[str]
    backgroundColor: Optional[str]
    frameImageUrl: Optional[str]
    attributes: JSON


@dataclasses.dataclass
class TokenMetadata(RetrievedTokenMetadata):
    tokenMetadataId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass(unsafe_hash=True)
class RetrievedTokenTransfer:
    transactionHash: str
    registryAddress: str
    tokenId: str
    fromAddress: str
    toAddress: str
    operatorAddress: str
    contractAddress: str
    amount: int
    value: int
    gasLimit: int
    gasPrice: int
    blockNumber: int
    tokenType: str
    isMultiAddress: bool
    isInterstitial: bool
    isSwap: bool
    isBatch: bool
    isOutbound: bool


@dataclasses.dataclass(unsafe_hash=True)
class TokenTransfer(RetrievedTokenTransfer):
    tokenTransferId: int
    blockDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class TradedToken:
    latestTransfer: TokenTransfer
    transferCount: int


@dataclasses.dataclass
class Token:
    registryAddress: str
    tokenId: str

    def to_dict(self) -> JSON:
        return {
            'registryAddress': self.registryAddress,
            'tokenId': self.tokenId,
        }

    @classmethod
    def from_dict(cls, tokenDict: JSON) -> Token:
        return cls(
            registryAddress=str(tokenDict['registryAddress']),  # type: ignore[index, call-overload]
            tokenId=str(tokenDict['tokenId']),  # type: ignore[index, call-overload]
        )


@dataclasses.dataclass
class AccountToken:
    registryAddress: str
    tokenId: str
    ownerAddress: str


@dataclasses.dataclass
class BaseSponsoredToken:
    date: datetime.datetime
    token: Token

    def to_dict(self) -> JSON:
        return {
            'date': date_util.datetime_to_string(dt=self.date),
            'token': self.token.to_dict(),  # type: ignore[dict-item]
        }

    @classmethod
    def from_dict(cls, sponsoredTokenDict: JSON) -> BaseSponsoredToken:
        return cls(
            date=date_util.datetime_from_string(str(sponsoredTokenDict['date'])),  # type: ignore[index, call-overload]
            token=Token.from_dict(dict(sponsoredTokenDict['token']))  # type: ignore[index, call-overload, arg-type]
        )


@dataclasses.dataclass
class SponsoredToken(BaseSponsoredToken):
    latestTransfer: Optional[TokenTransfer]


@dataclasses.dataclass
class Block:
    blockId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    blockNumber: int
    blockHash: str
    blockDate: datetime.datetime


@dataclasses.dataclass
class ProcessedBlock:
    blockNumber: int
    blockHash: str
    blockDate: datetime.datetime
    retrievedTokenTransfers: List[RetrievedTokenTransfer]


@dataclasses.dataclass
class RetrievedTokenOwnership:
    registryAddress: str
    tokenId: str
    ownerAddress: str
    transferValue: int
    transferDate: datetime.datetime
    transferTransactionHash: str


@dataclasses.dataclass
class TokenOwnership(RetrievedTokenOwnership):
    tokenOwnershipId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class RetrievedTokenMultiOwnership:
    registryAddress: str
    tokenId: str
    ownerAddress: str
    quantity: int
    averageTransferValue: int
    latestTransferDate: datetime.datetime
    latestTransferTransactionHash: str


@dataclasses.dataclass
class TokenMultiOwnership(RetrievedTokenMultiOwnership):
    tokenMultiOwnershipId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class RetrievedCollectionHourlyActivity:
    address: str
    date: datetime.datetime
    transferCount: int
    saleCount: int
    totalValue: int
    minimumValue: int
    maximumValue: int
    averageValue: int


@dataclasses.dataclass
class CollectionHourlyActivity(RetrievedCollectionHourlyActivity):
    collectionActivityId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class CollectionStatistics:
    itemCount: int
    holderCount: int
    saleCount: int
    transferCount: int
    totalTradeVolume: int
    lowestSaleLast24Hours: int
    highestSaleLast24Hours: int
    tradeVolume24Hours: int


@dataclasses.dataclass
class CollectionDailyActivity:
    date: datetime.date
    transferCount: int
    saleCount: int
    totalValue: int
    minimumValue: int
    maximumValue: int
    averageValue: int


@dataclasses.dataclass
class RetrievedCollectionTotalActivity:
    address: str
    transferCount: int
    saleCount: int
    totalValue: int
    minimumValue: int
    maximumValue: int
    averageValue: int


@dataclasses.dataclass
class CollectionTotalActivity(RetrievedCollectionTotalActivity):
    collectionTotalActivityId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class UserInteraction:
    userInteractionId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    date: datetime.datetime
    userAddress: str
    command: str
    signature: str
    message: JSON


@dataclasses.dataclass
class LatestUpdate:
    latestUpdateId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    key: str
    name: Optional[str]
    date: datetime.datetime


@dataclasses.dataclass
class Airdrop:
    tokenKey: Token
    name: str
    isClaimed: bool
    claimTokenKey: Token
    claimUrl: str


@dataclasses.dataclass
class RetrievedTokenListing:
    registryAddress: str
    tokenId: str
    offererAddress: str
    startDate: datetime.datetime
    endDate: datetime.datetime
    isValueNative: bool
    value: int
    source: str
    sourceId: str


@dataclasses.dataclass
class TokenListing(RetrievedTokenListing):
    tokenListingId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class RetrievedTokenAttribute:
    registryAddress: str
    tokenId: str
    name: str
    value: Optional[str]


@dataclasses.dataclass
class TokenAttribute(RetrievedTokenAttribute):
    tokenAttributeId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class CollectionAttribute:
    name: str
    values: List[str]


@dataclasses.dataclass
class SuperCollectionEntry:
    collectionAddress: str
    collectionAttributes: List[CollectionAttribute]


@dataclasses.dataclass
class TokenCustomization:
    tokenCustomizationId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    registryAddress: str
    tokenId: str
    creatorAddress: str
    blockNumber: int
    signature: str
    name: Optional[str]
    description: Optional[str]


@dataclasses.dataclass
class Lock:
    lockId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    name: str
    expiryDate: datetime.datetime


@dataclasses.dataclass
class Signature:
    message: str
    signature: str

    def to_dict(self) -> JSON:
        return {
            'message': self.message,
            'signature': self.signature,
        }

    @classmethod
    def from_dict(cls, signatureDict: JSON) -> Signature:
        return cls(
            message=str(signatureDict['message']),  # type: ignore[index, call-overload]
            signature=str(signatureDict['signature']),  # type: ignore[index, call-overload]
        )


@dataclasses.dataclass
class UserProfile:
    userProfileId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    address: str
    twitterId: Optional[str]
    discordId: Optional[str]
    signature: Signature


@dataclasses.dataclass
class TwitterCredential:
    twitterCredentialId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    twitterId: str
    accessToken: str
    refreshToken: str
    expiryDate: datetime.datetime


@dataclasses.dataclass
class RetrievedTwitterProfile:
    twitterId: str
    username: str
    name: str
    description: str
    isVerified: bool
    pinnedTweetId: Optional[str]
    followerCount: int
    followingCount: int
    tweetCount: int


@dataclasses.dataclass
class TwitterProfile(RetrievedTwitterProfile):
    twitterProfileId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class RetrievedTokenStaking:
    stakingAddress: str
    ownerAddress: str
    registryAddress: str
    tokenId: str
    stakedDate: datetime.datetime
    transactionHash: str


@dataclasses.dataclass
class TokenStaking(RetrievedTokenStaking):
    tokenStakingId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class GalleryToken:
    tokenMetadata: TokenMetadata
    tokenCustomization: Optional[TokenCustomization]
    tokenListing: Optional[TokenListing]
    tokenStaking: Optional[TokenStaking]
    quantity: int


@dataclasses.dataclass
class GalleryUser:
    address: str
    registryAddress: str
    userProfile: Optional[UserProfile]
    twitterProfile: Optional[TwitterProfile]
    joinDate: Optional[datetime.datetime]


@dataclasses.dataclass
class GalleryOwnedCollection:
    collection: Collection
    tokenMetadatas: List[TokenMetadata]


@dataclasses.dataclass
class AccountGm:
    accountGmId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    address: str
    delegateAddress: Optional[str]
    date: datetime.datetime
    streakLength: int
    collectionCount: int
    signatureMessage: str
    signature: str


@dataclasses.dataclass
class AccountCollectionGm:
    accountCollectionGmId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    registryAddress: str
    accountAddress: str
    accountDelegateAddress: Optional[str]
    date: datetime.datetime
    signatureMessage: str
    signature: str


@dataclasses.dataclass
class GmAccountRow:
    address: str
    lastDate: datetime.datetime
    streakLength: int
    weekCount: int
    monthCount: int


@dataclasses.dataclass
class GmCollectionRow:
    collection: Collection
    todayCount: int
    weekCount: int
    monthCount: int


@dataclasses.dataclass
class LatestAccountGm:
    accountGm: AccountGm
    accountCollectionGms: List[AccountCollectionGm]


@dataclasses.dataclass
class RetrievedCollectionOverlap:
    registryAddress: str
    otherRegistryAddress: str
    ownerAddress: str
    registryTokenCount: int
    otherRegistryTokenCount: int


@dataclasses.dataclass
class CollectionOverlap(RetrievedCollectionOverlap):
    collectionOverlapId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class CollectionOverlapSummary:
    registryAddress: str
    otherCollection: Collection
    ownerCount: int
    registryTokenCount: int
    otherRegistryTokenCount: int


@dataclasses.dataclass
class SuperCollectionOverlap:
    ownerAddress: str
    otherRegistryAddress: str
    otherRegistryTokenCount: int
    registryTokenCountMap: Dict[str, int]


@dataclasses.dataclass
class CollectionOverlapOwner:
    registryAddress: str
    otherCollection: Collection
    ownerAddress: str
    registryTokenCount: int
    otherRegistryTokenCount: int


@dataclasses.dataclass
class RetrievedGalleryBadgeHolder:
    registryAddress: str
    ownerAddress: str
    badgeKey: str
    achievedDate: datetime.datetime


@dataclasses.dataclass
class GalleryBadgeHolder(RetrievedGalleryBadgeHolder):
    galleryBadgeHolderId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass
class GalleryBadgeAssignment(RetrievedGalleryBadgeHolder):
    galleryBadgeAssignmentId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    assignerAddress: str
    signatureMessage: str
    signature: str


@dataclasses.dataclass
class GalleryUserRow:
    galleryUser: GalleryUser
    ownedTokenCount: int
    uniqueOwnedTokenCount: int
    chosenOwnedTokens: List[TokenMetadata]
    galleryBadgeHolders: List[GalleryBadgeHolder]


@dataclasses.dataclass
class GallerySuperCollectionUserRow:
    galleryUser: GalleryUser
    ownedTokenCountMap: Dict[str, int]
    uniqueOwnedTokenCountMap: Dict[str, int]
    chosenOwnedTokensMap: Dict[str, List[TokenMetadata]]
    galleryBadgeHolders: List[GalleryBadgeHolder]


@dataclasses.dataclass
class TrendingCollection:
    registryAddress: str
    previousSaleCount: str
    previousTotalVolume: str
    totalVolume: str
    totalSaleCount: str
