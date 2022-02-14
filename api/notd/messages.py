from core.queues.model import MessageContent


class ProcessBlockMessageContent(MessageContent):
    _COMMAND = 'PROCESS_BLOCK'
    blockNumber: int


class CheckBadBlocksMessageContent(MessageContent):
    _COMMAND = 'CHECK_BAD_BLOCKS'
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
