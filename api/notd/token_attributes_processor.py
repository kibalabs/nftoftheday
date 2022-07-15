
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
        tokenMetadata = await self.retriever.get_token_metadata_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        tokenAttributes = []
        for attribute in tokenMetadata.attributes:
            name, value = list(attribute.values())[0], list(attribute.values())[1]
            tokenAttributes += [RetrievedTokenAttribute(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, name=name, value=value)]
        return tokenAttributes
