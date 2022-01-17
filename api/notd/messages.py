from typing import List

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

class UpdateTokenMetadataMessageContent(MessageContent):
    _COMMAND = 'UPDATE_TOKEN_METADATA'
    registryAddress: str
    tokenId: str

class UpdateCollectionMessageContent(MessageContent):
    _COMMAND = 'UPDATE_COLLECTION'
    address: str
