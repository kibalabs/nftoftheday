
from core.store.retriever import StringFieldFilter
from notd.model import RetrievedTokenAttribute
from notd.store.schema import TokenMetadatasTable

from notd.store.retriever import Retriever


class TokenAttributeProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def get_token_attributes(self, registryAddress: str, tokenId: str) -> None:
        tokenMetadata = await self.retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(TokenMetadatasTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(TokenMetadatasTable.c.tokenId.key, eq=tokenId),
            ]
        )
        tokenAttributes = []
        for attribute in tokenMetadata.attributes:
            tokenAttributes += [RetrievedTokenAttribute(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, attributeName=attribute.get("trait_type"), attributeValue=attribute.get("value"))]
        return tokenAttributes
