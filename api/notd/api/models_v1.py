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
    frameImageUrl: Optional[str]
    attributes: Optional[List[Dict[str, Union[str, int, float, None, bool]]]]


class ApiTokenTransfer(BaseModel):
    tokenTransferId: int
    transactionHash: str
    registryAddress: str
    fromAddress: str
    toAddress: str
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
