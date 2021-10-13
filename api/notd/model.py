import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import dataclasses


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
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
class RetrievedTokenMetadata:
    registryAddress: str
    tokenId: str
    metadataUrl: str
    imageUrl: Optional[str]
    name: Optional[str]
    description: Optional[str]
    attributes: Optional[Dict[str, Union[str, int, float]]]

@dataclasses.dataclass
class TokenMetadata(RetrievedTokenMetadata):
    tokenMetadataId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime

    def to_dict(self) -> Dict:
        return {
            'tokenMetadataId': self.tokenMetadataId,
            'createdDate': self.createdDate,
            'updatedDate': self.updatedDate,
            'registryAddress': self.registryAddress,
            'tokenId': self.tokenId,
            'metadataUrl': self.metadataUrl,
            'imageUrl': self.imageUrl,
            'name': self.name,
            'description': self.description,
            'attributes': self.attributes,
        }

@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class TokenTransfer(RetrievedTokenTransfer):
    tokenTransferId: int

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
class Token:
    registryAddress: str
    tokenId: str

@dataclasses.dataclass
class UiData:
    highestPricedTokenTransfer: TokenTransfer
    mostTradedTokenTransfers: List[TokenTransfer]
    randomTokenTransfer: TokenTransfer
    sponsoredToken: Token
    transactionCount: int

@dataclasses.dataclass
class RegistryToken:
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
