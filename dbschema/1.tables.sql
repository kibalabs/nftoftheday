CREATE TABLE tbl_token_transfers (
    id BIGSERIAL PRIMARY KEY,
    transaction_hash TEXT NOT NULL,
    registry_address TEXT NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    operator_address TEXT NOT NULL,
    contract_address TEXT,
    token_id TEXT NOT NULL,
    value NUMERIC(256, 0) NOT NULL,
    amount_2 NUMERIC(256, 0) NOT NULL,
    gas_limit NUMERIC(256, 0) NOT NULL,
    gas_price NUMERIC(256, 0) NOT NULL,
    block_number INTEGER NOT NULL,
    token_type TEXT NOT NULL,
    is_multi_address BOOLEAN,
    is_interstitial BOOLEAN,
    is_swap BOOLEAN,
    is_batch BOOLEAN,
    is_outbound BOOLEAN
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


CREATE TABLE tbl_token_metadatas (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    metadata_url TEXT,
    image_url TEXT,
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

CREATE TABLE tbl_collection_hourly_activities (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    address TEXT NOT NULL,
    date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    transfer_count NUMERIC(256, 0) NOT NULL,
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
CREATE INDEX tbl_collection_hourly_activities_total_value ON tbl_collection_hourly_activities (total_value);
CREATE INDEX tbl_collection_hourly_activities_minimum_value ON tbl_collection_hourly_activities (minimum_value);
CREATE INDEX tbl_collection_hourly_activities_maximum_value ON tbl_collection_hourly_activities (maximum_value);
CREATE INDEX tbl_collection_hourly_activities_average_value ON tbl_collection_hourly_activities (average_value);

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
CREATE UNIQUE INDEX tbl_latest_token_listings_source_registry_address_token_id_offerer_address ON tbl_latest_token_listings (source, registry_address, token_id, offerer_address);
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
CREATE UNIQUE INDEX tbl_token_attributes_registry_address_token_id_attribute_name on tbl_token_attributes (registry_address, token_id, attribute_name);
CREATE INDEX tbl_token_attributes_created_date ON tbl_token_attributes (created_date);
CREATE INDEX tbl_token_attributes_updated_date ON tbl_token_attributes (updated_date);
CREATE INDEX tbl_token_attributes_registry_address ON tbl_token_attributes (registry_address);
CREATE INDEX tbl_token_attributes_token_id ON tbl_token_attributes (token_id);
CREATE INDEX tbl_token_attributes_attribute_name ON tbl_token_attributes (attribute_name);
CREATE INDEX tbl_token_attributes_attribute_value ON tbl_token_attributes (attribute_value);
