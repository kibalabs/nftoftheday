import datetime
from typing import List
from typing import Optional
from typing import Sequence

from core.exceptions import NotFoundException
from core.store.database import DatabaseConnection
from core.store.retriever import FieldFilter
from core.store.retriever import Order
from core.store.retriever import Retriever as CoreRetriever
from core.store.retriever import StringFieldFilter
from sqlalchemy import func as sqlalchemyfunc
from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy.sql.expression import func as sqlalchemyfunc
from sqlalchemy.sql.expression import select
from notd.store.schema import TokenOwnershipTable
from notd.store.schema_conversions import token_ownership_from_row

from notd.model import Collection
from notd.model import Token
from notd.model import TokenMetadata
from notd.model import TokenTransfer
from notd.store.schema import BlocksTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadataTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import block_from_row
from notd.store.schema_conversions import collection_from_row
from notd.store.schema_conversions import token_metadata_from_row
from notd.store.schema_conversions import token_transfer_from_row

_REGISTRY_BLACKLIST = set([
    '0x58A3c68e2D3aAf316239c003779F71aCb870Ee47', # Curve SynthSwap
    '0xFf488FD296c38a24CCcC60B43DD7254810dAb64e', # zed.run
    '0xC36442b4a4522E871399CD717aBDD847Ab11FE88', # uniswap-v3-positions
    '0xb9ed94c6d594b2517c4296e24a8c517ff133fb6d', # hegic-eth-atm-calls-pool
])

