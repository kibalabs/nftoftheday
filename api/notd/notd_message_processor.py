from core.message_queue_processor import MessageProcessor
from core.model import SqsMessage
from core.exceptions import KibaException
from notd.messages import ProcessBlocksMessageContent
from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.manager import NotdManager

class NotdMessageProcessor(MessageProcessor):

    def __init__(self, notdManager: NotdManager):
        self.notdManager = notdManager

    async def process_message(self, message: SqsMessage) -> None:
        if message.command == ProcessBlocksMessageContent._COMMAND:
            messageContent = ProcessBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.process_blocks(blockNumbers=messageContent.blockNumbers)
            return
        if message.command == ProcessBlockRangeMessageContent._COMMAND:
            messageContent = ProcessBlockRangeMessageContent.parse_obj(message.content)
            await self.notdManager.process_block_range(startBlockNumber=messageContent.startBlockNumber, endBlockNumber=messageContent.endBlockNumber)
            return
        if message.command == ReceiveNewBlocksMessageContent._COMMAND:
            messageContent = ReceiveNewBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.receive_new_blocks()
            return
        raise KibaException(message='Message was unhandled')
