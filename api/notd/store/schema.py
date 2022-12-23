import sqlalchemy

metadata = sqlalchemy.MetaData()

TokenTransfersTable = sqlalchemy.Table(
    'tbl_token_transfers',
    metadata,
    sqlalchemy.Column(key='tokenTransferId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='transactionHash', name='transaction_hash', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='fromAddress', name='from_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='toAddress', name='to_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='operatorAddress', name='operator_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='contractAddress', name='contract_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='value', name='value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    # NOTE(krishan711): switch back to amount once its renamed
    sqlalchemy.Column(key='amount', name='amount_2', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='gasLimit', name='gas_limit', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='gasPrice', name='gas_price', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='blockNumber', name='block_number', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='tokenType', name='token_type', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='isMultiAddress', name='is_multi_address', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='isInterstitial', name='is_interstitial', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='isSwap', name='is_swap', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='isBatch', name='is_batch', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='isOutbound', name='is_outbound', type_=sqlalchemy.Boolean, nullable=False),
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
    sqlalchemy.Column(key='resizableImageUrl', name='resizable_image_url', type_=sqlalchemy.TEXT, nullable=True),
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


TokenOwnershipsView = sqlalchemy.Table(
    'vw_token_ownerships',
    metadata,
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


CollectionHourlyActivitiesTable = sqlalchemy.Table(
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


CollectionTotalActivitiesTable = sqlalchemy.Table(
    'tbl_collection_total_activities',
    metadata,
    sqlalchemy.Column(key='collectionTotalActivityId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='address', name='address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='transferCount', name='transfer_count', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='saleCount', name='sale_count', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='totalValue', name='total_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='minimumValue', name='minimum_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='maximumValue', name='maximum_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='averageValue', name='average_value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
)


UserInteractionsTable = sqlalchemy.Table(
    'tbl_user_interactions',
    metadata,
    sqlalchemy.Column(key='userInteractionId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='date', name='date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='userAddress', name='user_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='command', name='command', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='signature', name='signature', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='message', name='message', type_=sqlalchemy.JSON, nullable=False),
)


LatestUpdatesTable = sqlalchemy.Table(
    'tbl_latest_updates',
    metadata,
    sqlalchemy.Column(key='latestUpdateId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='key', name='key', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='date', name='date', type_=sqlalchemy.DateTime, nullable=False),
)


LatestTokenListingsTable = sqlalchemy.Table(
    'tbl_latest_token_listings',
    metadata,
    sqlalchemy.Column(key='latestTokenListingId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='offererAddress', name='offerer_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='startDate', name='start_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='endDate', name='end_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='isValueNative', name='is_value_native', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='value', name='value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='source', name='source', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='sourceId', name='source_id', type_=sqlalchemy.Text, nullable=False),
)


OrderedTokenListingsView = sqlalchemy.Table(
    'vw_ordered_token_listings',
    metadata,
    sqlalchemy.Column(key='latestTokenListingId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='offererAddress', name='offerer_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='startDate', name='start_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='endDate', name='end_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='isValueNative', name='is_value_native', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='value', name='value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='source', name='source', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='sourceId', name='source_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenListingIndex', name='token_listing_index', type_=sqlalchemy.Integer, nullable=False),
)


TokenAttributesTable = sqlalchemy.Table(
    'tbl_token_attributes',
    metadata,
    sqlalchemy.Column(key='tokenAttributeId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='value', name='value', type_=sqlalchemy.Text, nullable=True),
)


TokenCustomizationsTable = sqlalchemy.Table(
    'tbl_token_customizations',
    metadata,
    sqlalchemy.Column(key='tokenCustomizationId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='creatorAddress', name='creator_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='signature', name='signature', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='blockNumber', name='block_number', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='description', name='description', type_=sqlalchemy.Text, nullable=True),
)


LocksTable = sqlalchemy.Table(
    'tbl_locks',
    metadata,
    sqlalchemy.Column(key='lockId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='expiryDate', name='expiry_date', type_=sqlalchemy.DateTime, nullable=False),
)



TwitterCredentialsTable = sqlalchemy.Table(
    'tbl_twitter_credentials',
    metadata,
    sqlalchemy.Column(key='twitterCredentialId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='twitterId', name='twitter_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='accessToken', name='access_token', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='refreshToken', name='refresh_token', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='expiryDate', name='expiry_date', type_=sqlalchemy.DateTime, nullable=False),
)


TwitterProfilesTable = sqlalchemy.Table(
    'tbl_twitter_profiles',
    metadata,
    sqlalchemy.Column(key='twitterProfileId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='twitterId', name='twitter_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='username', name='username', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='name', name='name', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='description', name='description', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='isVerified', name='is_verified', type_=sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(key='pinnedTweetId', name='pinned_tweet_id', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='followerCount', name='follower_count', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='followingCount', name='following_count', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='tweetCount', name='tweet_count', type_=sqlalchemy.Integer, nullable=False),
)


UserProfilesTable = sqlalchemy.Table(
    'tbl_user_profiles',
    metadata,
    sqlalchemy.Column(key='userProfileId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='address', name='address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='twitterId', name='twitter_id', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='discordId', name='discord_id', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='signature', name='signature', type_=sqlalchemy.JSON, nullable=False),
)


UserRegistryOrderedOwnershipsMaterializedView = sqlalchemy.Table(
    'mvw_user_registry_ordered_ownerships',
    metadata,
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='quantity', name='quantity', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='ownerTokenIndex', name='owner_token_index', type_=sqlalchemy.Integer, nullable=False),
)


UserRegistryFirstOwnershipsMaterializedView = sqlalchemy.Table(
    'mvw_user_registry_first_ownerships',
    metadata,
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='joinDate', name='join_date', type_=sqlalchemy.DateTime, nullable=False),
)


AccountGmsTable = sqlalchemy.Table(
    'tbl_account_gms',
    metadata,
    sqlalchemy.Column(key='accountGmId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='address', name='address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='delegateAddress', name='delegate_address', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='date', name='date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='streakLength', name='streak_length', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='collectionCount', name='collection_count', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(key='signatureMessage', name='signature_message', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='signature', name='signature', type_=sqlalchemy.JSON, nullable=False),
)


AccountCollectionGmsTable = sqlalchemy.Table(
    'tbl_account_collection_gms',
    metadata,
    sqlalchemy.Column(key='accountCollectionGmId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='accountAddress', name='account_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='accountDelegateAddress', name='account_delegate_address', type_=sqlalchemy.Text, nullable=True),
    sqlalchemy.Column(key='date', name='date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='signatureMessage', name='signature_message', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='signature', name='signature', type_=sqlalchemy.JSON, nullable=False),
)


TokenCollectionOverlapsTable = sqlalchemy.Table(
    'tbl_collection_overlaps',
    metadata,
    sqlalchemy.Column(key='collectionOverlapId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='otherRegistryAddress', name='other_registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='registryTokenCount', name='registry_token_count', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(key='otherRegistryTokenCount', name='other_registry_token_count', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
)


GalleryBadgeHoldersTable = sqlalchemy.Table(
    'tbl_gallery_badge_holders',
    metadata,
    sqlalchemy.Column(key='galleryBadgeHolderId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='badgeKey', name='badge_key', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='achievedDate', name='achieved_date', type_=sqlalchemy.DateTime, nullable=False),
)


GalleryBadgeAssignmentsTable = sqlalchemy.Table(
    'tbl_gallery_badge_assignments',
    metadata,
    sqlalchemy.Column(key='galleryBadgeAssignmentId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='badgeKey', name='badge_key', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='achievedDate', name='achieved_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='assignerAddress', name='assigner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='signatureMessage', name='signature_message', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='signature', name='signature', type_=sqlalchemy.Text, nullable=False),
)


GalleryBadgeHoldersView = sqlalchemy.Table(
    'vw_gallery_badge_holders',
    metadata,
    sqlalchemy.Column(key='galleryBadgeId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='badgeKey', name='badge_key', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='achievedDate', name='achieved_date', type_=sqlalchemy.DateTime, nullable=False),
)

TokenStakingsTable = sqlalchemy.Table(
    'tbl_token_stakings',
    metadata,
    sqlalchemy.Column(key='tokenStakingId', name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(key='createdDate', name='created_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='updatedDate', name='updated_date', type_=sqlalchemy.DateTime, nullable=False),
    sqlalchemy.Column(key='stakingAddress', name='staking_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='ownerAddress', name='owner_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='registryAddress', name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='tokenId', name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(key='stakingDate', name='staking_date', type_=sqlalchemy.DateTime, nullable=False),
)
