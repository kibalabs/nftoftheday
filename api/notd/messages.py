import datetime
from typing import Optional

from core.queues.model import MessageContent


class ProcessBlockMessageContent(MessageContent):
    _COMMAND = 'PROCESS_BLOCK'
    blockNumber: int
    shouldSkipProcessingTokens: Optional[bool]


class ReprocessBlocksMessageContent(MessageContent):
    _COMMAND = 'REPROCESS_OLD_BLOCKS'


class ReceiveNewBlocksMessageContent(MessageContent):
    _COMMAND = 'RECEIVE_NEW_BLOCKS'


class RefreshViewsMessageContent(MessageContent):
    _COMMAND = 'REFRESH_VIEWS'


class UpdateTokenMetadataMessageContent(MessageContent):
    _COMMAND = 'UPDATE_TOKEN_METADATA'
    registryAddress: str
    tokenId: str
    shouldForce: Optional[bool]


class UpdateTokenOwnershipMessageContent(MessageContent):
    _COMMAND = 'UPDATE_TOKEN_OWNERSHIP'
    registryAddress: str
    tokenId: str


class UpdateCollectionMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION'
    address: str
    shouldForce: Optional[bool]


class UpdateCollectionTokensMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION_TOKENS'
    address: str
    shouldForce: Optional[bool]


class UpdateActivityForAllCollectionsMessageContent(MessageContent):
    _COMMAND = 'UPDATE_ACTIVITY_FOR_ALL_COLLECTIONS'


class UpdateActivityForCollectionMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION_ACTIVITY'
    address: str
    startDate: datetime.datetime


class UpdateTotalActivityForAllCollectionsMessageContent(MessageContent):
    _COMMAND = 'UPDATE_TOTAL_ACTIVITY_FOR_ALL_COLLECTIONS'


class UpdateTotalActivityForCollectionMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION_TOTAL_ACTIVITY'
    address: str


class UpdateTokenAttributesForAllCollectionsMessageContent(MessageContent):
    _COMMAND = 'UPDATE_TOKEN_ATTRIBUTES_FOR_ALL_COLLECTIONS'


class UpdateCollectionTokenAttributesMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION_TOKEN_ATTRIBUTES'
    registryAddress: str
    tokenId: str


class UpdateListingsForAllCollections(MessageContent):
    _COMMAND = 'UPDATE_LISTINGS_FOR_ALL_COLLECTIONS'


class UpdateListingsForCollection(MessageContent):
    _COMMAND = 'UPDATE_LISTINGS_FOR_COLLECTION'
    address: str


class UpdateAllTwitterUsersMessageContent(MessageContent):
    _COMMAND = 'UPDATE_ALL_TWITTER_USERS'


class RefreshListingsForAllCollections(MessageContent):
    _COMMAND = 'REFRESH_LISTINGS_FOR_ALL_COLLECTIONS'


class RefreshListingsForCollection(MessageContent):
    _COMMAND = 'REFRESH_LISTINGS_FOR_COLLECTION'
    address: str


class RefreshCollectionOverlapMessageContent(MessageContent):
    _COMMAND = 'REFRESH_COLLECTION_OVERLAP'
    registryAddress: str


class RefreshAllCollectionOverlapsMessageContent(MessageContent):
    _COMMAND = 'REFRESH_ALL_COLLECTION_OVERLAPS'


class RefreshUserBadgesForCollectionMessageContent(MessageContent):
    _COMMAND = 'REFRESH_USER_BADGES_FOR_COLLECTION'
    registryAddress: str


class RefreshUserBadgesForAllCollectionsMessageContent(MessageContent):
    _COMMAND = 'REFRESH_USER_BADGES_FOR_ALL_COLLECTIONS'
