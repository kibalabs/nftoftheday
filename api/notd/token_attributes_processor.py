import datetime

from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from notd.model import RetrievedTokenAttribute
from notd.store.schema import TokenMetadatasTable

from notd.date_util import date_hour_from_datetime
from notd.model import RetrievedCollectionHourlyActivity
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable


class TokenAttributeProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def get_token_attributes(self, registryAddress: str, tokenId: str) -> None:
        tokenMetadatas = await self.retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(TokenMetadatasTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(TokenMetadatasTable.c.tokenId.key, eq=tokenId),
            ]
        )
        tokenAttributes = []
        for tokenMetadata in tokenMetadatas:
            for attribute in tokenMetadata.attributes:
                tokenAttributes += [RetrievedTokenAttribute(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, attributeName=attribute.get("trait_type"), attributeValue=attribute.get("value"))]
                
        return tokenAttributes
