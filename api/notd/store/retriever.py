from typing import Optional
from typing import Sequence

from core.exceptions import NotFoundException
from core.store.database import DatabaseConnection
from core.store.retriever import FieldFilter
from core.store.retriever import Order
from core.store.retriever import Retriever as CoreRetriever
from sqlalchemy import select
from sqlalchemy.sql import Select

from notd.model import AccountCollectionGm
from notd.model import AccountGm
from notd.model import Collection
from notd.model import CollectionHourlyActivity
from notd.model import CollectionOverlap
from notd.model import CollectionTotalActivity
from notd.model import GalleryBadgeHolder
from notd.model import LatestUpdate
from notd.model import Lock
from notd.model import TokenAttribute
from notd.model import TokenCustomization
from notd.model import TokenListing
from notd.model import TokenMetadata
from notd.model import TokenMultiOwnership
from notd.model import TokenOwnership
from notd.model import TokenTransfer
from notd.model import TwitterCredential
from notd.model import TwitterProfile
from notd.model import UserInteraction
from notd.model import UserProfile
from notd.store.schema import AccountCollectionGmsTable
from notd.store.schema import AccountGmsTable
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import GalleryBadgeHoldersTable
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import LatestUpdatesTable
from notd.store.schema import LocksTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionOverlapsTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenCustomizationsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import TwitterCredentialsTable
from notd.store.schema import TwitterProfilesTable
from notd.store.schema import UserInteractionsTable
from notd.store.schema import UserProfilesTable
from notd.store.schema_conversions import account_collection_gm_from_row
from notd.store.schema_conversions import account_gm_from_row
from notd.store.schema_conversions import block_from_row
from notd.store.schema_conversions import collection_activity_from_row
from notd.store.schema_conversions import collection_from_row
from notd.store.schema_conversions import collection_overlap_from_row
from notd.store.schema_conversions import collection_total_activity_from_row
from notd.store.schema_conversions import gallery_badge_holder_from_row
from notd.store.schema_conversions import latest_update_from_row
from notd.store.schema_conversions import lock_from_row
from notd.store.schema_conversions import token_attribute_from_row
from notd.store.schema_conversions import token_customization_from_row
from notd.store.schema_conversions import token_listing_from_row
from notd.store.schema_conversions import token_metadata_from_row
from notd.store.schema_conversions import token_multi_ownership_from_row
from notd.store.schema_conversions import token_ownership_from_row
from notd.store.schema_conversions import token_transfer_from_row
from notd.store.schema_conversions import twitter_credential_from_row
from notd.store.schema_conversions import twitter_profile_from_row
from notd.store.schema_conversions import user_interaction_from_row
from notd.store.schema_conversions import user_profile_from_row


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

    async def list_token_transfers(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, offset: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenTransfer]:
        query = select([TokenTransfersTable, BlocksTable]).join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
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
        tokenMetadata = token_metadata_from_row(row)
        return tokenMetadata

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

    async def list_collection_activities(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[CollectionHourlyActivity]:
        query = CollectionHourlyActivitiesTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=CollectionHourlyActivitiesTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=CollectionHourlyActivitiesTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        collectionActivities = [collection_activity_from_row(row) for row in result]
        return collectionActivities

    async def list_collection_total_activities(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[CollectionTotalActivity]:
        query = CollectionTotalActivitiesTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=CollectionTotalActivitiesTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=CollectionTotalActivitiesTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        collectionTotalActivities = [collection_total_activity_from_row(row) for row in result]
        return collectionTotalActivities

    async def get_collection_total_activity_by_address(self, address: str, connection: Optional[DatabaseConnection] = None) -> CollectionTotalActivity:
        query = (
            CollectionTotalActivitiesTable.select()
            .where(CollectionTotalActivitiesTable.c.address == address)
        )
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'CollectionTotalActivity with address:{address} not found')
        collectionTotalActivity = collection_total_activity_from_row(row)
        return collectionTotalActivity

    async def list_user_interactions(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[UserInteraction]:
        query = UserInteractionsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=UserInteractionsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=UserInteractionsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        userInteractions = [user_interaction_from_row(row) for row in result]
        return userInteractions

    async def list_latest_updates(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[LatestUpdate]:
        query = LatestUpdatesTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=LatestUpdatesTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=LatestUpdatesTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        latestUpdates = [latest_update_from_row(row) for row in result]
        return latestUpdates

    async def get_latest_update_by_key_name(self, key: str, name: Optional[str] = None, connection: Optional[DatabaseConnection] = None) -> LatestUpdate:
        query = (
            LatestUpdatesTable.select()
            .where(LatestUpdatesTable.c.key == key)
            .where(LatestUpdatesTable.c.name == name)
        )
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'LatestUpdate with key:{key} and name;{name} not found')
        latestUpdate = latest_update_from_row(row)
        return latestUpdate

    async def list_token_attributes(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenAttribute]:
        query = TokenAttributesTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenAttributesTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenAttributesTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        tokenAttributes = [token_attribute_from_row(row) for row in result]
        return tokenAttributes

    async def list_latest_token_listings(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenListing]:
        query = LatestTokenListingsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=LatestTokenListingsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=LatestTokenListingsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        latestTokenListings = [token_listing_from_row(row) for row in result]
        return latestTokenListings

    async def get_token_listing_by_registry_address_token_id(self, registryAddress: str, tokenId: str, connection: Optional[DatabaseConnection] = None) -> TokenListing:
        query = LatestTokenListingsTable.select() \
            .where(LatestTokenListingsTable.c.registryAddress == registryAddress) \
            .where(LatestTokenListingsTable.c.tokenId == tokenId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'LatestTokenListings with registry:{registryAddress} tokenId:{tokenId} not found')
        latestTokenListing = token_listing_from_row(row)
        return latestTokenListing

    async def list_token_customizations(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TokenCustomization]:
        query = TokenCustomizationsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenCustomizationsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenCustomizationsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        tokenCustomizations = [token_customization_from_row(row) for row in result]
        return tokenCustomizations

    async def get_token_customization_by_registry_address_token_id(self, registryAddress: str, tokenId: str, connection: Optional[DatabaseConnection] = None) -> TokenCustomization:
        query = TokenCustomizationsTable.select() \
            .where(TokenCustomizationsTable.c.registryAddress == registryAddress) \
            .where(TokenCustomizationsTable.c.tokenId == tokenId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TokenCustomization with registry:{registryAddress} tokenId:{tokenId} not found')
        tokenCustomization = token_customization_from_row(row)
        return tokenCustomization

    async def list_locks(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[Lock]:
        query = LocksTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=LocksTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=LocksTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        locks = [lock_from_row(row) for row in result]
        return locks

    async def get_lock(self, lockId: int, connection: Optional[DatabaseConnection] = None) -> Lock:
        query = LocksTable.select().where(LocksTable.c.lockId == lockId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'Lock with id:{lockId} not found')
        lock = lock_from_row(row)
        return lock

    async def get_lock_by_name(self, name: str, connection: Optional[DatabaseConnection] = None) -> Lock:
        query = LocksTable.select().where(LocksTable.c.name == name)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'Lock with name:{name} not found')
        lock = lock_from_row(row)
        return lock

    async def list_user_profiles(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[UserProfile]:
        query = UserProfilesTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=UserProfilesTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=UserProfilesTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        userProfiles = [user_profile_from_row(row) for row in result]
        return userProfiles

    async def get_user_profile(self, userProfileId: int, connection: Optional[DatabaseConnection] = None) -> UserProfile:
        query = UserProfilesTable.select().where(UserProfilesTable.c.userProfileId == userProfileId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'UserProfile with id:{userProfileId} not found')
        userProfile = user_profile_from_row(row)
        return userProfile

    async def get_user_profile_by_address(self, address: str, connection: Optional[DatabaseConnection] = None) -> UserProfile:
        query = UserProfilesTable.select().where(UserProfilesTable.c.address == address)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'UserProfile with address:{address} not found')
        userProfile = user_profile_from_row(row)
        return userProfile

    async def list_twitter_profiles(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TwitterProfile]:
        query = TwitterProfilesTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TwitterProfilesTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TwitterProfilesTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        twitterProfiles = [twitter_profile_from_row(row) for row in result]
        return twitterProfiles

    async def get_twitter_profile(self, twitterProfileId: int, connection: Optional[DatabaseConnection] = None) -> TwitterProfile:
        query = TwitterProfilesTable.select().where(TwitterProfilesTable.c.twitterProfileId == twitterProfileId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TwitterProfile with id:{twitterProfileId} not found')
        twitterProfile = twitter_profile_from_row(row)
        return twitterProfile

    async def get_twitter_profile_by_twitter_id(self, twitterId: str, connection: Optional[DatabaseConnection] = None) -> TwitterProfile:
        query = TwitterProfilesTable.select().where(TwitterProfilesTable.c.twitterId == twitterId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TwitterProfile with twitterId:{twitterId} not found')
        twitterProfile = twitter_profile_from_row(row)
        return twitterProfile

    async def get_twitter_profile_by_username(self, username: str, connection: Optional[DatabaseConnection] = None) -> TwitterProfile:
        query = TwitterProfilesTable.select().where(TwitterProfilesTable.c.username == username)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TwitterProfile with username:{username} not found')
        twitterProfile = twitter_profile_from_row(row)
        return twitterProfile

    async def list_twitter_credentials(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[TwitterCredential]:
        query = TwitterCredentialsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TwitterCredentialsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TwitterCredentialsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        twitterCredentials = [twitter_credential_from_row(row) for row in result]
        return twitterCredentials

    async def get_twitter_credential(self, twitterCredentialId: int, connection: Optional[DatabaseConnection] = None) -> TwitterCredential:
        query = TwitterCredentialsTable.select().where(TwitterCredentialsTable.c.twitterCredentialId == twitterCredentialId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TwitterCredential with id:{twitterCredentialId} not found')
        twitterCredential = twitter_credential_from_row(row)
        return twitterCredential

    async def get_twitter_credential_by_twitter_id(self, twitterId: str, connection: Optional[DatabaseConnection] = None) -> TwitterCredential:
        query = TwitterCredentialsTable.select().where(TwitterCredentialsTable.c.twitterId == twitterId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'TwitterCredential with twitterId:{twitterId} not found')
        twitterCredential = twitter_credential_from_row(row)
        return twitterCredential

    async def list_account_gms(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[AccountGm]:
        query = AccountGmsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=AccountGmsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=AccountGmsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        accountGms = [account_gm_from_row(row) for row in result]
        return accountGms

    async def get_account_gm(self, accountGmId: int, connection: Optional[DatabaseConnection] = None) -> AccountGm:
        query = AccountGmsTable.select().where(AccountGmsTable.c.accountGmId == accountGmId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'AccountGm with id:{accountGmId} not found')
        accountGm = account_gm_from_row(row)
        return accountGm

    async def list_account_collection_gms(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[AccountCollectionGm]:
        query = AccountCollectionGmsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=AccountCollectionGmsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=AccountCollectionGmsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        accountCollectionGms = [account_collection_gm_from_row(row) for row in result]
        return accountCollectionGms

    async def get_account_collection_gm(self, accountCollectionGmId: int, connection: Optional[DatabaseConnection] = None) -> AccountCollectionGm:
        query = AccountCollectionGmsTable.select().where(AccountCollectionGmsTable.c.accountCollectionGmId == accountCollectionGmId)
        result = await self.database.execute(query=query, connection=connection)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'AccountCollectionGm with id:{accountCollectionGmId} not found')
        accountCollectionGm = account_collection_gm_from_row(row)
        return accountCollectionGm

    async def list_collection_overlaps(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[CollectionOverlap]:
        query = TokenCollectionOverlapsTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=TokenCollectionOverlapsTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=TokenCollectionOverlapsTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        collectionOverlaps = [collection_overlap_from_row(row) for row in result]
        return collectionOverlaps

    async def list_gallery_badge(self, fieldFilters: Optional[Sequence[FieldFilter]] = None, orders: Optional[Sequence[Order]] = None, limit: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> Sequence[GalleryBadgeHolder]:
        query = GalleryBadgeHoldersTable.select()
        if fieldFilters:
            query = self._apply_field_filters(query=query, table=GalleryBadgeHoldersTable, fieldFilters=fieldFilters)
        if orders:
            query = self._apply_orders(query=query, table=GalleryBadgeHoldersTable, orders=orders)
        if limit:
            query = query.limit(limit)
        result = await self.database.execute(query=query, connection=connection)
        galleryBadgeHolders = [gallery_badge_holder_from_row(row) for row in result]
        return galleryBadgeHolders
