from typing import Optional
from typing import Sequence

from core.exceptions import NotFoundException
from core.store.database import DatabaseConnection
from core.store.retriever import FieldFilter
from core.store.retriever import Order
from core.store.retriever import Retriever as CoreRetriever
from core.store.retriever import StringFieldFilter
from sqlalchemy import select
from sqlalchemy.sql import Select

from notd.model import Collection
from notd.model import CollectionHourlyActivity
from notd.model import TokenMetadata
from notd.model import TokenMultiOwnership
from notd.model import TokenOwnership
from notd.model import TokenTransfer
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import block_from_row
from notd.store.schema_conversions import collection_activity_from_row
from notd.store.schema_conversions import collection_from_row
from notd.store.schema_conversions import token_metadata_from_row
from notd.store.schema_conversions import token_multi_ownership_from_row
from notd.store.schema_conversions import token_ownership_from_row
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
            raise NotFoundException(message=f'Block with blockNumber:{blockNumber} not found')
        block = block_from_row(row)
        return block

    async def list_token_transfers(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, offset: Optional[int] = None, shouldIgnoreRegistryBlacklist: bool = False, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenTransfer]:
        query = select([TokenTransfersTable, BlocksTable]).join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        if not shouldIgnoreRegistryBlacklist:
            query = self._apply_field_filter(query=query, table=TokenTransfersTable, fieldFilter=StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, notContainedIn=_REGISTRY_BLACKLIST))
        if fieldFilters:
            for fieldFilter in fieldFilters:
                if fieldFilter.fieldName in {BlocksTable.c.blockDate.key, BlocksTable.c.updatedDate.key}:
                    query = self._apply_date_field_filter(query=query, table=BlocksTable, fieldFilter=fieldFilter)
                else:
                    query = self._apply_field_filter(query=query, table=TokenTransfersTable, fieldFilter=fieldFilter)
        if orders:
            for order in orders:
                if order.fieldName in {BlocksTable.c.blockDate.key, BlocksTable.c.updatedDate.key}:
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

    async def query_token_metadatas(self, query: Select, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenMetadata]:
        result = await self.database.execute(query=query, connection=connection)
        tokenMetadatas = [token_metadata_from_row(row) for row in result]
        return tokenMetadatas

    async def list_token_metadatas(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenMetadata]:
        query = TokenMetadatasTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenMetadatasTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenMetadatasTable, orders=orders)
        if limit:
            query = query.limit(limit)
        return await self.query_token_metadatas(query=query, connection=connection)

    async def get_token_metadata_by_registry_address_token_id(self, registryAddress: str, tokenId: str, connection: Optional[DatabaseConnection] = None) -> TokenMetadata:
        query = TokenMetadatasTable.select() \
            .where(TokenMetadatasTable.c.registryAddress == registryAddress) \
            .where(TokenMetadatasTable.c.tokenId == tokenId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TokenMetadata with registry:{registryAddress} tokenId:{tokenId} not found')
        tokenMetdata = token_metadata_from_row(row)
        return tokenMetdata

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
            raise NotFoundException(message=f'Collection with registry:{address} not found')
        collection = collection_from_row(row)
        return collection

    async def list_token_ownerships(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenOwnership]:
        query = TokenOwnershipsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenOwnershipsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenOwnershipsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        tokenOwnerships = [token_ownership_from_row(row) for row in result]
        return tokenOwnerships

    async def get_token_ownership_by_registry_address_token_id(self, registryAddress: str, tokenId: str, connection: Optional[DatabaseConnection] = None) -> TokenOwnership:
        query = TokenOwnershipsTable.select() \
            .where(TokenOwnershipsTable.c.registryAddress == registryAddress) \
            .where(TokenOwnershipsTable.c.tokenId == tokenId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TokenOwnership with registry:{registryAddress} tokenId:{tokenId} not found')
        tokenOwnership = token_ownership_from_row(row)
        return tokenOwnership

    async def list_token_multi_ownerships(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenMultiOwnership]:
        query = TokenMultiOwnershipsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenMultiOwnershipsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenMultiOwnershipsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        tokenOwnerships = [token_multi_ownership_from_row(row) for row in result]
        return tokenOwnerships

    async def get_token_multi_ownership_by_registry_address_token_id_owner_address(self, registryAddress: str, tokenId: str, ownerAddress: str, connection: Optional[DatabaseConnection] = None) -> TokenMultiOwnership:  # pylint: disable=invalid-name
        query = TokenMultiOwnershipsTable.select() \
            .where(TokenMultiOwnershipsTable.c.registryAddress == registryAddress) \
            .where(TokenMultiOwnershipsTable.c.tokenId == tokenId) \
            .where(TokenMultiOwnershipsTable.c.ownerAddress == ownerAddress)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TokenMultiOwnership with registry:{registryAddress} tokenId:{tokenId} ownerAddress:{ownerAddress} not found')
        tokenOwnership = token_multi_ownership_from_row(row)
        return tokenOwnership

    async def list_collections_activity(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[CollectionHourlyActivity]:
        query = CollectionHourlyActivityTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=CollectionHourlyActivityTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=CollectionHourlyActivityTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        tokenCollections = [collection_activity_from_row(row) for row in result]
        return tokenCollections
