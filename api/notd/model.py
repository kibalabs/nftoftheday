import datetime
from typing import Dict
from typing import List
from typing import Optional

from pydantic import dataclasses


@dataclasses.dataclass
class TokenTransfer:
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

    def to_dict(self) -> Dict:
        return {
            'tokenTransferId': self.tokenTransferId,
            'transactionHash': self.transactionHash,
            'registryAddress': self.registryAddress,
            'fromAddress': self.fromAddress,
            'toAddress': self.toAddress,
            'tokenId': self.tokenId,
            'value': self.value,
            'gasLimit': self.gasLimit,
            'gasPrice': self.gasPrice,
            'gasUsed': self.gasUsed,
            'blockNumber': self.blockNumber,
            'blockHash': self.blockHash,
            'blockDate': self.blockDate.isoformat(),
        }

@dataclasses.dataclass
class RetrievedTokenTransfer:
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

@dataclasses.dataclass
class Token:
    registryAddress: str
    tokenId: str

@dataclasses.dataclass
class UiData:
    highestPricedTokenTransfer: TokenTransfer
    mostTradedTokenTransfers: List[TokenTransfer]
    randomTokenTransfer: TokenTransfer
    sponsoredToken: Token

@dataclasses.dataclass
class RegistryToken:
    registryAddress: str
    tokenId: int
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
    
