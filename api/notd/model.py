import datetime
from typing import Dict
from typing import List
from typing import Optional

from core.util import date_util
from core.util.typing_util import JSON
from pydantic import dataclasses


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class RetrievedTokenTransfer:
    transactionHash: str
    registryAddress: str
    fromAddress: str
    toAddress: str
    operatorAddress: Optional[str]
    tokenId: str
    amount: Optional[int]
    value: int
    gasLimit: int
    gasPrice: int
    gasUsed: int
    blockNumber: int
    blockHash: str
    blockDate: datetime.datetime
    tokenType: Optional[str]

@dataclasses.dataclass
class RetrievedTokenMetadata:
    registryAddress: str
    tokenId: str
    metadataUrl: str
    imageUrl: Optional[str]
    name: Optional[str]
    description: Optional[str]
    attributes: JSON


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
            'operatorAddress': self.operatorAddress,
            'tokenId': self.tokenId,
            'value': self.value,
            'amount': self.amount,
            'gasLimit': self.gasLimit,
            'gasPrice': self.gasPrice,
            'gasUsed': self.gasUsed,
            'blockNumber': self.blockNumber,
            'blockHash': self.blockHash,
            'blockDate': self.blockDate.isoformat(),
            'tokenType': self.tokenType,
        }


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

    def to_dict(self) -> Dict:
        return {
            'collectionId': self.collectionId,
            'createdDate': self.createdDate,
            'updatedDate': self.updatedDate,
            'address': self.address,
            'name': self.name ,
            'symbol': self.symbol ,
            'description': self.description ,
            'imageUrl': self.imageUrl ,
            'twitterUsername': self.twitterUsername,
            'instagramUsername': self.instagramUsername ,
            'wikiUrl': self.wikiUrl ,
            'openseaSlug': self.openseaSlug ,
            'url': self.url ,
            'discordUrl': self.discordUrl ,
            'bannerImageUrl': self.bannerImageUrl ,
            'doesSupportErc721': self.doesSupportErc721,
            'doesSupportErc1155': self.doesSupportErc1155,
 
        }

@dataclasses.dataclass
class SponsoredToken:
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
class TokenSale():
    tokenTransferId: int
    date: datetime.datetime
    value: int
    transactionHash: str
    fromAddress: str
    toAddress: str
    collectionToken: Collection

    #def to_dict(self) -> Dict:
    #    return {
    #        'tokenTransferId': self.tokenTransferId,
    #        'transactionHash': self.transactionHash,
    #        'fromAddress': self.fromAddress,
    #        'toAddress': self.toAddress,
    #        'value': self.value,
    #        'amount': self.amount,
    #        'blockDate': self.blockDate.isoformat(),
    #    }
