import datetime
from typing import Dict
from typing import List
from typing import Optional

from core.util import date_util
from core.util.typing_util import JSON
from pydantic import dataclasses


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
    imageUrl: Optional[str]
    animationUrl: Optional[str]
    youtubeUrl: Optional[str]
    backgroundColor: Optional[str]
    name: Optional[str]
    description: Optional[str]
    attributes: JSON


@dataclasses.dataclass
class TokenMetadata(RetrievedTokenMetadata):
    tokenMetadataId: int
    createdDate: datetime.datetime
    updatedDate: datetime.datetime


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class RetrievedTokenTransfer:
    transactionHash: str
    registryAddress: str
    tokenId: str
    fromAddress: str
    toAddress: str
    operatorAddress: Optional[str]
    amount: Optional[int]
    value: int
    gasLimit: int
    gasPrice: int
    blockNumber: int
    tokenType: Optional[str]


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class TokenTransfer(RetrievedTokenTransfer):
    tokenTransferId: int
    blockDate: datetime.datetime


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
class CollectionGraph:
    date: datetime.datetime
    value: int
    amount: int
