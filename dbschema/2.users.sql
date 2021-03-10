CREATE USER IF NOT EXISTS notd_api;
GRANT USAGE ON SCHEMA public TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_token_transfers TO notd_api;
GRANT ALL ON SEQUENCE tbl_token_transfers_id_seq TO notd_api;
