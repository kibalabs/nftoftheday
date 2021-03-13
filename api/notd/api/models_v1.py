import datetime
from typing import Dict
from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import Json

from notd.model import Token
from notd.model import TokenTransfer
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

    @classmethod
    def from_model(cls, model: UiData):
        return cls(
            highestPricedTokenTransfer=ApiTokenTransfer.from_model(model=model.highestPricedTokenTransfer),
            mostTradedTokenTransfers=[ApiTokenTransfer.from_model(model=transfer) for transfer in model.mostTradedTokenTransfers],
            randomTokenTransfer=ApiTokenTransfer.from_model(model=model.randomTokenTransfer),
            sponsoredToken=ApiToken.from_model(model=model.sponsoredToken),
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
