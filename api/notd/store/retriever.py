import datetime
from typing import Optional
from typing import Sequence
from typing import Optional

from  sqlalchemy.sql.expression import func as sqlalchemyfunc

from notd.core.store.retriever import Retriever
from notd.core.store.retriever import FieldFilter
from notd.core.store.retriever import Order
from notd.model import Token
from notd.model import TokenTransfer
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

class NotdRetriever(Retriever):

    async def list_token_transfers(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None) -> Sequence[TokenTransfer]:
        query = TokenTransfersTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenTransfersTable, fieldFilters=fieldFilters)
        if orders:
            for order in orders:
                query = self._apply_order(query=query, table=TokenTransfersTable, order=order)
        if limit:
            query = query.limit(limit)
        rows = await self.database.fetch_all(query=query)
        tokenTransfers = [token_transfer_from_row(row) for row in rows]
        return tokenTransfers

    async def get_most_traded_token(self, startDate: datetime.datetime, endDate: datetime.datetime) -> Token:
        query = TokenTransfersTable.select()
        query = query.with_only_columns([TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId, sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId)])
        query = query.group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
        query = query.where(TokenTransfersTable.c.blockDate >= startDate)
        query = query.where(TokenTransfersTable.c.blockDate < endDate)
        query = query.order_by(sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId).desc())
        query = query.limit(1)
        rows = await self.database.fetch_all(query=query)
        return Token(registryAddress=rows[0][TokenTransfersTable.c.registryAddress], tokenId=rows[0][TokenTransfersTable.c.tokenId])
