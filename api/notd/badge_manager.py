import datetime
import json
import logging

from core.exceptions import BadRequestException
from core.queues.message_queue import MessageQueue
from core.queues.model import Message
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from core.util import list_util
from eth_account.messages import defunct_hash_message
from web3.auto import w3

from notd.badge_processor import BadgeProcessor
from notd.messages import RefreshGalleryBadgeHoldersForAllCollectionsMessageContent
from notd.messages import RefreshGalleryBadgeHoldersForCollectionMessageContent
from notd.model import GALLERY_COLLECTION_ADMINS
from notd.model import GALLERY_COLLECTIONS
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import GalleryBadgeAssignmentsTable
from notd.store.schema import GalleryBadgeHoldersTable


class BadgeManager:

    def __init__(self, retriever: Retriever, saver: Saver, workQueue: MessageQueue[Message], badgeProcessor: BadgeProcessor) -> None:
        self.retriever = retriever
        self.saver = saver
        self.workQueue = workQueue
        self.badgeProcessor = badgeProcessor

    async def refresh_gallery_badge_holders_for_all_collections_deferred(self) -> None:
        await self.workQueue.send_message(message=RefreshGalleryBadgeHoldersForAllCollectionsMessageContent().to_message())

    async def refresh_gallery_badge_holders_for_all_collections(self) -> None:
        for registryAddress in GALLERY_COLLECTIONS:
            await self.refresh_gallery_badge_holders_for_collection_deferred(registryAddress=registryAddress)

    async def refresh_gallery_badge_holders_for_collection_deferred(self, registryAddress: str) -> None:
        await self.workQueue.send_message(message=RefreshGalleryBadgeHoldersForCollectionMessageContent(registryAddress=registryAddress).to_message())

    async def refresh_gallery_badge_holders_for_collection(self, registryAddress: str) -> None:
        registryAddress = chain_util.normalize_address(registryAddress)
        retrievedGalleryBadgeHolders = await self.badgeProcessor.calculate_all_gallery_badge_holders(registryAddress=registryAddress)
        async with self.saver.create_transaction() as connection:
            currentGalleryBadgeHolders = await self.retriever.list_gallery_badge_holders(fieldFilters=[
                StringFieldFilter(fieldName=GalleryBadgeHoldersTable.c.registryAddress.key, eq=registryAddress),
            ], connection=connection)
            galleryBadgeHoldersToDelete = {galleryBadgeHolders.galleryBadgeHolderId for galleryBadgeHolders in currentGalleryBadgeHolders}
            logging.info(f'Deleting {len(galleryBadgeHoldersToDelete)} existing gallery badges')
            for chunkedIds in list_util.generate_chunks(lst=list(galleryBadgeHoldersToDelete), chunkSize=100):
                await self.saver.delete_gallery_badge_holders(galleryBadgeHolderIds=chunkedIds, connection=connection)
            logging.info(f'Saving {len(retrievedGalleryBadgeHolders)} gallery badges')
            await self.saver.create_gallery_badge_holders(retrievedGalleryBadgeHolders=retrievedGalleryBadgeHolders, connection=connection)

    async def assign_badge(self, registryAddress: str, ownerAddress: str, badgeKey: str, assignerAddress: str, achievedDate: datetime.datetime, signature: str) -> None:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        assignerAddress = chain_util.normalize_address(value=assignerAddress)
        if registryAddress not in GALLERY_COLLECTION_ADMINS:
            raise BadRequestException('Registry has no admins')
        if assignerAddress not in set(GALLERY_COLLECTION_ADMINS[registryAddress]):
            raise BadRequestException('Signer is not an admin')
        command = 'ASSIGN_BADGE'
        message = {
            'registryAddress': registryAddress,
            'ownerAddress': ownerAddress,
            'badgeKey': badgeKey,
            'assignerAddress': assignerAddress,
            'achievedDate': date_util.datetime_to_string(achievedDate),
        }
        signatureMessage = json.dumps({ 'command': command, 'message': message }, indent=2, ensure_ascii=False)
        messageHash = defunct_hash_message(text=signatureMessage)
        signer = w3.eth.account.recoverHash(message_hash=messageHash, signature=signature)
        if signer != assignerAddress:
            raise BadRequestException('Invalid signature')
        async with self.saver.create_transaction() as connection:
            retrieveAssignedGalleryBadgeHolders = await self.retriever.list_gallery_badge_assignments(fieldFilters=[
                StringFieldFilter(fieldName=GalleryBadgeAssignmentsTable.c.registryAddress.key, eq=registryAddress),
                StringFieldFilter(fieldName=GalleryBadgeAssignmentsTable.c.ownerAddress.key, eq=ownerAddress),
                StringFieldFilter(fieldName=GalleryBadgeAssignmentsTable.c.badgeKey.key, eq=badgeKey),
            ], connection=connection)
            if len(retrieveAssignedGalleryBadgeHolders) > 1:
                raise BadRequestException('Badge already assigned')
            await self.saver.create_gallery_badge_assignment(registryAddress=registryAddress, ownerAddress=ownerAddress, assignerAddress=assignerAddress, badgeKey=badgeKey, achievedDate=achievedDate, signatureMessage=signatureMessage, signature=signature, connection=connection)
