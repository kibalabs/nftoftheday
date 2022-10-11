CREATE MATERIALIZED
VIEW mvw_user_registry_first_ownerships AS
(
    SELECT tbl_token_transfers.registry_address, tbl_token_transfers.to_address AS owner_address, min(tbl_blocks.block_date) AS join_date
FROM tbl_blocks
    JOIN tbl_token_transfers ON tbl_token_transfers.block_number = tbl_blocks.block_number
WHERE tbl_token_transfers.registry_address = ANY(array
(select registry_address
from tbl_gallery_customers)
)
    GROUP BY tbl_token_transfers.registry_address, tbl_token_transfers.to_address
);
CREATE UNIQUE INDEX mvw_user_registry_first_ownerships_registry_address_owner_address ON mvw_user_registry_first_ownerships (registry_address, owner_address);
CREATE INDEX mvw_user_registry_first_ownerships_registry_address ON mvw_user_registry_first_ownerships (registry_address);


CREATE MATERIALIZED VIEW mvw_user_registry_ordered_ownerships AS
(
    (
        SELECT tbl_token_metadatas.registry_address, tbl_token_metadatas.token_id, tbl_token_ownerships.owner_address, 1 as quantity, row_number() OVER (
            PARTITION BY tbl_token_ownerships.registry_address, tbl_token_ownerships.owner_address
            ORDER BY tbl_token_ownerships.transfer_date ASC
        ) AS owner_token_index
FROM tbl_token_metadatas
    JOIN tbl_token_ownerships ON tbl_token_ownerships.token_id = tbl_token_metadatas.token_id
        AND tbl_token_ownerships.registry_address = tbl_token_metadatas.registry_address
WHERE tbl_token_ownerships.registry_address = ANY(array
(select registry_address
from tbl_gallery_customers)
)
    ) UNION
(
        SELECT tbl_token_metadatas.registry_address, tbl_token_metadatas.token_id, tbl_token_multi_ownerships.owner_address, tbl_token_multi_ownerships.quantity, row_number() OVER (
            PARTITION BY tbl_token_multi_ownerships.registry_address, tbl_token_multi_ownerships.owner_address
            ORDER BY tbl_token_multi_ownerships.latest_transfer_date ASC
        ) AS owner_token_index
FROM tbl_token_metadatas
    JOIN tbl_token_multi_ownerships ON tbl_token_multi_ownerships.token_id = tbl_token_metadatas.token_id
        AND tbl_token_multi_ownerships.registry_address = tbl_token_metadatas.registry_address
        AND tbl_token_multi_ownerships.quantity > 0
WHERE tbl_token_multi_ownerships.registry_address = ANY(array
(select registry_address
from tbl_gallery_customers)
)
    )
);
CREATE UNIQUE INDEX mvw_user_registry_ordered_ownerships_registry_address_token_id_owner_address ON mvw_user_registry_ordered_ownerships (registry_address, token_id, owner_address);
CREATE INDEX mvw_user_registry_ordered_ownerships_registry_address ON mvw_user_registry_ordered_ownerships (registry_address);
CREATE INDEX mvw_user_registry_ordered_ownerships_registry_address_token_id ON mvw_user_registry_ordered_ownerships (registry_address, token_id);
CREATE INDEX mvw_user_registry_ordered_ownerships_registry_address_owner_address ON mvw_user_registry_ordered_ownerships (registry_address, owner_address);