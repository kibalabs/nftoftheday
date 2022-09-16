CREATE USER notd_api;
GRANT USAGE ON SCHEMA public TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_token_transfers TO notd_api;
GRANT ALL ON SEQUENCE tbl_token_transfers_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_token_metadatas TO notd_api;
GRANT ALL ON SEQUENCE tbl_token_metadatas_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_collections TO notd_api;
GRANT ALL ON SEQUENCE tbl_collections_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_blocks TO notd_api;
GRANT ALL ON SEQUENCE tbl_blocks_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_token_ownerships TO notd_api;
GRANT ALL ON SEQUENCE tbl_token_ownerships_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_token_multi_ownerships TO notd_api;
GRANT ALL ON SEQUENCE tbl_token_multi_ownerships_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_collection_hourly_activities TO notd_api;
GRANT ALL ON SEQUENCE tbl_collection_hourly_activities_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_collection_total_activities TO notd_api;
GRANT ALL ON SEQUENCE tbl_collection_total_activities_id_seq TO notd_api;
GRANT INSERT, SELECT ON tbl_user_interactions TO notd_api;
GRANT ALL ON SEQUENCE tbl_user_interactions_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_latest_updates TO notd_api;
GRANT ALL ON SEQUENCE tbl_latest_updates_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_latest_token_listings TO notd_api;
GRANT ALL ON SEQUENCE tbl_latest_token_listings_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_token_attributes TO notd_api;
GRANT ALL ON SEQUENCE tbl_token_attributes_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_token_customizations TO notd_api;
GRANT ALL ON SEQUENCE tbl_token_customizations_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE, DELETE ON tbl_locks TO notd_api;
GRANT ALL ON SEQUENCE tbl_locks_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_twitter_credentials TO notd_api;
GRANT ALL ON SEQUENCE tbl_twitter_credentials_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_twitter_profiles TO notd_api;
GRANT ALL ON SEQUENCE tbl_twitter_profiles_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_user_profiles TO notd_api;
GRANT ALL ON SEQUENCE tbl_user_profiles_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_gallery_customers TO notd_api;
GRANT ALL ON SEQUENCE tbl_gallery_customers_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_account_gms TO notd_api;
GRANT ALL ON SEQUENCE tbl_account_gms_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_account_collection_gms TO notd_api;
GRANT ALL ON SEQUENCE tbl_account_collection_gms_id_seq TO notd_api;
GRANT INSERT, SELECT, UPDATE ON tbl_collection_overlaps TO notd_api;
GRANT ALL ON SEQUENCE tbl_collection_overlaps_id_seq TO notd_api;
ALTER MATERIALIZED VIEW mvw_user_registry_first_ownerships OWNER TO notd_api;
ALTER MATERIALIZED VIEW mvw_user_registry_ordered_ownerships OWNER TO notd_api;
