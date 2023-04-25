CREATE TABLE tbl_token_transfers (
    id BIGSERIAL PRIMARY KEY,
    transaction_hash TEXT NOT NULL,
    registry_address TEXT NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    operator_address TEXT NOT NULL,
    contract_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    value NUMERIC(256, 0) NOT NULL,
    amount_2 NUMERIC(256, 0) NOT NULL,
    gas_limit NUMERIC(256, 0) NOT NULL,
    gas_price NUMERIC(256, 0) NOT NULL,
    block_number INTEGER NOT NULL,
    token_type TEXT NOT NULL,
    is_multi_address BOOLEAN NOT NULL,
    is_interstitial BOOLEAN NOT NULL,
    is_swap BOOLEAN NOT NULL,
    is_batch BOOLEAN NOT NULL,
    is_outbound BOOLEAN NOT NULL
);
CREATE UNIQUE INDEX tbl_token_transfers_transaction_hash_registry_address_token_id_from_address_to_address_block_number_amount ON tbl_token_transfers (transaction_hash, registry_address, token_id, from_address, to_address, block_number, amount_2);
CREATE INDEX tbl_token_transfers_registry_address_token_id ON tbl_token_transfers (registry_address, token_id);
CREATE INDEX tbl_token_transfers_registry_address_token_id_block_number ON tbl_token_transfers (registry_address, token_id, block_number);
CREATE INDEX tbl_token_transfers_registry_address ON tbl_token_transfers (registry_address);
CREATE INDEX tbl_token_transfers_registry_address_block_number ON tbl_token_transfers (registry_address, block_number);
CREATE INDEX tbl_token_transfers_token_id ON tbl_token_transfers (token_id);
CREATE INDEX tbl_token_transfers_value ON tbl_token_transfers (value);
CREATE INDEX tbl_token_transfers_block_number ON tbl_token_transfers (block_number);
CREATE INDEX tbl_token_transfers_to_address ON tbl_token_transfers (to_address);
CREATE INDEX tbl_token_transfers_from_address ON tbl_token_transfers (from_address);
CREATE INDEX tbl_token_transfers_operator_address ON tbl_token_transfers (operator_address);
CREATE INDEX tbl_token_transfers_contract_address ON tbl_token_transfers (contract_address);
CREATE INDEX tbl_token_transfers_token_type ON tbl_token_transfers (token_type);
CREATE INDEX tbl_token_transfers_is_multi_address ON tbl_token_transfers (is_multi_address);
CREATE INDEX tbl_token_transfers_is_interstitial ON tbl_token_transfers (is_interstitial);
CREATE INDEX tbl_token_transfers_is_swap ON tbl_token_transfers (is_swap);
CREATE INDEX tbl_token_transfers_is_batch ON tbl_token_transfers (is_batch);
CREATE INDEX tbl_token_transfers_is_outbound ON tbl_token_transfers (is_outbound);
-- NOTE(krishan711): this is O(100m) rows and fills O(100k) per day
ALTER TABLE tbl_token_transfers SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tbl_token_transfers SET (autovacuum_analyze_scale_factor = 0.001);

CREATE TABLE tbl_token_metadatas (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    metadata_url TEXT,
    image_url TEXT,
    resizable_image_url TEXT,
    animation_url TEXT,
    youtube_url TEXT,
    background_colour TEXT,
    frame_image_url TEXT,
    name TEXT,
    description TEXT,
    attributes JSON
);
CREATE UNIQUE INDEX tbl_token_metadatas_registry_address_token_id ON tbl_token_metadatas (registry_address, token_id);
CREATE INDEX tbl_token_metadatas_registry_address_token_id_updated_date ON tbl_token_metadatas (registry_address, token_id, updated_date);
CREATE INDEX tbl_token_metadatas_registry_address ON tbl_token_metadatas (registry_address);
CREATE INDEX tbl_token_metadatas_token_id ON tbl_token_metadatas (token_id);
CREATE INDEX tbl_token_metadatas_updated_date ON tbl_token_metadatas (updated_date);
CREATE INDEX tbl_token_metadatas_name ON tbl_token_metadatas (name);
-- NOTE(krishan711): this is O(10m) rows and fills O(10k) per day
ALTER TABLE tbl_token_metadatas SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tbl_token_metadatas SET (autovacuum_analyze_scale_factor = 0.001);


