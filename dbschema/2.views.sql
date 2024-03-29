CREATE MATERIALIZED VIEW mvw_user_registry_first_ownerships AS (
    SELECT tbl_token_transfers.registry_address, tbl_token_transfers.to_address AS owner_address, min(tbl_blocks.block_date) AS join_date
    FROM tbl_blocks
    JOIN tbl_token_transfers ON tbl_token_transfers.block_number = tbl_blocks.block_number
    WHERE tbl_token_transfers.registry_address = ANY(array(select registry_address from tbl_gallery_customers))
    GROUP BY tbl_token_transfers.registry_address, tbl_token_transfers.to_address
);
CREATE UNIQUE INDEX mvw_user_registry_first_ownerships_registry_address_owner_address ON mvw_user_registry_first_ownerships (registry_address, owner_address);
CREATE INDEX mvw_user_registry_first_ownerships_registry_address ON mvw_user_registry_first_ownerships (registry_address);


CREATE MATERIALIZED VIEW mvw_user_registry_ordered_ownerships AS (
    (
        SELECT tbl_token_metadatas.registry_address, tbl_token_metadatas.token_id, tbl_token_stakings.owner_address, 1 AS quantity, row_number() OVER (
            PARTITION BY tbl_token_stakings.registry_address, tbl_token_stakings.owner_address
            ORDER BY tbl_token_stakings.staked_date, tbl_token_stakings.token_id ASC
        ) AS owner_token_index
        FROM tbl_token_metadatas
        JOIN tbl_token_stakings ON tbl_token_stakings.token_id = tbl_token_metadatas.token_id
            AND tbl_token_stakings.registry_address = tbl_token_metadatas.registry_address
        WHERE tbl_token_stakings.registry_address = ANY(array(select registry_address from tbl_gallery_customers))
    ) UNION (
        SELECT tbl_token_metadatas.registry_address, tbl_token_metadatas.token_id, tbl_token_ownerships.owner_address, 1 AS quantity, row_number() OVER (
            PARTITION BY tbl_token_ownerships.registry_address, tbl_token_ownerships.owner_address
            ORDER BY tbl_token_ownerships.transfer_date, tbl_token_ownerships.token_id ASC
        ) AS owner_token_index
        FROM tbl_token_metadatas
        JOIN tbl_token_ownerships ON tbl_token_ownerships.token_id = tbl_token_metadatas.token_id
            AND tbl_token_ownerships.registry_address = tbl_token_metadatas.registry_address
        WHERE tbl_token_ownerships.registry_address = ANY(array(select registry_address from tbl_gallery_customers))
        AND ((tbl_token_ownerships.registry_address, tbl_token_ownerships.token_id) not in (select registry_address, token_id from tbl_token_stakings))
    ) UNION (
        SELECT tbl_token_metadatas.registry_address, tbl_token_metadatas.token_id, tbl_token_multi_ownerships.owner_address, tbl_token_multi_ownerships.quantity, row_number() OVER (
            PARTITION BY tbl_token_multi_ownerships.registry_address, tbl_token_multi_ownerships.owner_address
            ORDER BY tbl_token_multi_ownerships.latest_transfer_date, tbl_token_multi_ownerships.token_id ASC
        ) AS owner_token_index
        FROM tbl_token_metadatas
        JOIN tbl_token_multi_ownerships ON tbl_token_multi_ownerships.token_id = tbl_token_metadatas.token_id
            AND tbl_token_multi_ownerships.registry_address = tbl_token_metadatas.registry_address
            AND tbl_token_multi_ownerships.quantity > 0
        WHERE tbl_token_multi_ownerships.registry_address = ANY(array(select registry_address from tbl_gallery_customers))
        AND ((tbl_token_multi_ownerships.registry_address, tbl_token_multi_ownerships.token_id) not in (select registry_address, token_id from tbl_token_stakings))
    )
);
CREATE UNIQUE INDEX mvw_user_registry_ordered_ownerships_registry_address_token_id_owner_address ON mvw_user_registry_ordered_ownerships (registry_address, token_id, owner_address);
CREATE INDEX mvw_user_registry_ordered_ownerships_registry_address ON mvw_user_registry_ordered_ownerships (registry_address);
CREATE INDEX mvw_user_registry_ordered_ownerships_registry_address_token_id ON mvw_user_registry_ordered_ownerships (registry_address, token_id);
CREATE INDEX mvw_user_registry_ordered_ownerships_registry_address_owner_address ON mvw_user_registry_ordered_ownerships (registry_address, owner_address);

CREATE VIEW vw_token_ownerships AS
(
    SELECT id, created_date, updated_date, registry_address, token_id, owner_address, transfer_value AS average_transfer_value, transfer_date AS latest_transfer_date, transfer_transaction_hash AS latest_transfer_transaction_hash, 1 AS quantity
    FROM tbl_token_ownerships
)
UNION
(
    SELECT id, created_date, updated_date, registry_address, token_id, owner_address, average_transfer_value, latest_transfer_date, latest_transfer_transaction_hash, quantity
    FROM tbl_token_multi_ownerships
);

CREATE VIEW vw_ordered_token_listings AS
(
    SELECT tbl_latest_token_listings.*, row_number() OVER (
        PARTITION BY tbl_latest_token_listings.registry_address, tbl_latest_token_listings.token_id
        ORDER BY tbl_latest_token_listings.value ASC
    ) AS token_listing_index
    FROM tbl_latest_token_listings
    JOIN vw_token_ownerships ON
        vw_token_ownerships.registry_address = tbl_latest_token_listings.registry_address
        AND vw_token_ownerships.token_id = tbl_latest_token_listings.token_id
        AND vw_token_ownerships.owner_address = tbl_latest_token_listings.offerer_address
        AND vw_token_ownerships.quantity > 0
    WHERE tbl_latest_token_listings.end_date > now()
);

CREATE VIEW vw_gallery_badge_holders AS
(
    SELECT id, created_date, updated_date, registry_address, owner_address, badge_key, achieved_date
    FROM tbl_gallery_badge_holders
)
UNION
(
    SELECT id, created_date, updated_date, registry_address, owner_address, badge_key, achieved_date
    FROM tbl_gallery_badge_assignments
);
