from typing import List

from notd.core.model import MessageContent


class ProcessBlocksMessageContent(MessageContent):
    _COMMAND = 'PROCESS_BLOCKS'
    blockNumbers: List[int]

class ProcessBlockRangeMessageContent(MessageContent):
    _COMMAND = 'PROCESS_BLOCK_RANGE'
    startBlockNumber: int
    endBlockNumber: int

class ReceiveNewBlocksMessageContent(MessageContent):
    _COMMAND = 'RECEIVE_NEW_BLOCKS'
