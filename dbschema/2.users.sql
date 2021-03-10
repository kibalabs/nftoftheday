CREATE USER IF NOT EXISTS notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_token_transfers TO notd_api;
