
from typing import List

from core.store.retriever import StringFieldFilter

from notd.model import RetrievedTokenAttribute
from notd.model import TokenAttribute
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.schema import TokenMetadatasTable


class TokenAttributeProcessor:

    def __init__(self, retriever: Retriever) -> None:
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
            tokenAttributes += [RetrievedTokenAttribute(registryAddress=token.registryAddress, tokenId=token.tokenId, name=attribute.get("trait_type"), value=attribute.get("value"))]
        return tokenAttributes
