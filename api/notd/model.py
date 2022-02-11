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
    metadataUrl: str
    imageUrl: Optional[str]
    animationUrl: Optional[str]
    youtubeUrl: Optional[str]
    backgroundColour: Optional[str]
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
    gasUsed: int
    blockNumber: int
    blockHash: str
    blockDate: datetime.datetime
    tokenType: Optional[str]


@dataclasses.dataclass(frozen=True, unsafe_hash=True)
class TokenTransfer(RetrievedTokenTransfer):
    tokenTransferId: int

# TODO(krishan711): everything below this line should be removed!

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
