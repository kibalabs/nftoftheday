import logging

from core.exceptions import KibaException
from core.queues.message_queue_processor import MessageProcessor
from core.queues.model import SqsMessage
from core.util import date_util

from notd.manager import NotdManager
from notd.messages import CheckBadBlocksMessageContent
from notd.messages import ProcessBlockMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateTokenMetadataMessageContent


class NotdMessageProcessor(MessageProcessor):

    def __init__(self, notdManager: NotdManager):
        self.notdManager = notdManager

    async def process_message(self, message: SqsMessage) -> None:
        if message.command == ProcessBlockMessageContent.get_command():
            messageContent = ProcessBlockMessageContent.parse_obj(message.content)
            await self.notdManager.process_block(blockNumber=messageContent.blockNumber)
            return
        if message.command == ReceiveNewBlocksMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping received new blocks from more than 5 minutes ago')
                return
            messageContent = ReceiveNewBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.receive_new_blocks()
            return
        if message.command == CheckBadBlocksMessageContent.get_command():
            messageContent = CheckBadBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.check_bad_blocks(startBlockNumber=messageContent.startBlockNumber, endBlockNumber=messageContent.endBlockNumber)
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
