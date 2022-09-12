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


class ApiTradedToken(BaseModel):
    token: ApiCollectionToken
    collection: ApiCollection
    latestTransfer: ApiTokenTransfer
    transferCount: str


class ApiSponsoredToken(BaseModel):
    token: ApiCollectionToken
    collection: ApiCollection
    date: datetime.datetime
    latestTransfer: Optional[ApiTokenTransfer]


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


class ApiGalleryToken(BaseModel):
    collectionToken: ApiCollectionToken
    tokenCustomization: Optional[ApiTokenCustomization]
    tokenListing: Optional[ApiTokenListing]


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


class ApiGalleryUser(BaseModel):
    address: str
    registryAddress: str
    userProfile: Optional[ApiUserProfile]
    twitterProfile: Optional[ApiTwitterProfile]
    ownedTokenCount: int
    joinDate: Optional[datetime.datetime]


class ApiGalleryUserRow(BaseModel):
    galleryUser: ApiGalleryUser
    chosenOwnedTokens: List[ApiCollectionToken]


class ApiGalleryOwnedCollection(BaseModel):
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


class ApiGmCollectionRow(BaseModel):
    collection: ApiCollection
    todayCount: int
    weekCount: int
    monthCount: int
