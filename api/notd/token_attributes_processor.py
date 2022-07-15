
from typing import List

from notd.model import RetrievedTokenAttribute
from notd.store.retriever import Retriever


class TokenAttributeProcessor:

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    async def get_token_attributes(self, registryAddress: str, tokenId: str) -> List[RetrievedTokenAttribute]:
        tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        tokenAttributes = []
        for attribute in tokenMetadata.attributes:
            name = attribute.get('trait_type')
            if not name:
                continue
            value = attribute.get('value')
            tokenAttributes += [RetrievedTokenAttribute(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, name=name, value=value)]
        return tokenAttributes
