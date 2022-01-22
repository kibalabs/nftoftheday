CREATE TABLE tbl_token_transfers (
    id BIGSERIAL PRIMARY KEY,
    transaction_hash TEXT NOT NULL,
    registry_address TEXT NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    -- NOTE(krishan711): operator_address should be NOT NULL once filled
    operator_address TEXT,
    token_id TEXT NOT NULL,
    value NUMERIC(256, 0) NOT NULL,
    -- NOTE(krishan711): amount should be NOT NULL once filled
    amount INTEGER,
    gas_limit NUMERIC(256, 0) NOT NULL,
    gas_price NUMERIC(256, 0) NOT NULL,
    gas_used NUMERIC(256, 0) NOT NULL,
    block_number INTEGER NOT NULL,
    block_hash TEXT NOT NULL,
    block_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    -- NOTE(krishan711): token_type should be NOT NULL once filled
    token_type TEXT
);
CREATE UNIQUE INDEX tbl_token_transfers_transaction_hash_registry_address_token_id_from_address_to_address ON tbl_token_transfers (transaction_hash, registry_address, token_id, from_address, to_address);
CREATE INDEX tbl_token_transfers_registry_address ON tbl_token_transfers (registry_address);
CREATE INDEX tbl_token_transfers_token_id ON tbl_token_transfers (token_id);
CREATE INDEX tbl_token_transfers_value ON tbl_token_transfers (value);
CREATE INDEX tbl_token_transfers_block_date ON tbl_token_transfers (block_date);
CREATE INDEX tbl_token_transfers_block_number ON tbl_token_transfers (block_number);
CREATE INDEX tbl_token_transfers_block_hash ON tbl_token_transfers (block_hash);
CREATE INDEX tbl_token_transfers_to_address ON tbl_token_transfers (to_address);
CREATE INDEX tbl_token_transfers_from_address ON tbl_token_transfers (from_address);
CREATE INDEX tbl_token_transfers_operator_address ON tbl_token_transfers (operator_address);
CREATE INDEX tbl_token_transfers_token_type ON tbl_token_transfers (token_type);

CREATE TABLE tbl_token_metadatas (
    id BIGSERIAL PRIMARY KEY,
    created_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    updated_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    registry_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    metadata_url TEXT NOT NULL,
    image_url TEXT,
    name TEXT,
    description TEXT,
    attributes JSON
);
CREATE UNIQUE INDEX tbl_tokens_metadatas_registry_address_token_id ON tbl_token_metadatas (registry_address, token_id);
CREATE INDEX tbl_token_metadatas_registry_address ON tbl_token_metadatas (registry_address);
CREATE INDEX tbl_token_metadatas_token_id ON tbl_token_metadatas (token_id);
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
    does_support_erc721 BOOLEAN,
    does_support_erc1155 BOOLEAN
);
CREATE UNIQUE INDEX tbl_collections_address ON tbl_collections (address);
CREATE INDEX tbl_collections_name ON tbl_collections (name);
