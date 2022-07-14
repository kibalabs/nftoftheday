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

class UpdateCollectionAttributesMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION_ATTRIBUTES'

class UpdateCollectionTokenAttributesMessageContent(MessageContent):
    _COMMAND = 'UPDATE_TOKEN_ATTRIBUTE'
    registryAddress: str
    tokenId: str
