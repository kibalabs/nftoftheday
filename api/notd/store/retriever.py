import datetime
from typing import AsyncGenerator
from typing import Optional
from typing import Sequence

from core.store.retriever import FieldFilter
from core.store.retriever import Order
from core.store.retriever import Retriever as CoreRetriever
from core.store.retriever import StringFieldFilter
from notd.model import Token
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_metadata_from_row
from notd.store.schema_conversions import token_transfer_from_row
from sqlalchemy.sql.expression import func as sqlalchemyfunc

_REGISTRY_BLACKLIST = set([
    '0x58A3c68e2D3aAf316239c003779F71aCb870Ee47', # Curve SynthSwap
    '0xFf488FD296c38a24CCcC60B43DD7254810dAb64e', # zed.run
    '0xC36442b4a4522E871399CD717aBDD847Ab11FE88', # uniswap-v3-positions
    '0xb9ed94c6d594b2517c4296e24a8c517ff133fb6d', # hegic-eth-atm-calls-pool
])

class Retriever(CoreRetriever):

    async def list_token_transfers(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None) -> Sequence[TokenTransfer]:
        return [tokenTransfer async for tokenTransfer in self.generate_token_transfers(fieldFilters=fieldFilters, orders=orders, limit=limit)]

    async def generate_token_transfers(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None) -> AsyncGenerator[TokenTransfer, None]:
        query = TokenTransfersTable.select()
        query = self._apply_field_filter(query=query, table=TokenTransfersTable, fieldFilter=StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, notContainedIn=_REGISTRY_BLACKLIST))
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenTransfersTable, fieldFilters=fieldFilters)
        if orders:
            for order in orders:
                query = self._apply_order(query=query, table=TokenTransfersTable, order=order)
        if limit:
            query = query.limit(limit)
        async for row in self.database.iterate(query=query):
            tokenTransfer = token_transfer_from_row(row)
            yield tokenTransfer

    async def get_transaction_count(self, startDate: datetime.datetime, endDate: datetime.datetime) -> int:
        query = TokenTransfersTable.select()
        query = query.with_only_columns([sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId)])
        query = query.where(TokenTransfersTable.c.blockDate >= startDate)
        query = query.where(TokenTransfersTable.c.blockDate < endDate)
        query = query.where(TokenTransfersTable.c.registryAddress.notin_(_REGISTRY_BLACKLIST))
        count = await self.database.execute(query)
        return count

    async def get_most_traded_token(self, startDate: datetime.datetime, endDate: datetime.datetime) -> Token:
        query = TokenTransfersTable.select()
        query = query.with_only_columns([TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId, sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId)])
        query = query.group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
        query = query.where(TokenTransfersTable.c.blockDate >= startDate)
        query = query.where(TokenTransfersTable.c.blockDate < endDate)
        query = query.where(TokenTransfersTable.c.registryAddress.notin_(_REGISTRY_BLACKLIST))
        query = query.order_by(sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId).desc())
        query = query.limit(1)
        rows = await self.database.fetch_all(query=query)
        return Token(registryAddress=rows[0][TokenTransfersTable.c.registryAddress], tokenId=rows[0][TokenTransfersTable.c.tokenId])

    async def list_token_metadata(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None) -> Sequence[TokenMetadata]:
        query = TokenMetadataTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenMetadataTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenMetadataTable, orders=orders)
        if limit:
            query = query.limit(limit)
        rows = await self.database.fetch_all(query=query)
        tokenMetdata = [token_metadata_from_row(row) for row in rows]
        return tokenMetdata
