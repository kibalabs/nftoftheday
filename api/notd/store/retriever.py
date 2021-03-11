from enum import Enum
from typing import Optional
from typing import Sequence
from typing import List
from typing import Optional

from databases import Database
import sqlalchemy

from notd.model import TokenTransfer
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

class Direction(Enum):
    ASCENDING = 'ascending'
    DESCENDING = 'descending'

class Order:

    def __init__(self, fieldName: str, direction: Direction = Direction.DESCENDING):
        self.fieldName = fieldName
        self.direction = direction

class Retriever:

    def __init__(self, database: Database):
        self.database = database

    async def list_token_transfers(self, orders: Optional[List[Order]], limit: Optional[int]) -> Sequence[TokenTransfer]:
        query = TokenTransfersTable.select()
        if orders:
            for order in orders:
                field = TokenTransfersTable.c[order.fieldName]
                query = query.order_by(field.asc() if order.direction == Direction.ASCENDING else field.desc())
        if limit:
            query = query.limit(1)
        rows = await self.database.fetch_all(query=query)
        tokenTransfers = [token_transfer_from_row(row) for row in rows]
        return tokenTransfers
