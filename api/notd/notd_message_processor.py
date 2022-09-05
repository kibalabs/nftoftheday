from core import logging
from core.exceptions import KibaException
from core.queues.message_queue_processor import MessageProcessor
from core.queues.model import SqsMessage
from core.util import date_util

from notd.gallery_manager import GalleryManager
from notd.manager import NotdManager
from notd.messages import ProcessBlockMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import RefreshListingsForAllCollections
from notd.messages import RefreshListingsForCollection
from notd.messages import RefreshViewsMessageContent
from notd.messages import ReprocessBlocksMessageContent
from notd.messages import UpdateActivityForAllCollectionsMessageContent
from notd.messages import UpdateActivityForCollectionMessageContent
from notd.messages import UpdateAllTwitterUsersMessageContent
from notd.messages import UpdateCollectionMessageContent
from notd.messages import UpdateCollectionTokenAttributesMessageContent
from notd.messages import UpdateCollectionTokensMessageContent
from notd.messages import UpdateListingsForAllCollections
from notd.messages import UpdateListingsForCollection
from notd.messages import UpdateTokenAttributesForAllCollectionsMessageContent
from notd.messages import UpdateTokenMetadataMessageContent
from notd.messages import UpdateTokenOwnershipMessageContent


class NotdMessageProcessor(MessageProcessor):

    def __init__(self, notdManager: NotdManager):
        self.notdManager = notdManager

    async def process_message(self, message: SqsMessage) -> None:
        if message.command == ProcessBlockMessageContent.get_command():
            messageContent = ProcessBlockMessageContent.parse_obj(message.content)
            await self.notdManager.process_block(blockNumber=messageContent.blockNumber, shouldSkipProcessingTokens=messageContent.shouldSkipProcessingTokens)
            return
        if message.command == ReceiveNewBlocksMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            messageContent = ReceiveNewBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.receive_new_blocks()
            return
        if message.command == RefreshViewsMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            messageContent = RefreshViewsMessageContent.parse_obj(message.content)
            await self.notdManager.refresh_views()
            return
        if message.command == ReprocessBlocksMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            messageContent = ReprocessBlocksMessageContent.parse_obj(message.content)
            await self.notdManager.reprocess_old_blocks()
            return
        if message.command == UpdateTokenMetadataMessageContent.get_command():
            messageContent = UpdateTokenMetadataMessageContent.parse_obj(message.content)
            await self.notdManager.update_token_metadata(registryAddress=messageContent.registryAddress, tokenId=messageContent.tokenId, shouldForce=messageContent.shouldForce)
            return
        if message.command == UpdateTokenOwnershipMessageContent.get_command():
            messageContent = UpdateTokenOwnershipMessageContent.parse_obj(message.content)
            await self.notdManager.update_token_ownership(registryAddress=messageContent.registryAddress, tokenId=messageContent.tokenId)
            return
        if message.command == UpdateCollectionMessageContent.get_command():
            messageContent = UpdateCollectionMessageContent.parse_obj(message.content)
            await self.notdManager.update_collection(address=messageContent.address, shouldForce=messageContent.shouldForce)
            return
        if message.command == UpdateCollectionTokensMessageContent.get_command():
            messageContent = UpdateCollectionTokensMessageContent.parse_obj(message.content)
            await self.notdManager.update_collection_tokens(address=messageContent.address, shouldForce=messageContent.shouldForce)
            return
        if message.command == UpdateActivityForAllCollectionsMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 10)):
                logging.info(f'Skipping {message.command} from more than 10 minutes ago')
                return
            messageContent = UpdateActivityForAllCollectionsMessageContent.parse_obj(message.content)
            await self.notdManager.update_activity_for_all_collections()
            return
        if message.command == UpdateActivityForCollectionMessageContent.get_command():
            messageContent = UpdateActivityForCollectionMessageContent.parse_obj(message.content)
            await self.notdManager.update_activity_for_collection(address=messageContent.address, startDate=messageContent.startDate)
            return
        if message.command == UpdateTokenAttributesForAllCollectionsMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 60)):
                logging.info(f'Skipping {message.command} from more than 60 minutes ago')
                return
            messageContent = UpdateTokenAttributesForAllCollectionsMessageContent.parse_obj(message.content)
            await self.notdManager.update_token_attributes_for_all_collections()
            return
        if message.command == UpdateCollectionTokenAttributesMessageContent.get_command():
            messageContent = UpdateCollectionTokenAttributesMessageContent.parse_obj(message.content)
            await self.notdManager.update_collection_token_attributes(registryAddress=messageContent.registryAddress, tokenId=messageContent.tokenId)
            return
        if message.command == UpdateListingsForAllCollections.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            messageContent = UpdateListingsForAllCollections.parse_obj(message.content)
            await self.notdManager.update_latest_listings_for_all_collections()
            return
        if message.command == UpdateListingsForCollection.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            messageContent = UpdateListingsForCollection.parse_obj(message.content)
            await self.notdManager.update_latest_listings_for_collection(address=messageContent.address)
            return
        if message.command == RefreshListingsForAllCollections.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 60)):
                logging.info(f'Skipping {message.command} from more than 60 minutes ago')
                return
            messageContent = RefreshListingsForAllCollections.parse_obj(message.content)
            await self.notdManager.refresh_latest_listings_for_all_collections()
            return
        if message.command == RefreshListingsForCollection.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 60)):
                logging.info(f'Skipping {message.command} from more than 60 minutes ago')
                return
            messageContent = RefreshListingsForCollection.parse_obj(message.content)
            await self.notdManager.refresh_latest_listings_for_collection(address=messageContent.address)
            return
        if message.command == UpdateAllTwitterUsersMessageContent.get_command():
            messageContent = UpdateAllTwitterUsersMessageContent.parse_obj(message.content)
            await self.notdManager.update_all_twitter_users()
        raise KibaException(message='Message was unhandled')
