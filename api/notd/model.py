import datetime
from typing import Dict
from typing import List
from typing import Optional

from core.util import date_util
from core.util.typing_util import JSON
from pydantic import dataclasses

COLLECTION_SPRITE_CLUB_ADDRESS = '0x2744fE5e7776BCA0AF1CDEAF3bA3d1F5cae515d3'
COLLECTION_GOBLINTOWN_ADDRESS = '0xbCe3781ae7Ca1a5e050Bd9C4c77369867eBc307e'
COLLECTION_MDTP_ADDRESS = '0x8e720F90014fA4De02627f4A4e217B7e3942d5e8'

GALLERY_COLLECTIONS = {
    COLLECTION_SPRITE_CLUB_ADDRESS,
    COLLECTION_GOBLINTOWN_ADDRESS,
    COLLECTION_MDTP_ADDRESS,
}


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
    operatorAddress: Optional[str]
    contractAddress: Optional[str]
    amount: Optional[int]
    value: int
    gasLimit: int
    gasPrice: int
    blockNumber: int
    tokenType: Optional[str]
    # TODO(Femi-Ogunkola): Make non-optional w=once db is backfilled
    isMultiAddress: Optional[bool]
    isInterstitial: Optional[bool]
    isSwap: Optional[bool]
    isBatch: Optional[bool]
    isOutbound: Optional[bool]


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

    def to_dict(self) -> Dict:
        return {
            'registryAddress': self.registryAddress,
            'tokenId': self.tokenId,
        }

    @classmethod
    def from_dict(cls, tokenDict: Dict):
        return cls(registryAddress=tokenDict['registryAddress'], tokenId=tokenDict['tokenId'])


@dataclasses.dataclass
class BaseSponsoredToken:
    date: datetime.datetime
    token: Token

    def to_dict(self) -> Dict:
        return {
            'date': date_util.datetime_to_string(dt=self.date),
            'token': self.token.to_dict(),
        }

    @classmethod
    def from_dict(cls, sponsoredTokenDict: Dict):
        return cls(
            date=date_util.datetime_from_string(sponsoredTokenDict.get('date')),
            token=Token.from_dict(sponsoredTokenDict.get('token'))
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
class GalleryToken:
    tokenMetadata: TokenMetadata
    tokenCustomization: Optional[TokenCustomization]
    tokenListing: Optional[TokenListing]


@dataclasses.dataclass
class Lock:
    lockId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    name: str
    expiryDate: datetime.datetime
