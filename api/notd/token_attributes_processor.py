
import logging
from typing import List
from attr import attributes

from core.store.retriever import StringFieldFilter
from notd.model import TokenAttribute
from notd.store.saver import Saver
from notd.store.schema import TokenAttributesTable

from notd.model import RetrievedTokenAttribute
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.schema import TokenMetadatasTable


class TokenAttributeProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def get_token_attributes(self, registryAddress: str, tokenId: str) -> List[TokenAttribute]:
        tokenMetadata: List[TokenMetadata] = await self.retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(TokenMetadatasTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(TokenMetadatasTable.c.tokenId.key, eq=tokenId),
            ]
        )
        token = tokenMetadata[0]
        tokenAttributes = []
        for attribute in token.attributes:
            tokenAttributes += [RetrievedTokenAttribute(registryAddress=token.registryAddress, tokenId=token.tokenId, attributeName=attribute.get("trait_type"), attributeValue=attribute.get("value"))]
        return tokenAttributes