CREATE TABLE tbl_collections (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    address TEXT NOT NULL,
    name TEXT,
    symbol TEXT,
    description TEXT,
    image_url TEXT,
    twitter_username TEXT,
    instagram_username TEXT,
    wiki_url TEXT,
    opensea_slug TEXT,
    url TEXT,
    discord_url TEXT,
    banner_image_url TEXT,
    does_support_erc721 BOOLEAN NOT NULL,
    does_support_erc1155 BOOLEAN NOT NULL
);
CREATE UNIQUE INDEX tbl_collections_address ON tbl_collections (address);
CREATE INDEX tbl_collections_address_updated_date ON tbl_collections (address, updated_date);
CREATE INDEX tbl_collections_updated_date ON tbl_collections (updated_date);
CREATE INDEX tbl_collections_name ON tbl_collections (name);


CREATE TABLE tbl_blocks (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    block_number INTEGER NOT NULL,
    block_hash TEXT NOT NULL,
    block_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX tbl_blocks_block_number ON tbl_blocks (block_number);
CREATE INDEX tbl_blocks_block_number_updated_date ON tbl_blocks (block_number, updated_date);
CREATE INDEX tbl_blocks_block_number_block_date ON tbl_blocks (block_number, block_date);
CREATE INDEX tbl_blocks_created_date ON tbl_blocks (created_date);
CREATE INDEX tbl_blocks_updated_date ON tbl_blocks (updated_date);
CREATE INDEX tbl_blocks_block_hash ON tbl_blocks (block_hash);
CREATE INDEX tbl_blocks_block_date ON tbl_blocks (block_date);
-- NOTE(krishan711): this is O(10m) rows and fills O(10k) per day
ALTER TABLE tbl_blocks SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tbl_blocks SET (autovacuum_analyze_scale_factor = 0.001);


CREATE TABLE tbl_token_ownerships (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    transfer_value NUMERIC(256, 0) NOT NULL,
    transfer_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    transfer_transaction_hash TEXT NOT NULL
);
CREATE UNIQUE INDEX tbl_token_ownerships_registry_address_token_id ON tbl_token_ownerships (registry_address, token_id);
CREATE INDEX tbl_token_ownerships_registry_address_token_id_updated_date ON tbl_token_ownerships (registry_address, token_id, updated_date);
CREATE INDEX tbl_token_ownerships_owner_address_transfer_date ON tbl_token_ownerships (owner_address, transfer_date);
CREATE INDEX tbl_token_ownerships_created_date ON tbl_token_ownerships (created_date);
CREATE INDEX tbl_token_ownerships_updated_date ON tbl_token_ownerships (updated_date);
CREATE INDEX tbl_token_ownerships_regsitry_address ON tbl_token_ownerships (registry_address);
CREATE INDEX tbl_token_ownerships_token_id ON tbl_token_ownerships (token_id);
CREATE INDEX tbl_token_ownerships_owner_address ON tbl_token_ownerships (owner_address);
CREATE INDEX tbl_token_ownerships_transfer_date ON tbl_token_ownerships (transfer_date);
CREATE INDEX tbl_token_ownerships_transfer_value ON tbl_token_ownerships (transfer_value);
CREATE INDEX tbl_token_ownerships_transfer_transaction_hash ON tbl_token_ownerships (transfer_transaction_hash);
-- NOTE(krishan711): this is O(10m) rows and fills O(10k) per day
ALTER TABLE tbl_token_ownerships SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tbl_token_ownerships SET (autovacuum_analyze_scale_factor = 0.001);


CREATE TABLE tbl_token_multi_ownerships (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    quantity NUMERIC(256, 0) NOT NULL,
    average_transfer_value NUMERIC(256, 0) NOT NULL,
    latest_transfer_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    latest_transfer_transaction_hash TEXT NOT NULL
);
CREATE UNIQUE INDEX tbl_token_multi_ownerships_registry_address_token_id_owner_address ON tbl_token_multi_ownerships (registry_address, token_id, owner_address);
CREATE INDEX tbl_token_multi_ownerships_registry_address_token_id_updated_date ON tbl_token_multi_ownerships (registry_address, token_id, updated_date);
CREATE INDEX tbl_token_multi_ownerships_owner_address_quantity_latest_transfer_date ON tbl_token_multi_ownerships (owner_address, quantity, latest_transfer_date);
CREATE INDEX tbl_token_multi_ownerships_owner_address_latest_transfer_date ON tbl_token_multi_ownerships (owner_address, latest_transfer_date);
CREATE INDEX tbl_token_multi_ownerships_registry_address_token_id ON tbl_token_multi_ownerships (registry_address, token_id);
CREATE INDEX tbl_token_multi_ownerships_created_date ON tbl_token_multi_ownerships (created_date);
CREATE INDEX tbl_token_multi_ownerships_updated_date ON tbl_token_multi_ownerships (updated_date);
CREATE INDEX tbl_token_multi_ownerships_regsitry_address ON tbl_token_multi_ownerships (registry_address);
CREATE INDEX tbl_token_multi_ownerships_token_id ON tbl_token_multi_ownerships (token_id);
CREATE INDEX tbl_token_multi_ownerships_owner_address ON tbl_token_multi_ownerships (owner_address);
CREATE INDEX tbl_token_multi_ownerships_latest_transfer_date ON tbl_token_multi_ownerships (latest_transfer_date);
CREATE INDEX tbl_token_multi_ownerships_latest_transfer_value ON tbl_token_multi_ownerships (latest_transfer_value);
CREATE INDEX tbl_token_multi_ownerships_latest_transfer_transaction_hash ON tbl_token_multi_ownerships (latest_transfer_transaction_hash);
-- NOTE(krishan711): this is O(10m) rows and fills O(10k) per day
ALTER TABLE tbl_token_multi_ownerships SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tbl_token_multi_ownerships SET (autovacuum_analyze_scale_factor = 0.001);


CREATE TABLE tbl_collection_hourly_activities (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    address TEXT NOT NULL,
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    transfer_count NUMERIC(256, 0) NOT NULL,
    mint_count NUMERIC(256, 0) NOT NULL,
    sale_count NUMERIC(256, 0) NOT NULL,
    total_value NUMERIC(256, 0) NOT NULL,
    minimum_value NUMERIC(256, 0) NOT NULL,
    maximum_value NUMERIC(256, 0) NOT NULL,
    average_value NUMERIC(256, 0) NOT NULL
);
CREATE UNIQUE INDEX tbl_collection_hourly_activities_address_date ON tbl_collection_hourly_activities (address, date);
CREATE INDEX tbl_collection_hourly_activities_created_date ON tbl_collection_hourly_activities (created_date);
CREATE INDEX tbl_collection_hourly_activities_updated_date ON tbl_collection_hourly_activities (updated_date);
CREATE INDEX tbl_collection_hourly_activities_address ON tbl_collection_hourly_activities (address);
CREATE INDEX tbl_collection_hourly_activities_date ON tbl_collection_hourly_activities (date);
CREATE INDEX tbl_collection_hourly_activities_transfer_count ON tbl_collection_hourly_activities (transfer_count);
CREATE INDEX tbl_collection_hourly_activities_sale_count ON tbl_collection_hourly_activities (sale_count);
CREATE INDEX tbl_collection_hourly_activities_mint_count ON tbl_collection_hourly_activities (mint_count);
CREATE INDEX tbl_collection_hourly_activities_total_value ON tbl_collection_hourly_activities (total_value);
CREATE INDEX tbl_collection_hourly_activities_minimum_value ON tbl_collection_hourly_activities (minimum_value);
CREATE INDEX tbl_collection_hourly_activities_maximum_value ON tbl_collection_hourly_activities (maximum_value);
CREATE INDEX tbl_collection_hourly_activities_average_value ON tbl_collection_hourly_activities (average_value);
-- NOTE(krishan711): this is O(10m) rows and fills O(10k) per day
ALTER TABLE tbl_collection_hourly_activities SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tbl_collection_hourly_activities SET (autovacuum_analyze_scale_factor = 0.001);


CREATE TABLE tbl_user_interactions (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    user_address TEXT NOT NULL,
    command TEXT NOT NULL,
    signature TEXT NOT NULL,
    message JSONB NOT NULL
);
CREATE INDEX tbl_user_interactions_created_date ON tbl_user_interactions (created_date);
CREATE INDEX tbl_user_interactions_updated_date ON tbl_user_interactions (updated_date);
CREATE INDEX tbl_user_interactions_date ON tbl_user_interactions (date);
CREATE INDEX tbl_user_interactions_user_address ON tbl_user_interactions (user_address);
CREATE INDEX tbl_user_interactions_command ON tbl_user_interactions (command);
CREATE INDEX tbl_user_interactions_user_address_command ON tbl_user_interactions (user_address, command);
CREATE INDEX tbl_user_interactions_message ON tbl_user_interactions USING GIN (message);


CREATE TABLE tbl_latest_updates (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    key TEXT NOT NULL,
    name TEXT ,
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX tbl_latest_updates_key_name on tbl_latest_updates (key, name);
CREATE INDEX tbl_latest_updates_created_date ON tbl_latest_updates (created_date);
CREATE INDEX tbl_latest_updates_updated_date ON tbl_latest_updates (updated_date);
CREATE INDEX tbl_latest_updates_date ON tbl_latest_updates (date);
CREATE INDEX tbl_latest_updates_key ON tbl_latest_updates (key);
CREATE INDEX tbl_latest_updates_name ON tbl_latest_updates (name);


CREATE TABLE tbl_latest_token_listings (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    offerer_address TEXT NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    start_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    is_value_native BOOLEAN NOT NULL,
    value NUMERIC(256, 0) NOT NULL,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL
);
CREATE INDEX tbl_latest_token_listings_source_registry_address_token_id_offerer_address ON tbl_latest_token_listings (source, registry_address, token_id, offerer_address);
CREATE INDEX tbl_latest_token_listings_registry_address_token_id_value ON tbl_latest_token_listings (registry_address, token_id, value);
CREATE INDEX tbl_latest_token_listings_registry_address_token_id_offerer_address ON tbl_latest_token_listings (registry_address, token_id, offerer_address);
CREATE INDEX tbl_latest_token_listings_created_date ON tbl_latest_token_listings (created_date);
CREATE INDEX tbl_latest_token_listings_updated_date ON tbl_latest_token_listings (updated_date);


CREATE TABLE tbl_token_attributes (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    name TEXT NOT NULL,
    value TEXT
);
CREATE UNIQUE INDEX tbl_token_attributes_registry_address_token_id_name on tbl_token_attributes (registry_address, token_id, name);
CREATE INDEX tbl_token_attributes_registry_address_token_id_name_value on tbl_token_attributes (registry_address, token_id, name, value);
CREATE INDEX tbl_token_attributes_registry_address_name_value on tbl_token_attributes (registry_address, name, value);
CREATE INDEX tbl_token_attributes_created_date ON tbl_token_attributes (created_date);
CREATE INDEX tbl_token_attributes_updated_date ON tbl_token_attributes (updated_date);
CREATE INDEX tbl_token_attributes_registry_address ON tbl_token_attributes (registry_address);
CREATE INDEX tbl_token_attributes_name ON tbl_token_attributes (name);
CREATE INDEX tbl_token_attributes_value ON tbl_token_attributes (value);


CREATE TABLE tbl_token_customizations (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    creator_address TEXT NOT NULL,
    signature TEXT NOT NULL,
    block_number INT NOT NULL,
    name TEXT,
    description TEXT
);
CREATE UNIQUE INDEX tbl_token_customizations_registry_address_token_id on tbl_token_customizations (registry_address, token_id);
CREATE INDEX tbl_token_customizations_created_date ON tbl_token_customizations (created_date);
CREATE INDEX tbl_token_customizations_updated_date ON tbl_token_customizations (updated_date);
CREATE INDEX tbl_token_customizations_registry_address_token_id_creator_address on tbl_token_customizations (registry_address, token_id, creator_address);


CREATE TABLE tbl_locks (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    name TEXT NOT NULL,
    expiry_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX tbl_locks_name on tbl_locks (name);
CREATE INDEX tbl_locks_created_date ON tbl_locks (created_date);
CREATE INDEX tbl_locks_updated_date ON tbl_locks (updated_date);


CREATE TABLE tbl_twitter_credentials (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    twitter_id TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expiry_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX tbl_twitter_credentials_twitter_id on tbl_twitter_credentials (twitter_id);
CREATE INDEX tbl_twitter_credentials_created_date ON tbl_twitter_credentials (created_date);
CREATE INDEX tbl_twitter_credentials_updated_date ON tbl_twitter_credentials (updated_date);


CREATE TABLE tbl_twitter_profiles (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    twitter_id TEXT NOT NULL,
    username TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    is_verified BOOLEAN NOT NULL,
    pinned_tweet_id TEXT,
    follower_count INTEGER NOT NULL,
    following_count INTEGER NOT NULL,
    tweet_count INTEGER NOT NULL
);
CREATE UNIQUE INDEX tbl_twitter_profiles_twitter_id on tbl_twitter_profiles (twitter_id);
CREATE UNIQUE INDEX tbl_twitter_profiles_username ON tbl_twitter_profiles (username);
CREATE INDEX tbl_twitter_profiles_created_date ON tbl_twitter_profiles (created_date);
CREATE INDEX tbl_twitter_profiles_updated_date ON tbl_twitter_profiles (updated_date);
CREATE INDEX tbl_twitter_profiles_follower_count ON tbl_twitter_profiles (follower_count);


CREATE TABLE tbl_user_profiles (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    address TEXT NOT NULL,
    twitter_id TEXT,
    discord_id TEXT,
    signature JSON NOT NULL
);
CREATE UNIQUE INDEX tbl_user_profiles_address on tbl_user_profiles (address);
CREATE INDEX tbl_user_profiles_created_date ON tbl_user_profiles (created_date);
CREATE INDEX tbl_user_profiles_updated_date ON tbl_user_profiles (updated_date);
CREATE INDEX tbl_user_profiles_twitter_id ON tbl_user_profiles (twitter_id);


CREATE TABLE tbl_gallery_customers (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    name TEXT NOT NULL,
    registry_address TEXT NOT NULL
);
CREATE UNIQUE INDEX tbl_gallery_customers_registry_address on tbl_gallery_customers (registry_address);

CREATE TABLE tbl_collection_total_activities (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    address TEXT NOT NULL,
    transfer_count NUMERIC(256, 0) NOT NULL,
    mint_count NUMERIC(256, 0) NOT NULL,
    sale_count NUMERIC(256, 0) NOT NULL,
    total_value NUMERIC(256, 0) NOT NULL,
    minimum_value NUMERIC(256, 0) NOT NULL,
    maximum_value NUMERIC(256, 0) NOT NULL,
    average_value NUMERIC(256, 0) NOT NULL
);
CREATE UNIQUE INDEX tbl_collection_total_activities_address on tbl_collection_total_activities (address);
CREATE INDEX tbl_collection_total_activities_created_date ON tbl_collection_total_activities (created_date);
CREATE INDEX tbl_collection_total_activities_updated_date ON tbl_collection_total_activities (updated_date);
CREATE INDEX tbl_collection_total_activities_transfer_count ON tbl_collection_total_activities (transfer_count);
CREATE INDEX tbl_collection_total_activities_mint_count ON tbl_collection_total_activities (mint_count);
CREATE INDEX tbl_collection_total_activities_sale_count ON tbl_collection_total_activities (sale_count);
CREATE INDEX tbl_collection_total_activities_total_value ON tbl_collection_total_activities (total_value);
CREATE INDEX tbl_collection_total_activities_minimum_value ON tbl_collection_total_activities (minimum_value);
CREATE INDEX tbl_collection_total_activities_maximum_value ON tbl_collection_total_activities (maximum_value);
CREATE INDEX tbl_collection_total_activities_average_value ON tbl_collection_total_activities (average_value);

CREATE TABLE tbl_account_gms (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    address TEXT NOT NULL,
    delegate_address TEXT,
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    streak_length INTEGER NOT NULL,
    collection_count INTEGER NOT NULL,
    signature_message TEXT NOT NULL,
    signature TEXT NOT NULL
);
CREATE UNIQUE INDEX tbl_account_gms_address_date on tbl_account_gms (address, date);
CREATE INDEX tbl_account_gms_created_date ON tbl_account_gms (created_date);
CREATE INDEX tbl_account_gms_updated_date ON tbl_account_gms (updated_date);
CREATE INDEX tbl_account_gms_address ON tbl_account_gms (address);
CREATE INDEX tbl_account_gms_date ON tbl_account_gms (date);

CREATE TABLE tbl_account_collection_gms (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    account_address TEXT NOT NULL,
    account_delegate_address TEXT,
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    signature_message TEXT NOT NULL,
    signature TEXT NOT NULL
);
CREATE UNIQUE INDEX tbl_account_collection_gms_registry_address_account_address_date on tbl_account_collection_gms (registry_address, account_address, date);
CREATE INDEX tbl_account_collection_gms_created_date ON tbl_account_collection_gms (created_date);
CREATE INDEX tbl_account_collection_gms_updated_date ON tbl_account_collection_gms (updated_date);
CREATE INDEX tbl_account_collection_gms_registry_address ON tbl_account_collection_gms (registry_address);
CREATE INDEX tbl_account_collection_gms_account_address ON tbl_account_collection_gms (account_address);
CREATE INDEX tbl_account_collection_gms_registry_address_date ON tbl_account_collection_gms (registry_address, date);
CREATE INDEX tbl_account_collection_gms_date ON tbl_account_collection_gms (date);

CREATE TABLE tbl_collection_overlaps (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    other_registry_address TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    registry_token_count NUMERIC(256, 0) NOT NULL,
    other_registry_token_count NUMERIC(256, 0) NOT NULL
);
CREATE UNIQUE INDEX tbl_collection_overlaps_owner_address_registry_address_other_registry_address on tbl_collection_overlaps (owner_address, registry_address, other_registry_address);
CREATE INDEX tbl_collection_overlaps_created_date ON tbl_collection_overlaps (created_date);
CREATE INDEX tbl_collection_overlaps_updated_date ON tbl_collection_overlaps (updated_date);
CREATE INDEX tbl_collection_overlaps_registry_address_other_registry_address ON tbl_collection_overlaps (registry_address, other_registry_address);
CREATE INDEX tbl_collection_overlaps_registry_address_owner_address ON tbl_collection_overlaps (registry_address, owner_address);
CREATE INDEX tbl_collection_overlaps_other_registry_address_owner_address ON tbl_collection_overlaps (other_registry_address, owner_address);
CREATE INDEX tbl_collection_overlaps_registry_address ON tbl_collection_overlaps (registry_address);
CREATE INDEX tbl_collection_overlaps_other_registry_address ON tbl_collection_overlaps (other_registry_address);
CREATE INDEX tbl_collection_overlaps_owner_address ON tbl_collection_overlaps (owner_address);
CREATE INDEX tbl_collection_overlaps_registry_token_count ON tbl_collection_overlaps (registry_token_count);


CREATE TABLE tbl_gallery_badge_holders (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    badge_key TEXT NOT NULL,
    achieved_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX tbl_gallery_badge_holders_owner_address_registry_address_badge_key on tbl_gallery_badge_holders (owner_address, registry_address, badge_key);
CREATE INDEX tbl_gallery_badge_holders_created_date ON tbl_gallery_badge_holders (created_date);
CREATE INDEX tbl_gallery_badge_holders_updated_date ON tbl_gallery_badge_holders (updated_date);
CREATE INDEX tbl_gallery_badge_holders_registry_address ON tbl_gallery_badge_holders (registry_address);
CREATE INDEX tbl_gallery_badge_holders_badge_key ON tbl_gallery_badge_holders (badge_key);
CREATE INDEX tbl_gallery_badge_holders_owner_address ON tbl_gallery_badge_holders (owner_address);
CREATE INDEX tbl_gallery_badge_holders_achieved_date ON tbl_gallery_badge_holders (achieved_date);

CREATE TABLE tbl_gallery_badge_assignments (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    badge_key TEXT NOT NULL,
    achieved_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    assigner_address TEXT NOT NULL,
    signature_message TEXT NOT NULL,
    signature TEXT NOT NULL
);
CREATE UNIQUE INDEX tbl_gallery_badge_assignments_owner_address_registry_address_badge_key on tbl_gallery_badge_assignments (owner_address, registry_address, badge_key);
CREATE INDEX tbl_gallery_badge_assignments_created_date ON tbl_gallery_badge_assignments (created_date);
CREATE INDEX tbl_gallery_badge_assignments_updated_date ON tbl_gallery_badge_assignments (updated_date);
CREATE INDEX tbl_gallery_badge_assignments_registry_address ON tbl_gallery_badge_assignments (registry_address);
CREATE INDEX tbl_gallery_badge_assignments_assigner_address ON tbl_gallery_badge_assignments (assigner_address);
CREATE INDEX tbl_gallery_badge_assignments_badge_key ON tbl_gallery_badge_assignments (badge_key);
CREATE INDEX tbl_gallery_badge_assignments_owner_address ON tbl_gallery_badge_assignments (owner_address);
CREATE INDEX tbl_gallery_badge_assignments_achieved_date ON tbl_gallery_badge_assignments (achieved_date);

CREATE TABLE tbl_token_stakings (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    staking_address TEXT NOT NULL,
    owner_address TEXT NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    staked_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    transaction_hash TEXT NOT NULL
);

CREATE UNIQUE INDEX tbl_token_stakings_regsitry_address_staking_address_owner_address_token_id ON tbl_token_stakings (registry_address, staking_address, owner_address, token_id);
CREATE INDEX tbl_token_stakings_created_date ON tbl_token_stakings (created_date);
CREATE INDEX tbl_token_stakings_updated_date ON tbl_token_stakings (updated_date);
CREATE INDEX tbl_token_stakings_registry_address_token_id ON tbl_token_stakings (registry_address, token_id);
CREATE INDEX tbl_token_stakings_registry_address ON tbl_token_stakings (registry_address);
CREATE INDEX tbl_token_stakings_staking_address ON tbl_token_stakings (staking_address);
CREATE INDEX tbl_token_stakings_owner_address ON tbl_token_stakings (owner_address);
CREATE INDEX tbl_token_stakings_staked_date ON tbl_token_stakings (staked_date);
CREATE INDEX tbl_token_stakings_token_id ON tbl_token_stakings (token_id);
CREATE INDEX tbl_token_stakings_transaction_hash ON tbl_token_stakings (transaction_hash);

CREATE TABLE tbl_subcontract_tokens (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    collection_name TEXT NOT NULL,
    token_id TEXT NOT NULL,
);

CREATE UNIQUE INDEX tbl_subcontract_tokens_registry_address_token_id ON tbl_subcontract_tokens (registry_address, token_id);
CREATE INDEX tbl_subcontract_tokens_created_date ON tbl_subcontract_tokens (created_date);
CREATE INDEX tbl_subcontract_tokens_updated_date ON tbl_subcontract_tokens (updated_date);
CREATE INDEX tbl_subcontract_tokens_collection_name ON tbl_subcontract_tokens (collection_name);
CREATE INDEX tbl_subcontract_tokens_registry_address ON tbl_subcontract_tokens (registry_address);
CREATE INDEX tbl_subcontract_tokens_token_id ON tbl_subcontract_tokens (token_id);
