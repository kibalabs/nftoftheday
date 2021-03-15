import datetime
from typing import Optional
from typing import Sequence
from typing import Optional

from  sqlalchemy.sql.expression import func as sqlalchemyfunc

from notd.core.store.retriever import Retriever
from notd.core.store.retriever import FieldFilter
from notd.core.store.retriever import Order
from notd.core.store.retriever import StringFieldFilter
from notd.model import Token
from notd.model import TokenTransfer
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

_REGISTRY_BLACKLIST = set([
    '0x58A3c68e2D3aAf316239c003779F71aCb870Ee47',
    '0x58A3c68e2D3aAf316239c003779F71aCb870Ee47234808169212587382971023711941828336222959677902651',
    '0xFf488FD296c38a24CCcC60B43DD7254810dAb64e',
    '0x4201dB13824a50a11f931169b2F0Bca9cAc23614',
])

class NotdRetriever(Retriever):

    async def list_token_transfers(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None) -> Sequence[TokenTransfer]:
        query = TokenTransfersTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenTransfersTable, fieldFilters=fieldFilters)
        for registryAddress in _REGISTRY_BLACKLIST:
            query = self._apply_field_filter(query=query, table=TokenTransfersTable, fieldFilter=StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, ne=registryAddress))
        if orders:
            for order in orders:
                query = self._apply_order(query=query, table=TokenTransfersTable, order=order)
        if limit:
            query = query.limit(limit)
        print('query', query)
        rows = await self.database.fetch_all(query=query)
        tokenTransfers = [token_transfer_from_row(row) for row in rows]
        return tokenTransfers

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
