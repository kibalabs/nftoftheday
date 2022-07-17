import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

import sqlalchemy
from core.util import chain_util
from core.web3.eth_client import EthClientInterface

from notd.api.endpoints_v1 import InQueryParam
from notd.model import Airdrop
from notd.model import CollectionAttribute
from notd.model import Token
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenOwnershipsTable

SPRITE_CLUB_REGISTRY_ADDRESS = '0x2744fE5e7776BCA0AF1CDEAF3bA3d1F5cae515d3'
SPRITE_CLUB_STORMDROP_REGISTRY_ADDRESS = '0x27C86e1c64622643049d3D7966580Cb832dCd1EF'

class GalleryManager:

    def __init__(self, ethClient: EthClientInterface, retriever: Retriever) -> None:
        self.ethClient = ethClient
        self.retriever = retriever
        with open('./contracts/SpriteClub.json', 'r') as contractJsonFile:
            self.spriteClubContract = json.load(contractJsonFile)
        with open('./contracts/SpriteClubStormdrop.json', 'r') as contractJsonFile:
            self.spriteClubStormdropContract = json.load(contractJsonFile)
        self.spriteClubStormdropClaimedFunctionAbi = [internalAbi for internalAbi in self.spriteClubStormdropContract['abi'] if internalAbi.get('name') == 'claimedSpriteItemIdMap'][0]
        with open('./contracts/SpriteClubStormdropIdMap.json', 'r') as contractJsonFile:
            self.spriteClubStormdropIdMap = json.load(contractJsonFile)

    async def list_collection_token_airdrops(self, registryAddress: str, tokenId: str) -> List[Airdrop]:
        registryAddress = chain_util.normalize_address(registryAddress)
        tokenKey = Token(registryAddress=registryAddress, tokenId=tokenId)
        if registryAddress == SPRITE_CLUB_REGISTRY_ADDRESS:
            claimedTokenId = (await self.ethClient.call_function(toAddress=SPRITE_CLUB_STORMDROP_REGISTRY_ADDRESS, contractAbi=self.spriteClubStormdropContract['abi'], functionAbi=self.spriteClubStormdropClaimedFunctionAbi, arguments={'': int(tokenId)}))[0]
            isClaimed = claimedTokenId > 0
            claimTokenId = claimedTokenId or self.spriteClubStormdropIdMap[tokenId]
            claimTokenKey = Token(registryAddress=SPRITE_CLUB_STORMDROP_REGISTRY_ADDRESS, tokenId=claimTokenId)
            return [Airdrop(name='Stormdrop ⚡️⚡️', tokenKey=tokenKey, isClaimed=isClaimed, claimTokenKey=claimTokenKey, claimUrl='https://stormdrop.spriteclubnft.com')]
        return []

    async def get_collection_attributes(self, registryAddress: str) -> List[CollectionAttribute]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        query = (
            TokenAttributesTable.select()
                .distinct()
                .with_only_columns([TokenAttributesTable.c.name, TokenAttributesTable.c.value])
                .where(TokenAttributesTable.c.registryAddress == registryAddress)
                .order_by(TokenAttributesTable.c.name.asc(), TokenAttributesTable.c.value.asc())
        )
        result = await self.retriever.database.execute(query=query)
        collectionAttributeNameMap: Dict[str, CollectionAttribute] = dict()
        for name, value in result:
            collectionAttribute = collectionAttributeNameMap.get(name)
            if not collectionAttribute:
                collectionAttribute = CollectionAttribute(name=name, values=[])
                collectionAttributeNameMap[name] = collectionAttribute
            collectionAttribute.values.append(value)
        return list(collectionAttributeNameMap.values())

    async def query_collection_tokens(self, registryAddress: str, minPrice: Optional[int], maxPrice: Optional[int], isListed: Optional[bool], tokenIdIn: Optional[List[str]], attributeFilters: Optional[List[InQueryParam]], limit: int, offset: int) -> Sequence[TokenMetadata]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        # TODO(krishan711): this shouldn't join on single ownerships for erc1155
        query = (
            TokenMetadatasTable.select()
                .where(TokenMetadatasTable.c.registryAddress == registryAddress)
                .order_by(TokenMetadatasTable.c.tokenId.asc())
                .limit(limit)
                .offset(offset)
        )
        if isListed or minPrice or maxPrice:
            query = (
                query
                    .join(LatestTokenListingsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == LatestTokenListingsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == LatestTokenListingsTable.c.tokenId))
                    .join(TokenOwnershipsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenOwnershipsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenOwnershipsTable.c.tokenId, TokenOwnershipsTable.c.ownerAddress == LatestTokenListingsTable.c.offererAddress))
            )
        if minPrice:
            query = query.where(LatestTokenListingsTable.c.value >= minPrice)
        if maxPrice:
            query = query.where(LatestTokenListingsTable.c.value <= maxPrice)
        if tokenIdIn:
            query = query.where(TokenMetadatasTable.c.tokenId.in_(tokenIdIn))
        if attributeFilters:
            query = query.join(TokenAttributesTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenAttributesTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenAttributesTable.c.tokenId))
            for attributeFilter in attributeFilters:
                query = (
                    query
                        .where(TokenAttributesTable.c.name == attributeFilter.fieldName)
                        .where(TokenAttributesTable.c.value.in_(attributeFilter.values))
                )
        tokenMetadatas = await self.retriever.query_token_metadatas(query=query)
        return tokenMetadatas
