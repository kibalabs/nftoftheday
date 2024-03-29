import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel


class ApiCollection(BaseModel):
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


class ApiCollectionToken(BaseModel):
    registryAddress: str
    tokenId: str
    metadataUrl: Optional[str]
    name: Optional[str]
    description: Optional[str]
    imageUrl: Optional[str]
    resizableImageUrl: Optional[str]
    frameImageUrl: Optional[str]
    attributes: Optional[List[Dict[str, Union[str, int, float, None, bool]]]]


class ApiAccountCollectionToken(ApiCollectionToken):
    ownerAddress: str


class ApiTokenTransfer(BaseModel):
    tokenTransferId: int
    transactionHash: str
    registryAddress: str
    fromAddress: str
    toAddress: str
    contractAddress: Optional[str]
    tokenId: str
    value: str
    gasLimit: int
    gasPrice: int
    blockNumber: int
    tokenType: str
    isMultiAddress: bool
    isInterstitial: bool
    isSwap: bool
    isBatch: bool
    isOutbound: bool
    blockDate: datetime.datetime
    collection: ApiCollection
    token: ApiCollectionToken


class ApiTokenTransferValue(BaseModel):
    registryAddress: str
    tokenId: str
    value: str
    blockDate: datetime.datetime


class ApiTokenOwnership(BaseModel):
    registryAddress: str
    tokenId: str
    ownerAddress: str
    quantity: int


class ApiCollectionStatistics(BaseModel):
    itemCount: int
    holderCount: int
    saleCount: int
    transferCount: int
    totalTradeVolume: str
    lowestSaleLast24Hours: str
    highestSaleLast24Hours: str
    tradeVolume24Hours: str


class ApiCollectionDailyActivity(BaseModel):
    date: datetime.date
    transferCount: str
    saleCount: str
    totalValue: str
    minimumValue: str
    maximumValue: str
    averageValue: str


class ApiAirdrop(BaseModel):
    token: ApiCollectionToken
    name: str
    isClaimed: bool
    claimToken: ApiCollectionToken
    claimUrl: str


class ApiCollectionAttribute(BaseModel):
    name: str
    values: List[str]


class ApiSuperCollectionEntry(BaseModel):
    collection: ApiCollection
    collectionAttributes: List[ApiCollectionAttribute]


class ApiTokenCustomization(BaseModel):
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


class ApiTokenListing(BaseModel):
    tokenListingId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    registryAddress: str
    tokenId: str
    offererAddress: str
    startDate: datetime.datetime
    endDate: datetime.datetime
    isValueNative: bool
    value: str
    source: str
    sourceId: str


class ApiTokenStaking(BaseModel):
    stakingAddress: str
    ownerAddress: str
    registryAddress: str
    tokenId: str
    stakedDate: datetime.datetime


class ApiGalleryToken(BaseModel):
    collectionToken: ApiCollectionToken
    tokenCustomization: Optional[ApiTokenCustomization]
    tokenListing: Optional[ApiTokenListing]
    tokenStaking: Optional[ApiTokenStaking]
    quantity: int


class ApiUserProfile(BaseModel):
    address: str
    twitterId: Optional[str]
    discordId: Optional[str]


class ApiTwitterProfile(BaseModel):
    twitterId: str
    username: str
    name: str
    description: str
    isVerified: bool
    pinnedTweetId: Optional[str]
    followerCount: int
    followingCount: int
    tweetCount: int


class ApiGalleryUserBadge(BaseModel):
    registryAddress: str
    ownerAddress: str
    badgeKey: str
    achievedDate: datetime.datetime


class ApiGalleryUser(BaseModel):
    address: str
    registryAddress: str
    userProfile: Optional[ApiUserProfile]
    twitterProfile: Optional[ApiTwitterProfile]
    joinDate: Optional[datetime.datetime]


class ApiGalleryUserRow(BaseModel):
    galleryUser: ApiGalleryUser
    ownedTokenCount: int
    uniqueOwnedTokenCount: int
    chosenOwnedTokens: List[ApiCollectionToken]
    galleryUserBadges: List[ApiGalleryUserBadge]


class ApiGallerySuperCollectionUserRow(BaseModel):
    galleryUser: ApiGalleryUser
    ownedTokenCountMap: Dict[str, int]
    uniqueOwnedTokenCountMap: Dict[str, int]
    chosenOwnedTokensMap: Dict[str, List[ApiCollectionToken]]
    galleryUserBadges: List[ApiGalleryUserBadge]


class ApiOwnedCollection(BaseModel):
    collection: ApiCollection
    tokens: List[ApiCollectionToken]


class ApiAccountGm(BaseModel):
    address: str
    date: datetime.datetime
    streakLength: int
    collectionCount: int


class ApiGmAccountRow(BaseModel):
    address: str
    lastDate: datetime.datetime
    streakLength: int
    weekCount: int
    monthCount: int


class ApiAccountCollectionGm(BaseModel):
    accountCollectionGmId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime
    registryAddress: str
    accountAddress: str
    date: datetime.datetime
    signatureMessage: str
    signature: str


class ApiGmCollectionRow(BaseModel):
    collection: ApiCollection
    todayCount: int
    weekCount: int
    monthCount: int


class ApiLatestAccountGm(BaseModel):
    accountGm: ApiAccountGm
    accountCollectionGms: List[ApiAccountCollectionGm]


class ApiCollectionOverlap(BaseModel):
    registryAddress: str
    otherRegistryAddress: str
    ownerAddress: str
    registryTokenCount: int
    otherRegistryTokenCount: int


class ApiCollectionOverlapSummary(BaseModel):
    registryAddress: str
    otherCollection: ApiCollection
    ownerCount: int
    registryTokenCount: int
    otherRegistryTokenCount: int


class ApiCollectionOverlapOwner(BaseModel):
    registryAddress: str
    otherCollection: ApiCollection
    ownerAddress: str
    registryTokenCount: int
    otherRegistryTokenCount: int


class ApiSuperCollectionOverlap(BaseModel):
    ownerAddress: str
    otherRegistryAddress: str
    otherRegistryTokenCount: int
    registryTokenCountMap: Dict[str, int]


class ApiTrendingCollection(BaseModel):
    collection: ApiCollection
    previousSaleCount: str
    previousTotalVolume: str
    totalVolume: str
    totalSaleCount: str


class ApiMintedTokenCount(BaseModel):
    date: datetime.datetime
    mintedTokenCount: str
    newRegistryCount: str


class ApiTradingHistory(BaseModel):
    date: datetime.date
    transferCount: int
    buyCount: int
    sellCount: int
    mintCount: int


class ApiUserTradingOverview(BaseModel):
    mostTradedToken: Optional[ApiCollectionToken]
    highestSoldTokenTransfer: Optional[ApiTokenTransfer]
    highestBoughtTokenTransfer: Optional[ApiTokenTransfer]
    mostRecentlyMintedTokenTransfer: Optional[ApiTokenTransfer]
