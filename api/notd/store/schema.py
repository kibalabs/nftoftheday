import sqlalchemy

metadata = sqlalchemy.MetaData()

TokenTransfersTable = sqlalchemy.Table('tbl_token_transfers', metadata,
    sqlalchemy.Column(key='tokenTransferId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='transactionHash', name='transaction_hash', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='fromAddress', name='from_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='toAddress', name='to_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='operatorAddress', name='operator_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='value', name='value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    # NOTE(krishan711): switch back to amount once its renamed
    sqlalchemy.Column(key='amount', name='amount_2', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='gasLimit', name='gas_limit', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='gasPrice', name='gas_price', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='blockNumber', name='block_number', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='tokenType', name='token_type', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='isMultiAddress', name='is_multi_address', type_=sqlalchemy.BOOLEAN, nullable=False),
    sqlalchemy.Column(key='isInterstitialTransfer', name='is_interstitial_transfer', type_=sqlalchemy.BOOLEAN, nullable=False),

)

BlocksTable = sqlalchemy.Table(
    'tbl_blocks',
    metadata,
    sqlalchemy.Column(key='blockId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='blockNumber', name='block_number', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='blockHash', name='block_hash', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='blockDate', name='block_date', type_=sqlalchemy.DateTime, nullable=False),
)

TokenMetadatasTable = sqlalchemy.Table(
    'tbl_token_metadatas',
    metadata,
    sqlalchemy.Column(key='tokenMetadataId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='metadataUrl', name='metadata_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='imageUrl', name='image_url', type_=sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column(key='animationUrl', name='animation_url', type_=sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column(key='youtubeUrl', name='youtube_url', type_=sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column(key='backgroundColor', name='background_color', type_=sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column(key='frameImageUrl', name='frame_image_url', type_=sqlalchemy.TEXT, nullable=True),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='description', name='description', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='attributes', name='attributes', type_=sqlalchemy.JSON, nullable=True),
)

TokenCollectionsTable = sqlalchemy.Table(
    'tbl_collections',
    metadata,
    sqlalchemy.Column(key='collectionId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='address', name='address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='symbol', name='symbol', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='description', name='description', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='imageUrl', name='image_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='twitterUsername', name='twitter_username', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='instagramUsername', name='instagram_username', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='wikiUrl', name='wiki_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='openseaSlug', name='opensea_slug', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='url', name='url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='discordUrl', name='discord_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='bannerImageUrl', name='banner_image_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='doesSupportErc721', name='does_support_erc721', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='doesSupportErc1155', name='does_support_erc1155', type_=sqlalchemy.Boolean, nullable=False),
)

TokenOwnershipsTable = sqlalchemy.Table(
    'tbl_token_ownerships',
    metadata,
    sqlalchemy.Column(key='tokenOwnershipId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='transferValue', name='transfer_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='transferDate', name='transfer_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='transferTransactionHash', name='transfer_transaction_hash', type_=sqlalchemy.Text, nullable=False),
)

TokenMultiOwnershipsTable = sqlalchemy.Table(
    'tbl_token_multi_ownerships',
    metadata,
    sqlalchemy.Column(key='tokenMultiOwnershipId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='quantity', name='quantity', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='averageTransferValue', name='average_transfer_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='latestTransferDate', name='latest_transfer_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='latestTransferTransactionHash', name='latest_transfer_transaction_hash', type_=sqlalchemy.Text, nullable=False),
)

CollectionHourlyActivityTable = sqlalchemy.Table(
    'tbl_collection_hourly_activities',
    metadata,
    sqlalchemy.Column(key='collectionActivityId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='address', name='address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='date', name='date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='transferCount', name='transfer_count', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='saleCount', name='sale_count', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='totalValue', name='total_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='minimumValue', name='minimum_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='maximumValue', name='maximum_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='averageValue', name='average_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
)