class Retriever(CoreRetriever):

    async def list_blocks(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, offset: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenTransfer]:
        query = BlocksTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=BlocksTable, fieldFilters=fieldFilters)
        if orders:
            for order in orders:
                query = self._apply_order(query=query, table=BlocksTable, order=order)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = await self.database.execute(query=query, connection=connection)
        blocks = [block_from_row(row) for row in result]
        return blocks

    async def get_block_by_number(self, blockNumber: int, connection: Optional[DatabaseConnection] = None) -> TokenMetadata:
        query = BlocksTable.select() \
            .where(BlocksTable.c.blockNumber == blockNumber)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'Block with blockNumber {blockNumber} not found')
        block = block_from_row(row)
        return block

    async def list_token_transfers(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, offset: Optional[int] = None, shouldIgnoreRegistryBlacklist: bool = False, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenTransfer]:
        query = select([TokenTransfersTable, BlocksTable.c.blockDate]).join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        if not shouldIgnoreRegistryBlacklist:
            query = self._apply_field_filter(query=query, table=TokenTransfersTable, fieldFilter=StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, notContainedIn=_REGISTRY_BLACKLIST))
        if fieldFilters:
            for fieldFilter in fieldFilters:
                if fieldFilter.fieldName == BlocksTable.c.blockDate.key:
                    query = self._apply_date_field_filter(query=query, table=BlocksTable, fieldFilter=fieldFilter)
                else:
                    query = self._apply_field_filter(query=query, table=TokenTransfersTable, fieldFilter=fieldFilter)
        if orders:
            for order in orders:
                if order.fieldName == BlocksTable.c.blockDate.key:
                    query = self._apply_order(query=query, table=BlocksTable, order=order)
                else:
                    query = self._apply_order(query=query, table=TokenTransfersTable, order=order)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = await self.database.execute(query=query, connection=connection)
        tokenTransfers = [token_transfer_from_row(row) for row in result]
        return tokenTransfers

    async def get_transaction_count(self, startDate: datetime.datetime, endDate: datetime.datetime, connection: Optional[DatabaseConnection] = None) -> int:
        query = TokenTransfersTable.select().join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        query = query.with_only_columns([sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId)])
        query = query.where(BlocksTable.c.blockDate >= startDate)
        query = query.where(BlocksTable.c.blockDate < endDate)
        result = await self.database.execute(query=query, connection=connection)
        count = result.scalar()
        return count

    async def get_most_traded_token(self, startDate: datetime.datetime, endDate: datetime.datetime, connection: Optional[DatabaseConnection] = None) -> Token:
        query = TokenTransfersTable.select().join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        query = query.with_only_columns([TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId, sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId)])
        query = query.group_by(TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId)
        query = query.where(BlocksTable.c.blockDate >= startDate)
        query = query.where(BlocksTable.c.blockDate < endDate)
        query = query.where(TokenTransfersTable.c.registryAddress.notin_(_REGISTRY_BLACKLIST))
        query = query.order_by(sqlalchemyfunc.count(TokenTransfersTable.c.tokenTransferId).desc())
        query = query.limit(1)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        return Token(registryAddress=row[TokenTransfersTable.c.registryAddress], tokenId=row[TokenTransfersTable.c.tokenId])

    async def list_tokens_by_collection(self, address: str, connection: Optional[DatabaseConnection] = None) -> List:
        query = TokenTransfersTable.select().distinct(TokenTransfersTable.c.tokenId)
        query = query.with_only_columns([TokenTransfersTable.c.registryAddress, TokenTransfersTable.c.tokenId])
        query = query.where(TokenTransfersTable.c.registryAddress == address)
        result = await self.database.execute(query=query, connection=connection)
        return list(result)

    async def query_token_metadatas(self, query: Select, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenMetadata]:
        result = await self.database.execute(query=query, connection=connection)
        tokenMetadatas = [token_metadata_from_row(row) for row in result]
        return tokenMetadatas

    async def list_token_metadatas(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenMetadata]:
        query = TokenMetadataTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenMetadataTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenMetadataTable, orders=orders)
        if limit:
            query = query.limit(limit)
        return await self.query_token_metadatas(query=query, connection=connection)

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str, connection: Optional[DatabaseConnection] = None) -> TokenMetadata:
        query = TokenMetadataTable.select() \
            .where(TokenMetadataTable.c.registryAddress == registryAddress) \
            .where(TokenMetadataTable.c.tokenId == tokenId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TokenMetadata with registry {registryAddress} tokenId {tokenId} not found')
        tokenMetdata = token_metadata_from_row(row)
        return tokenMetdata

    async def get_token_ownership_by_registry_address_token_id(self, registryAddress: str, tokenId: str, connection: Optional[DatabaseConnection] = None) -> TokenMetadata:
        query = TokenOwnershipTable.select() \
            .where(TokenOwnershipTable.c.registryAddress == registryAddress) \
            .where(TokenOwnershipTable.c.tokenId == tokenId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TokenMetadata with registry {registryAddress} tokenId {tokenId} not found')
        tokenOwnership = token_ownership_from_row(row)
        return tokenOwnership

    async def list_collections(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[Collection]:
        query = TokenCollectionsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenCollectionsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenCollectionsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        tokenCollections = [collection_from_row(row) for row in result]
        return tokenCollections

    async def get_collection_by_address(self, address: str, connection: Optional[DatabaseConnection] = None) -> Collection:
        query = TokenCollectionsTable.select() \
            .where(TokenCollectionsTable.c.address == address)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'Collection with registry {address} not found')
        collection = collection_from_row(row)
        return collection

    async def list_collection_tokens_by_owner(self, address: str, ownerAddress: str, connection: Optional[DatabaseConnection] = None) -> List[Token]:
        boughtTokens = []
        soldTokens= []
        query = select([TokenTransfersTable, BlocksTable.c.blockDate]).join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        query = query.where(TokenTransfersTable.c.registryAddress == address)
        query = query.where(TokenTransfersTable.c.toAddress == ownerAddress)
        boughtResult = await self.database.execute(query=query, connection=connection)
        boughtTokens = [(token.registryAddress, token.tokenId) for token in [token_transfer_from_row(row) for row in boughtResult]]
        query = select([TokenTransfersTable, BlocksTable.c.blockDate]).join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        query = query.where(TokenTransfersTable.c.registryAddress == address)
        query = query.where(TokenTransfersTable.c.fromAddress == ownerAddress)
        soldResult = await self.database.execute(query=query, connection=connection)
        soldTokens = [(token.registryAddress, token.tokenId) for token in [token_transfer_from_row(row) for row in soldResult]]
        for token in soldTokens:
            boughtTokens.remove(token)
        return list(boughtTokens)
