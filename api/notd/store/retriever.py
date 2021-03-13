import dataclasses
from enum import Enum
from typing import Optional
from typing import Sequence
from typing import List
from typing import Optional

from databases import Database
import sqlalchemy
from sqlalchemy import Table
from sqlalchemy.sql.expression import FromClause

from notd.model import TokenTransfer
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

class Direction(Enum):
    ASCENDING = 'ascending'
    DESCENDING = 'descending'

@dataclasses.dataclass
class Order:
        fieldName: str
        direction: Direction = Direction.DESCENDING

@dataclassess.dataclass
class NumericField:
    isNull: Optional[bool]: None
    isNotNull: Optional[bool]: None
    eq: Optional[int]: None
    ne: Optional[int]: None
    le: Optional[int]: None
    lt: Optional[int]: None
    ge: Optional[int]: None
    gt: Optional[int]: None
    containedIn: Optional[List[int]]: None
    notContainedIn: Optional[List[int]]: None

@dataclassess.dataclass
class DateField:
    isNull: Optional[bool]: None
    isNotNull: Optional[bool]: None
    eq: Optional[int]: None
    ne: Optional[int]: None
    le: Optional[int]: None
    lt: Optional[int]: None
    ge: Optional[int]: None
    gt: Optional[int]: None
    containedIn: Optional[List[int]]: None
    notContainedIn: Optional[List[int]]: None

class Retriever:

    def __init__(self, database: Database):
        self.database = database

    def _apply_order(self, query: FromClause, tableClass: Table, order: Order) -> FromClause:
        field = table.c[order.fieldName]
        query = query.order_by(field.asc() if order.direction == Direction.ASCENDING else field.desc())
        return query

    async def list_token_transfers(self, orders: Optional[List[Order]], limit: Optional[int]) -> Sequence[TokenTransfer]:
        query = TokenTransfersTable.select()
        if orders:
            for order in orders:
                query = self._apply_order(query=query, table=TokenTransfersTable, order=order)
        if limit:
            query = query.limit(1)
        rows = await self.database.fetch_all(query=query)
        tokenTransfers = [token_transfer_from_row(row) for row in rows]
        return tokenTransfers
