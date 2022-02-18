import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel

from notd.model import Token
from notd.model import UiData


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
    imageUrl: Optional[str]
    description: Optional[str]
    attributes: Optional[List[Dict[str, Union[str, int, float]]]]


class ApiTokenTransfer(BaseModel):
    tokenTransferId: int
    transactionHash: str
    registryAddress: str
    fromAddress: str
    toAddress: str
    tokenId: str
    value: int
    gasLimit: int
    gasPrice: int
    gasUsed: int
    blockNumber: int
    blockHash: str
    blockDate: datetime.datetime
    # NOTE(krishan711): make these non-optional once ui-data is fixed
    collection: Optional[ApiCollection]
    token: Optional[ApiCollectionToken]

    @classmethod
    def from_model(cls, model: UiData):
        return cls(
            tokenTransferId=model.tokenTransferId,
            transactionHash=model.transactionHash,
            registryAddress=model.registryAddress,
            fromAddress=model.fromAddress,
            toAddress=model.toAddress,
            tokenId=model.tokenId,
            value=model.value,
            gasLimit=model.gasLimit,
            gasPrice=model.gasPrice,
            gasUsed=model.gasUsed,
            blockNumber=model.blockNumber,
            blockHash=model.blockHash,
            blockDate=model.blockDate,
        )

class ApiToken(BaseModel):
    registryAddress: str
    tokenId: str

    @classmethod
    def from_model(cls, model: Token):
        return cls(
            registryAddress=model.registryAddress,
            tokenId=model.tokenId,
        )

class ApiTradedToken(BaseModel):
    collectionToken: ApiCollectionToken
    latestTransfer: ApiTokenTransfer
    transferCount: int


class ApiUiData(BaseModel):
    highestPricedTokenTransfer: ApiTokenTransfer
    mostTradedTokenTransfers: List[ApiTokenTransfer]
    randomTokenTransfer: ApiTokenTransfer
    sponsoredToken: ApiToken
    transactionCount: int

    @classmethod
    def from_model(cls, model: UiData):
        return cls(
            highestPricedTokenTransfer=ApiTokenTransfer.from_model(model=model.highestPricedTokenTransfer),
            mostTradedTokenTransfers=[ApiTokenTransfer.from_model(model=transfer) for transfer in model.mostTradedTokenTransfers],
            randomTokenTransfer=ApiTokenTransfer.from_model(model=model.randomTokenTransfer),
            sponsoredToken=ApiToken.from_model(model=model.sponsoredToken),
            transactionCount=model.transactionCount
        )

class ApiCollectionStatistics(BaseModel):
    itemCount: int
    holderCount: int
    totalTradeVolume: int
    lowestSaleLast24Hours: Optional[int]
    highestSaleLast24Hours: Optional[int]
    tradeVolume24Hours: Optional[int]
