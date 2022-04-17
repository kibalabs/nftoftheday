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

class SaveCollectionStatisticsMessageContent(MessageContent):
    _COMMAND = 'SAVE_COLLECTION_STATISTICS'
    address: str
    date: datetime.datetime
    shouldForce: Optional[bool]
