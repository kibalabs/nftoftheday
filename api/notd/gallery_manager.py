import json
from typing import List
from typing import Optional

import sqlalchemy
from core.util import chain_util
from core.web3.eth_client import EthClientInterface
from core.store.retriever import StringFieldFilter

from sqlalchemy import literal_column

from notd.model import Airdrop
from notd.model import CollectionAttribute
from notd.model import Token
from notd.store.retriever import Retriever
from notd.store.schema import TokenAttributesTable

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
        query = (
            TokenAttributesTable.select()
                .with_only_columns([TokenAttributesTable.c.attributeName, sqlalchemy.func.string_agg(TokenAttributesTable.c.attributeValue, literal_column("', '"))])
                .group_by(TokenAttributesTable.c.attributeName)
        )
        result = await self.retriever.database.execute(query=query)
        attributeValues = [CollectionAttribute(attributeName=row[0], attributeValues=list({row[1]})) for row in result]
        return attributeValues

    async def get_tokens_with_attributes(self, registryAddress: str, queryStringDict: dict, limit: int, offset: int):
        query = (TokenAttributesTable.select()
                .with_only_columns([TokenAttributesTable.c.registryAddress, TokenAttributesTable.c.tokenId])
                .where(TokenAttributesTable.c.registryAddress == registryAddress)
                .subquery())
        for name, value in queryStringDict.items():
            query = (query.select()
                .with_only_columns([TokenAttributesTable.c.registryAddress, TokenAttributesTable.c.tokenId])
                .where(sqlalchemy.tuple_(TokenAttributesTable.c.registryAddress,TokenAttributesTable.c.tokenId).in_(query.select()))
                .where(sqlalchemy.tuple_(TokenAttributesTable.c.name,TokenAttributesTable.c.value) == (name, value)))   
        query = query.offset(offset)
        query = query.limit(limit)     
        result = await self.retriever.database.execute(query=query)
        tokens = [Token(registryAddress=row[0], tokenId=row[1]) for row in result]
        return tokens
