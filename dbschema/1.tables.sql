CREATE TABLE tbl_token_transfers (
    id BIGSERIAL PRIMARY KEY,
    transaction_hash TEXT NOT NULL,
    registry_address TEXT NOT NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    token_id TEXT NOT NULL,
    value NUMERIC(256, 0) NOT NULL,
    gas_limit NUMERIC(256, 0) NOT NULL,
    gas_price NUMERIC(256, 0) NOT NULL,
    gas_used NUMERIC(256, 0) NOT NULL,
    block_number INTEGER NOT NULL,
    block_hash TEXT NOT NULL,
    block_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE UNIQUE INDEX tbl_token_transfers_transaction_hash_registry_address_token_id ON tbl_token_transfers (transaction_hash, registry_address, token_id);
CREATE INDEX tbl_token_transfers_registry_address ON tbl_token_transfers (registry_address);
CREATE INDEX tbl_token_transfers_token_id ON tbl_token_transfers (token_id);
CREATE INDEX tbl_token_transfers_value ON tbl_token_transfers (value);
CREATE INDEX tbl_token_transfers_block_date ON tbl_token_transfers (block_date);
