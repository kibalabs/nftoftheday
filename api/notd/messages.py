from core.queues.model import MessageContent


class ProcessBlockMessageContent(MessageContent):
    _COMMAND = 'PROCESS_BLOCK'
    blockNumber: int


# TODO(krishan711): remove this once everything uses ProcessBlockMessageContent
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
