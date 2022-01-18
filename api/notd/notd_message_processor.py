import logging
from core.exceptions import KibaException
from core.queues.message_queue_processor import MessageProcessor
from core.queues.model import SqsMessage
from core.util import date_util

from notd.manager import NotdManager
from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ProcessBlocksMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateTokenMetadataMessageContent


class NotdMessageProcessor(MessageProcessor):

    def __init__(self, notdManager: NotdManager):
        self.notdManager = notdManager

    async def process_message(self, message: SqsMessage) -> None:
        if message.command == ProcessBlocksMessageContent.get_command():
            messageContent = ProcessBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.process_blocks(blockNumbers=messageContent.blockNumbers)
            return
        if message.command == ProcessBlockRangeMessageContent.get_command():
            messageContent = ProcessBlockRangeMessageContent.parse_obj(message.content)
            await self.notdManager.process_block_range(startBlockNumber=messageContent.startBlockNumber, endBlockNumber=messageContent.endBlockNumber)
            return
        if message.command == ReceiveNewBlocksMessageContent.get_command():
            if message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping received new blocks from more than 5 minutes ago')
                return
            messageContent = ReceiveNewBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.receive_new_blocks()
            return
        if message.command == UpdateTokenMetadataMessageContent.get_command():
            messageContent = UpdateTokenMetadataMessageContent.parse_obj(message.content)
            await self.notdManager.update_token_metadata(registryAddress=messageContent.registryAddress, tokenId=messageContent.tokenId)
            return
        if message.command == UpdateCollectionMessageContent.get_command():
            messageContent = UpdateCollectionMessageContent.parse_obj(message.content)
            await self.notdManager.update_collection(address=messageContent.address)
            return

        raise KibaException(message='Message was unhandled')
