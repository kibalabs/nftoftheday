from core import logging
from core.exceptions import KibaException
from core.queues.message_queue_processor import MessageProcessor
from core.queues.model import Message
from core.util import date_util

from notd.manager import NotdManager
from notd.messages import ProcessBlockMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.messages import RefreshAllCollectionOverlapsMessageContent
from notd.messages import RefreshCollectionOverlapMessageContent
from notd.messages import RefreshGalleryBadgeHoldersForAllCollectionsMessageContent
from notd.messages import RefreshGalleryBadgeHoldersForCollectionMessageContent
from notd.messages import RefreshListingsForAllCollections
from notd.messages import RefreshListingsForCollection
from notd.messages import RefreshStakingsForCollectionMessageContent
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
from notd.messages import UpdateTotalActivityForAllCollectionsMessageContent
from notd.messages import UpdateTotalActivityForCollectionMessageContent


class NotdMessageProcessor(MessageProcessor):

    def __init__(self, notdManager: NotdManager):
        self.notdManager = notdManager

    async def process_message(self, message: Message) -> None:
        if message.command == ProcessBlockMessageContent.get_command():
            processBlockMessageContent = ProcessBlockMessageContent.parse_obj(message.content)
            await self.notdManager.process_block(blockNumber=processBlockMessageContent.blockNumber, shouldSkipProcessingTokens=processBlockMessageContent.shouldSkipProcessingTokens)
            return
        if message.command == ReceiveNewBlocksMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            receiveNewBlocksMessageContent = ReceiveNewBlocksMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.receive_new_blocks()
            return
        if message.command == RefreshViewsMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            refreshViewsMessageContent = RefreshViewsMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.refresh_views()
            return
        if message.command == ReprocessBlocksMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            reprocessBlocksMessageContent = ReprocessBlocksMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.reprocess_old_blocks()
            return
        if message.command == UpdateTokenMetadataMessageContent.get_command():
            updateTokenMetadataMessageContent = UpdateTokenMetadataMessageContent.parse_obj(message.content)
            await self.notdManager.update_token_metadata(registryAddress=updateTokenMetadataMessageContent.registryAddress, tokenId=updateTokenMetadataMessageContent.tokenId, shouldForce=updateTokenMetadataMessageContent.shouldForce)
            return
        if message.command == UpdateTokenOwnershipMessageContent.get_command():
            updateTokenOwnershipMessageContent = UpdateTokenOwnershipMessageContent.parse_obj(message.content)
            await self.notdManager.update_token_ownership(registryAddress=updateTokenOwnershipMessageContent.registryAddress, tokenId=updateTokenOwnershipMessageContent.tokenId)
            return
        if message.command == UpdateCollectionMessageContent.get_command():
            updateCollectionMessageContent = UpdateCollectionMessageContent.parse_obj(message.content)
            await self.notdManager.update_collection(address=updateCollectionMessageContent.address, shouldForce=updateCollectionMessageContent.shouldForce)
            return
        if message.command == UpdateCollectionTokensMessageContent.get_command():
            updateCollectionTokensMessageContent = UpdateCollectionTokensMessageContent.parse_obj(message.content)
            await self.notdManager.update_collection_tokens(address=updateCollectionTokensMessageContent.address, shouldForce=updateCollectionTokensMessageContent.shouldForce)
            return
        if message.command == UpdateActivityForAllCollectionsMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 10)):
                logging.info(f'Skipping {message.command} from more than 10 minutes ago')
                return
            updateActivityForAllCollectionsMessageContent = UpdateActivityForAllCollectionsMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.update_activity_for_all_collections()
            return
        if message.command == UpdateActivityForCollectionMessageContent.get_command():
            updateActivityForCollectionMessageContent = UpdateActivityForCollectionMessageContent.parse_obj(message.content)
            await self.notdManager.update_activity_for_collection(address=updateActivityForCollectionMessageContent.address, startDate=updateActivityForCollectionMessageContent.startDate)
            return
        if message.command == UpdateTotalActivityForAllCollectionsMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 10)):
                logging.info(f'Skipping {message.command} from more than 10 minutes ago')
                return
            updateTotalActivityForAllCollectionsMessageContent = UpdateTotalActivityForAllCollectionsMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.update_total_activity_for_all_collections()
            return
        if message.command == UpdateTotalActivityForCollectionMessageContent.get_command():
            updateTotalActivityForCollectionMessageContent = UpdateTotalActivityForCollectionMessageContent.parse_obj(message.content)
            await self.notdManager.update_total_activity_for_collection(address=updateTotalActivityForCollectionMessageContent.address)
            return
        if message.command == UpdateTokenAttributesForAllCollectionsMessageContent.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 60)):
                logging.info(f'Skipping {message.command} from more than 60 minutes ago')
                return
            updateTokenAttributesForAllCollectionsMessageContent = UpdateTokenAttributesForAllCollectionsMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable, invalid-name
            await self.notdManager.update_token_attributes_for_all_collections()
            return
        if message.command == UpdateCollectionTokenAttributesMessageContent.get_command():
            updateCollectionTokenAttributesMessageContent = UpdateCollectionTokenAttributesMessageContent.parse_obj(message.content)
            await self.notdManager.update_collection_token_attributes(registryAddress=updateCollectionTokenAttributesMessageContent.registryAddress, tokenId=updateCollectionTokenAttributesMessageContent.tokenId)
            return
        if message.command == UpdateListingsForAllCollections.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            updateListingsForAllCollections = UpdateListingsForAllCollections.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.update_latest_listings_for_all_collections()
            return
        if message.command == UpdateListingsForCollection.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 5)):
                logging.info(f'Skipping {message.command} from more than 5 minutes ago')
                return
            updateListingsForCollection = UpdateListingsForCollection.parse_obj(message.content)
            await self.notdManager.update_latest_listings_for_collection(address=updateListingsForCollection.address)
            return
        if message.command == RefreshListingsForAllCollections.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 60)):
                logging.info(f'Skipping {message.command} from more than 60 minutes ago')
                return
            refreshListingsForAllCollections = RefreshListingsForAllCollections.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.refresh_latest_listings_for_all_collections()
            return
        if message.command == RefreshListingsForCollection.get_command():
            if message.postDate is None or message.postDate < date_util.datetime_from_now(seconds=-(60 * 60)):
                logging.info(f'Skipping {message.command} from more than 60 minutes ago')
                return
            refreshListingsForCollection = RefreshListingsForCollection.parse_obj(message.content)
            await self.notdManager.refresh_latest_listings_for_collection(address=refreshListingsForCollection.address)
            return
        if message.command == UpdateAllTwitterUsersMessageContent.get_command():
            updateAllTwitterUsersMessageContent = UpdateAllTwitterUsersMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.update_all_twitter_users()
            return
        if message.command == RefreshAllCollectionOverlapsMessageContent.get_command():
            refreshAllCollectionOverlapsMessageContent = RefreshAllCollectionOverlapsMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable
            await self.notdManager.refresh_overlaps_for_all_collections()
            return
        if message.command == RefreshCollectionOverlapMessageContent.get_command():
            refreshCollectionOverlapMessageContent = RefreshCollectionOverlapMessageContent.parse_obj(message.content)
            await self.notdManager.refresh_overlap_for_collection(registryAddress=refreshCollectionOverlapMessageContent.registryAddress)
            return
        if message.command == RefreshGalleryBadgeHoldersForAllCollectionsMessageContent.get_command():
            refreshGalleryBadgeHoldersForAllCollectionsMessageContent = RefreshGalleryBadgeHoldersForAllCollectionsMessageContent.parse_obj(message.content)  # pylint: disable=unused-variable, invalid-name
            await self.notdManager.refresh_gallery_badge_holders_for_all_collections()
            return
        if message.command == RefreshGalleryBadgeHoldersForCollectionMessageContent.get_command():
            refreshGalleryBadgeHoldersForCollectionMessageContent = RefreshGalleryBadgeHoldersForCollectionMessageContent.parse_obj(message.content)  # pylint: disable=invalid-name
            await self.notdManager.refresh_gallery_badge_holders_for_collection(registryAddress=refreshGalleryBadgeHoldersForCollectionMessageContent.registryAddress)
            return
        if message.command == RefreshStakingsForCollectionMessageContent.get_command():
            refreshStakingsForCollectionMessageContent = RefreshStakingsForCollectionMessageContent.parse_obj(message.content)  # pylint: disable=invalid-name
            await self.notdManager.refresh_collection_stakings(registryAddress=refreshStakingsForCollectionMessageContent.address)
            return
        raise KibaException(message='Message was unhandled')
