import sqlalchemy

metadata = sqlalchemy.MetaData()

TokenTransfersTable = sqlalchemy.Table('tbl_token_transfers', metadata,
    sqlalchemy.Column(key='tokenTransferId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='transactionHash', name='transaction_hash', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='fromAddress', name='from_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='toAddress', name='to_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='operatorAddress', name='operator_address', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='value', name='value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='amount', name='amount', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='gasLimit', name='gas_limit', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='gasPrice', name='gas_price', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='gasUsed', name='gas_used', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='blockNumber', name='block_number', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='blockHash', name='block_hash', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='blockDate', name='block_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='tokenType', name='token_type', type_=sqlalchemy.Text, nullable=False),
)

TokenMetadataTable = sqlalchemy.Table(
    'tbl_token_metadatas',
    metadata,
    sqlalchemy.Column(key='tokenMetadataId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='metadataUrl', name='metadata_url', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='imageUrl', name='image_url', type_=sqlalchemy.TEXT, nullable=True),
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
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column(key='symbol', name='symbol', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='description', name='description', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='imageUrl', name='image_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='twitterUsername', name='twitter_username', type_=sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column(key='instagramUsername', name='instagram_username', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='wikiUrl', name='wiki_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='openseaSlug', name='opensea_slug', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='url', name='url', type_=sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column(key='discordUrl', name='discord_url', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='bannerImageUrl', name='banner_image_url', type_=sqlalchemy.Text, nullable=True)
)
