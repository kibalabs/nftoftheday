import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from notd.model import RegistryToken
from notd.model import UiData


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
    def from_model(cls, model: UiData):
        return cls(
            registryAddress=model.registryAddress,
            tokenId=model.tokenId,
        )


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

class ApiRegistryToken(BaseModel):
    registryAddress: str
    tokenId: str
    name: str
    imageUrl: Optional[str]
    openSeaUrl: Optional[str]
    externalUrl: Optional[str]
    lastSaleDate: Optional[datetime.datetime]
    lastSalePrice: Optional[int]
    collectionName: str
    collectionImageUrl: Optional[str]
    collectionOpenSeaUrl: Optional[str]
    collectionExternalUrl: Optional[str]

    @classmethod
    def from_model(cls, model: RegistryToken):
        return cls(
            registryAddress=model.registryAddress,
            tokenId=model.tokenId,
            name=model.name,
            imageUrl=model.imageUrl,
            openSeaUrl=model.openSeaUrl,
            externalUrl=model.externalUrl,
            lastSaleDate=model.lastSaleDate,
            lastSalePrice=model.lastSalePrice,
            collectionName=model.collectionName,
            collectionImageUrl=model.collectionImageUrl,
            collectionOpenSeaUrl=model.collectionOpenSeaUrl,
            collectionExternalUrl=model.collectionExternalUrl,
        )

class RetrieveUiDataRequest(BaseModel):
    startDate: Optional[datetime.datetime]
    endDate: Optional[datetime.datetime]

class RetrieveUiDataResponse(BaseModel):
    uiData: ApiUiData

class ReceiveNewBlocksDeferredRequest(BaseModel):
    pass

class ReceiveNewBlocksDeferredResponse(BaseModel):
    pass

class RetreiveRegistryTokenRequest(BaseModel):
    # registryAddress: str
    # tokenId: str
    pass

class RetreiveRegistryTokenResponse(BaseModel):
    registryToken: ApiRegistryToken

class SubscribeRequest(BaseModel):
    email: str

class SubscribeResponse(BaseModel):
    pass
