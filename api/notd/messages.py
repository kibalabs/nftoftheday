import datetime
from typing import List, Optional

from core.queues.model import MessageContent


class ProcessBlocksMessageContent(MessageContent):
    _COMMAND = 'PROCESS_BLOCKS'
    blockNumbers: List[int]

class ProcessBlockRangeMessageContent(MessageContent):
    _COMMAND = 'PROCESS_BLOCK_RANGE'
    startBlockNumber: int
    endBlockNumber: int

class ReceiveNewBlocksMessageContent(MessageContent):
    _COMMAND = 'RECEIVE_NEW_BLOCKS'
    _postDate = Optional[datetime.datetime]

class UpdateTokenMetadataMessageContent(MessageContent):
    _COMMAND = 'UPDATE_TOKEN_METADATA'
    registryAddress: str
    tokenId: str

class UpdateCollectionMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION'
    address: str
