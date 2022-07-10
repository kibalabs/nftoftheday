import datetime

from core.store.retriever import DateFieldFilter
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from notd.model import RetrievedTokenAttributes
from notd.store.schema import TokenMetadatasTable

from notd.date_util import date_hour_from_datetime
from notd.model import RetrievedCollectionHourlyActivity
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable


class TokenAttributeProcessor:

    def __init__(self,retriever: Retriever) -> None:
        self.retriever = retriever

    async def get_token_attribute(self, address: str, startDate: datetime.datetime) -> None:
        tokenMetadatas = await self.retriever.list_token_metadatas(
            fieldFilters=[
                StringFieldFilter(TokenMetadatasTable.c.registryAddress.key, eq=address),
                DateFieldFilter(TokenMetadatasTable.c.updatedDate.key, gte=startDate),
            ]
        )
        print(len(tokenMetadatas))
        for tokenMetadata in tokenMetadatas:
            print(tokenMetadata.attributes)
            for attribute in tokenMetadata.attributes:
                tokenAttribute = RetrievedTokenAttributes(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, attributeName=attribute.get("trait_type"), attributeValue=attribute.get("value"))
                print(tokenAttribute)
            break
        pass
        