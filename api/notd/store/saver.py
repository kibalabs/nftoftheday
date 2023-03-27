# pylint: disable=too-many-lines
import datetime
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from core.store.database import DatabaseConnection
from core.store.saver import Saver as CoreSaver
from core.util import date_util
from core.util import list_util
from core.util.typing_util import JSON

from notd.model import AccountCollectionGm
from notd.model import AccountGm
from notd.model import Block
from notd.model import Collection
from notd.model import CollectionHourlyActivity
from notd.model import CollectionTotalActivity
from notd.model import GalleryBadgeAssignment
from notd.model import LatestUpdate
from notd.model import Lock
from notd.model import RetrievedCollectionOverlap
from notd.model import RetrievedGalleryBadgeHolder
from notd.model import RetrievedTokenAttribute
from notd.model import RetrievedTokenListing
from notd.model import RetrievedTokenMultiOwnership
from notd.model import RetrievedTokenStaking
from notd.model import RetrievedTokenTransfer
from notd.model import Signature
from notd.model import TokenCustomization
from notd.model import TokenMetadata
from notd.model import TokenOwnership
from notd.model import TwitterCredential
from notd.model import TwitterProfile
from notd.model import UserInteraction
from notd.model import UserProfile
from notd.store.schema import AccountCollectionGmsTable
from notd.store.schema import AccountGmsTable
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivitiesTable
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import GalleryBadgeAssignmentsTable
from notd.store.schema import GalleryBadgeHoldersTable
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import LatestUpdatesTable
from notd.store.schema import LocksTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionOverlapsTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenCustomizationsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenStakingsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import TwitterCredentialsTable
from notd.store.schema import TwitterProfilesTable
from notd.store.schema import UserInteractionsTable
from notd.store.schema import UserProfilesTable

if TYPE_CHECKING:
    from sqlalchemy.sql._typing import _DMLColumnArgument
else:
    _DMLColumnArgument = Any

_EMPTY_STRING = '_EMPTY_STRING'
_EMPTY_OBJECT = '_EMPTY_OBJECT'

CreateRecordDict = Dict[_DMLColumnArgument, Any]  # type: ignore[misc]
UpdateRecordDict = Dict[_DMLColumnArgument, Any]  # type: ignore[misc]

class Saver(CoreSaver):

    @staticmethod
    def _get_create_token_transfer_values(retrievedTokenTransfer: RetrievedTokenTransfer) -> CreateRecordDict:  # type: ignore[misc]
        return {
            TokenTransfersTable.c.transactionHash.key: retrievedTokenTransfer.transactionHash,
            TokenTransfersTable.c.registryAddress.key: retrievedTokenTransfer.registryAddress,
            TokenTransfersTable.c.fromAddress.key: retrievedTokenTransfer.fromAddress,
            TokenTransfersTable.c.toAddress.key: retrievedTokenTransfer.toAddress,
            TokenTransfersTable.c.operatorAddress.key: retrievedTokenTransfer.operatorAddress,
            TokenTransfersTable.c.contractAddress.key: retrievedTokenTransfer.contractAddress,
            TokenTransfersTable.c.tokenId.key: retrievedTokenTransfer.tokenId,
            TokenTransfersTable.c.value.key: retrievedTokenTransfer.value,
            TokenTransfersTable.c.amount.key: retrievedTokenTransfer.amount,
            TokenTransfersTable.c.gasLimit.key: retrievedTokenTransfer.gasLimit,
            TokenTransfersTable.c.gasPrice.key: retrievedTokenTransfer.gasPrice,
            TokenTransfersTable.c.blockNumber.key: retrievedTokenTransfer.blockNumber,
            TokenTransfersTable.c.tokenType.key: retrievedTokenTransfer.tokenType,
            TokenTransfersTable.c.isMultiAddress.key: retrievedTokenTransfer.isMultiAddress,
            TokenTransfersTable.c.isInterstitial.key: retrievedTokenTransfer.isInterstitial,
            TokenTransfersTable.c.isSwap.key: retrievedTokenTransfer.isSwap,
            TokenTransfersTable.c.isBatch.key: retrievedTokenTransfer.isBatch,
            TokenTransfersTable.c.isOutbound.key: retrievedTokenTransfer.isOutbound,
        }

    async def create_token_transfer(self, retrievedTokenTransfer: RetrievedTokenTransfer, connection: Optional[DatabaseConnection] = None) -> int:
        values = self._get_create_token_transfer_values(retrievedTokenTransfer=retrievedTokenTransfer)
        query = TokenTransfersTable.insert().values(values).returning(TokenTransfersTable.c.tokenTransferId)
        result = await self._execute(query=query, connection=connection)
        tokenTransferId = int(result.scalar_one())
        return tokenTransferId

    async def create_token_transfers(self, retrievedTokenTransfers: Sequence[RetrievedTokenTransfer], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedTokenTransfers) == 0:
            return []
        tokenTransferIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenTransfers, chunkSize=100):
            values = [self._get_create_token_transfer_values(retrievedTokenTransfer=retrievedTokenTransfer) for retrievedTokenTransfer in chunk]
            query = TokenTransfersTable.insert().values(values).returning(TokenTransfersTable.c.tokenTransferId)
            rows = await self._execute(query=query, connection=connection)
            tokenTransferIds += [row[0] for row in rows]
        return tokenTransferIds

    async def delete_token_transfer(self, tokenTransferId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = TokenTransfersTable.delete().where(TokenTransfersTable.c.tokenTransferId == tokenTransferId).returning(TokenTransfersTable.c.tokenTransferId)
        await self._execute(query=query, connection=connection)

    async def delete_token_transfers(self, tokenTransferIds: Sequence[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(tokenTransferIds) == 0:
            return
        query = TokenTransfersTable.delete().where(TokenTransfersTable.c.tokenTransferId.in_(tokenTransferIds)).returning(TokenTransfersTable.c.tokenTransferId)
        await self._execute(query=query, connection=connection)

    async def create_block(self, blockNumber: int, blockHash: str, blockDate: datetime.datetime, connection: Optional[DatabaseConnection] = None) -> Block:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            BlocksTable.c.createdDate.key: createdDate,
            BlocksTable.c.updatedDate.key: updatedDate,
            BlocksTable.c.blockNumber.key: blockNumber,
            BlocksTable.c.blockHash.key: blockHash,
            BlocksTable.c.blockDate.key: blockDate,
        }
        query = BlocksTable.insert().values(values).returning(BlocksTable.c.blockId)
        result = await self._execute(query=query, connection=connection)
        blockId = int(result.scalar_one())
        return Block(
            blockId=blockId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            blockNumber=blockNumber,
            blockHash=blockHash,
            blockDate=blockDate,
        )

    async def update_block(self, blockId: int, blockHash: Optional[str] = None, blockDate: Optional[datetime.datetime] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if blockHash is not None:
            values[BlocksTable.c.blockHash.key] = blockHash
        if blockDate is not None:
            values[BlocksTable.c.blockDate.key] = blockDate
        if len(values) > 0:
            values[BlocksTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = BlocksTable.update().where(BlocksTable.c.blockId == blockId).values(values).returning(BlocksTable.c.blockId)
        await self._execute(query=query, connection=connection)

    async def create_token_metadata(self, tokenId: str, registryAddress: str, metadataUrl: Optional[str], name: Optional[str], description: Optional[str], imageUrl: Optional[str], resizableImageUrl: Optional[str], animationUrl: Optional[str], youtubeUrl: Optional[str], backgroundColor: Optional[str], frameImageUrl: Optional[str], attributes: Optional[JSON], connection: Optional[DatabaseConnection] = None) -> TokenMetadata:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            TokenMetadatasTable.c.createdDate.key: createdDate,
            TokenMetadatasTable.c.updatedDate.key: updatedDate,
            TokenMetadatasTable.c.registryAddress.key: registryAddress,
            TokenMetadatasTable.c.tokenId.key: tokenId,
            TokenMetadatasTable.c.metadataUrl.key: metadataUrl,
            TokenMetadatasTable.c.name.key: name,
            TokenMetadatasTable.c.description.key: description,
            TokenMetadatasTable.c.imageUrl.key: imageUrl,
            TokenMetadatasTable.c.resizableImageUrl.key: resizableImageUrl,
            TokenMetadatasTable.c.animationUrl.key: animationUrl,
            TokenMetadatasTable.c.youtubeUrl.key: youtubeUrl,
            TokenMetadatasTable.c.backgroundColor.key: backgroundColor,
            TokenMetadatasTable.c.frameImageUrl.key: frameImageUrl,
            TokenMetadatasTable.c.attributes.key: attributes,
        }
        query = TokenMetadatasTable.insert().values(values).returning(TokenMetadatasTable.c.tokenMetadataId)
        result = await self._execute(query=query, connection=connection)
        tokenMetadataId = int(result.scalar_one())
        return TokenMetadata(
            tokenMetadataId=tokenMetadataId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            name=name,
            description=description,
            imageUrl=imageUrl,
            resizableImageUrl=resizableImageUrl,
            animationUrl=animationUrl,
            youtubeUrl=youtubeUrl,
            backgroundColor=backgroundColor,
            frameImageUrl=frameImageUrl,
            attributes=attributes,
        )

    async def update_token_metadata(self, tokenMetadataId: int, metadataUrl: Optional[str] = None, name: Optional[str] = _EMPTY_STRING, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, resizableImageUrl: Optional[str] = _EMPTY_STRING, animationUrl: Optional[str] = _EMPTY_STRING, youtubeUrl: Optional[str] = _EMPTY_STRING, backgroundColor: Optional[str] = _EMPTY_STRING, frameImageUrl: Optional[str] = _EMPTY_STRING, attributes: Optional[JSON] = _EMPTY_OBJECT, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if metadataUrl is not None:
            values[TokenMetadatasTable.c.metadataUrl.key] = metadataUrl
        if name != _EMPTY_STRING:
            values[TokenMetadatasTable.c.name.key] = name
        if description != _EMPTY_STRING:
            values[TokenMetadatasTable.c.description.key] = description
        if imageUrl != _EMPTY_STRING:
            values[TokenMetadatasTable.c.imageUrl.key] = imageUrl
        if resizableImageUrl != _EMPTY_STRING:
            values[TokenMetadatasTable.c.resizableImageUrl.key] = resizableImageUrl
        if animationUrl != _EMPTY_STRING:
            values[TokenMetadatasTable.c.animationUrl.key] = animationUrl
        if youtubeUrl != _EMPTY_STRING:
            values[TokenMetadatasTable.c.youtubeUrl.key] = youtubeUrl
        if backgroundColor != _EMPTY_STRING:
            values[TokenMetadatasTable.c.backgroundColor.key] = backgroundColor
        if frameImageUrl != _EMPTY_STRING:
            values[TokenMetadatasTable.c.frameImageUrl.key] = frameImageUrl
        if attributes != _EMPTY_OBJECT:
            values[TokenMetadatasTable.c.attributes.key] = attributes
        if len(values) > 0:
            values[TokenMetadatasTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TokenMetadatasTable.update().where(TokenMetadatasTable.c.tokenMetadataId == tokenMetadataId).values(values).returning(TokenMetadatasTable.c.tokenMetadataId)
        await self._execute(query=query, connection=connection)

    async def create_collection(self, address: str, name: Optional[str], symbol: Optional[str], description: Optional[str], imageUrl: Optional[str] , twitterUsername: Optional[str], instagramUsername: Optional[str], wikiUrl: Optional[str], openseaSlug: Optional[str], url: Optional[str], discordUrl: Optional[str], bannerImageUrl: Optional[str], doesSupportErc721: bool, doesSupportErc1155: bool, connection: Optional[DatabaseConnection] = None) -> Collection:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            TokenCollectionsTable.c.createdDate.key: createdDate,
            TokenCollectionsTable.c.updatedDate.key: updatedDate,
            TokenCollectionsTable.c.address.key: address,
            TokenCollectionsTable.c.name.key: name,
            TokenCollectionsTable.c.symbol.key: symbol,
            TokenCollectionsTable.c.description.key: description,
            TokenCollectionsTable.c.imageUrl.key: imageUrl,
            TokenCollectionsTable.c.twitterUsername.key: twitterUsername,
            TokenCollectionsTable.c.instagramUsername.key: instagramUsername,
            TokenCollectionsTable.c.wikiUrl.key: wikiUrl,
            TokenCollectionsTable.c.openseaSlug.key: openseaSlug,
            TokenCollectionsTable.c.url.key: url,
            TokenCollectionsTable.c.discordUrl.key: discordUrl,
            TokenCollectionsTable.c.bannerImageUrl.key: bannerImageUrl,
            TokenCollectionsTable.c.doesSupportErc721.key: doesSupportErc721,
            TokenCollectionsTable.c.doesSupportErc1155.key: doesSupportErc1155,
        }
        query = TokenCollectionsTable.insert().values(values).returning(TokenCollectionsTable.c.collectionId)
        result = await self._execute(query=query, connection=connection)
        collectionId = int(result.scalar_one())
        return Collection(
            collectionId=collectionId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            address=address,
            name=name,
            symbol=symbol,
            description=description,
            imageUrl=imageUrl,
            twitterUsername=twitterUsername,
            instagramUsername=instagramUsername,
            wikiUrl=wikiUrl,
            openseaSlug=openseaSlug,
            url=url,
            discordUrl=discordUrl,
            bannerImageUrl=bannerImageUrl,
            doesSupportErc721=doesSupportErc721,
            doesSupportErc1155=doesSupportErc1155,
        )

    async def update_collection(self, collectionId: int, name: Optional[str] = _EMPTY_STRING, symbol: Optional[str] = _EMPTY_STRING, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, twitterUsername: Optional[str] = _EMPTY_STRING, instagramUsername: Optional[str] = _EMPTY_STRING, wikiUrl: Optional[str] = _EMPTY_STRING, openseaSlug: Optional[str] = _EMPTY_STRING, url: Optional[str] = _EMPTY_STRING, discordUrl: Optional[str] = _EMPTY_STRING, bannerImageUrl: Optional[str] = _EMPTY_STRING, doesSupportErc721: Optional[bool] = None, doesSupportErc1155: Optional[bool] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if name != _EMPTY_STRING:
            values[TokenCollectionsTable.c.name.key] = name
        if symbol != _EMPTY_STRING:
            values[TokenCollectionsTable.c.symbol.key] = symbol
        if description != _EMPTY_STRING:
            values[TokenCollectionsTable.c.description.key] = description
        if imageUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.imageUrl.key] = imageUrl
        if twitterUsername != _EMPTY_STRING:
            values[TokenCollectionsTable.c.twitterUsername.key] = twitterUsername
        if instagramUsername != _EMPTY_STRING:
            values[TokenCollectionsTable.c.instagramUsername.key] = instagramUsername
        if wikiUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.wikiUrl.key] = wikiUrl
        if openseaSlug != _EMPTY_STRING:
            values[TokenCollectionsTable.c.openseaSlug.key] = openseaSlug
        if url != _EMPTY_STRING:
            values[TokenCollectionsTable.c.url.key] = url
        if discordUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.discordUrl.key] = discordUrl
        if bannerImageUrl != _EMPTY_STRING:
            values[TokenCollectionsTable.c.bannerImageUrl.key] = bannerImageUrl
        if doesSupportErc721 is not None:
            values[TokenCollectionsTable.c.doesSupportErc721.key] = doesSupportErc721
        if doesSupportErc1155 is not None:
            values[TokenCollectionsTable.c.doesSupportErc1155.key] = doesSupportErc1155
        if len(values) > 0:
            values[TokenCollectionsTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TokenCollectionsTable.update().where(TokenCollectionsTable.c.collectionId == collectionId).values(values).returning(TokenCollectionsTable.c.collectionId)
        await self._execute(query=query, connection=connection)

    async def create_token_ownership(self, registryAddress: str, tokenId: str, ownerAddress: str, transferValue: int, transferDate: datetime.datetime, transferTransactionHash: str, connection: Optional[DatabaseConnection] = None) -> TokenOwnership:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            TokenOwnershipsTable.c.createdDate.key: createdDate,
            TokenOwnershipsTable.c.updatedDate.key: updatedDate,
            TokenOwnershipsTable.c.registryAddress.key: registryAddress,
            TokenOwnershipsTable.c.tokenId.key: tokenId,
            TokenOwnershipsTable.c.ownerAddress.key: ownerAddress,
            TokenOwnershipsTable.c.transferValue.key: transferValue,
            TokenOwnershipsTable.c.transferDate.key: transferDate,
            TokenOwnershipsTable.c.transferTransactionHash.key: transferTransactionHash,
        }
        query = TokenOwnershipsTable.insert().values(values).returning(TokenOwnershipsTable.c.tokenOwnershipId)
        result = await self._execute(query=query, connection=connection)
        tokenOwnershipId = int(result.scalar_one())
        return TokenOwnership(
            tokenOwnershipId=tokenOwnershipId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            tokenId=tokenId,
            ownerAddress=ownerAddress,
            transferValue=transferValue,
            transferDate=transferDate,
            transferTransactionHash=transferTransactionHash,
        )

    async def update_token_ownership(self, tokenOwnershipId: int, ownerAddress: Optional[str] = None, transferDate: Optional[datetime.datetime] = None, transferValue: Optional[int] = None, transferTransactionHash: Optional[str] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if ownerAddress is not None:
            values[TokenOwnershipsTable.c.ownerAddress.key] = ownerAddress
        if transferValue is not None:
            values[TokenOwnershipsTable.c.transferValue.key] = transferValue
        if transferDate is not None:
            values[TokenOwnershipsTable.c.transferDate.key] = transferDate
        if transferTransactionHash is not None:
            values[TokenOwnershipsTable.c.transferTransactionHash.key] = transferTransactionHash
        if len(values) > 0:
            values[TokenOwnershipsTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TokenOwnershipsTable.update().where(TokenOwnershipsTable.c.tokenOwnershipId == tokenOwnershipId).values(values).returning(TokenOwnershipsTable.c.tokenOwnershipId)
        await self._execute(query=query, connection=connection)

    @staticmethod
    def _get_create_token_multi_ownership(creationDate: datetime.datetime, retrievedTokenMultiOwnership: RetrievedTokenMultiOwnership) -> CreateRecordDict:  # type: ignore[misc]
        return {
            TokenMultiOwnershipsTable.c.createdDate.key: creationDate,
            TokenMultiOwnershipsTable.c.updatedDate.key: creationDate,
            TokenMultiOwnershipsTable.c.registryAddress.key: retrievedTokenMultiOwnership.registryAddress,
            TokenMultiOwnershipsTable.c.tokenId.key: retrievedTokenMultiOwnership.tokenId,
            TokenMultiOwnershipsTable.c.ownerAddress.key: retrievedTokenMultiOwnership.ownerAddress,
            TokenMultiOwnershipsTable.c.quantity.key: retrievedTokenMultiOwnership.quantity,
            TokenMultiOwnershipsTable.c.averageTransferValue.key: retrievedTokenMultiOwnership.averageTransferValue,
            TokenMultiOwnershipsTable.c.latestTransferDate.key: retrievedTokenMultiOwnership.latestTransferDate,
            TokenMultiOwnershipsTable.c.latestTransferTransactionHash.key: retrievedTokenMultiOwnership.latestTransferTransactionHash,
        }

    async def create_token_multi_ownership(self, retrievedTokenMultiOwnership: RetrievedTokenMultiOwnership, connection: Optional[DatabaseConnection] = None) -> int:
        creationDate = date_util.datetime_from_now()
        values = self._get_create_token_multi_ownership(creationDate=creationDate, retrievedTokenMultiOwnership=retrievedTokenMultiOwnership)
        query = TokenMultiOwnershipsTable.insert().values(values).returning(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId)
        result = await self._execute(query=query, connection=connection)
        tokenMultiOwnershipId = int(result.scalar_one())
        return tokenMultiOwnershipId

    async def create_token_multi_ownerships(self, retrievedTokenMultiOwnerships: Sequence[RetrievedTokenMultiOwnership], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedTokenMultiOwnerships) == 0:
            return []
        creationDate = date_util.datetime_from_now()
        tokenMultiOwnershipIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenMultiOwnerships, chunkSize=100):
            values = [self._get_create_token_multi_ownership(creationDate=creationDate, retrievedTokenMultiOwnership=retrievedTokenMultiOwnership) for retrievedTokenMultiOwnership in chunk]
            query = TokenMultiOwnershipsTable.insert().values(values).returning(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId)
            rows = await self._execute(query=query, connection=connection)
            tokenMultiOwnershipIds += [row[0] for row in rows]
        return tokenMultiOwnershipIds

    async def update_token_multi_ownership(self, tokenMultiOwnershipId: int, ownerAddress: Optional[str] = None, quantity: Optional[int] = None, averageTransferValue: Optional[int] = None, latestTransferDate: Optional[str] = None, latestTransferTransactionHash: Optional[str] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if ownerAddress is not None:
            values[TokenMultiOwnershipsTable.c.ownerAddress.key] = ownerAddress
        if quantity is not None:
            values[TokenMultiOwnershipsTable.c.quantity.key] = quantity
        if averageTransferValue is not None:
            values[TokenMultiOwnershipsTable.c.averageTransferValue.key] = averageTransferValue
        if latestTransferDate is not None:
            values[TokenMultiOwnershipsTable.c.latestTransferDate.key] = latestTransferDate
        if latestTransferTransactionHash is not None:
            values[TokenMultiOwnershipsTable.c.latestTransferTransactionHash.key] = latestTransferTransactionHash
        if len(values) > 0:
            values[TokenMultiOwnershipsTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TokenMultiOwnershipsTable.update().where(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId == tokenMultiOwnershipId).values(values).returning(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId)
        await self._execute(query=query, connection=connection)

    async def delete_token_multi_ownerships(self, tokenMultiOwnershipIds: Sequence[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(tokenMultiOwnershipIds) == 0:
            return
        query = TokenMultiOwnershipsTable.delete().where(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId.in_(tokenMultiOwnershipIds)).returning(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId)
        await self._execute(query=query, connection=connection)

    async def create_collection_hourly_activity(self, address: str, date: datetime.datetime, transferCount: int, mintCount: int, saleCount: int, totalValue: int, minimumValue: int, maximumValue: int, averageValue: int, connection: Optional[DatabaseConnection] = None) -> CollectionHourlyActivity:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            CollectionHourlyActivitiesTable.c.createdDate.key: createdDate,
            CollectionHourlyActivitiesTable.c.updatedDate.key: updatedDate,
            CollectionHourlyActivitiesTable.c.address.key: address,
            CollectionHourlyActivitiesTable.c.date.key: date,
            CollectionHourlyActivitiesTable.c.transferCount.key: transferCount,
            CollectionHourlyActivitiesTable.c.mintCount.key: mintCount,
            CollectionHourlyActivitiesTable.c.saleCount.key: saleCount,
            CollectionHourlyActivitiesTable.c.totalValue.key: totalValue,
            CollectionHourlyActivitiesTable.c.minimumValue.key: minimumValue,
            CollectionHourlyActivitiesTable.c.maximumValue.key: maximumValue,
            CollectionHourlyActivitiesTable.c.averageValue.key: averageValue,
        }
        query = CollectionHourlyActivitiesTable.insert().values(values).returning(CollectionHourlyActivitiesTable.c.collectionActivityId)
        result = await self._execute(query=query, connection=connection)
        collectionActivityId = int(result.scalar_one())
        return CollectionHourlyActivity(
            collectionActivityId=collectionActivityId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            address=address,
            date=date,
            transferCount=transferCount,
            mintCount=mintCount,
            saleCount=saleCount,
            totalValue=totalValue,
            minimumValue=minimumValue,
            maximumValue=maximumValue,
            averageValue=averageValue,
        )

    async def update_collection_hourly_activity(self, collectionActivityId: int, address: Optional[str], date: Optional[datetime.datetime], transferCount: Optional[int] = None, mintCount: Optional[int] = None, saleCount: Optional[int] = None, totalValue: Optional[int] = None, minimumValue: Optional[int] = None, maximumValue: Optional[int] = None, averageValue: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if address is not None:
            values[CollectionHourlyActivitiesTable.c.address.key] = address
        if date is not None:
            values[CollectionHourlyActivitiesTable.c.date.key] = date
        if transferCount is not None:
            values[CollectionHourlyActivitiesTable.c.transferCount.key] = transferCount
        if mintCount is not None:
            values[CollectionHourlyActivitiesTable.c.mintCount.key] = mintCount
        if saleCount is not None:
            values[CollectionHourlyActivitiesTable.c.saleCount.key] = saleCount
        if totalValue is not None:
            values[CollectionHourlyActivitiesTable.c.totalValue.key] = totalValue
        if minimumValue is not None:
            values[CollectionHourlyActivitiesTable.c.minimumValue.key] = minimumValue
        if maximumValue is not None:
            values[CollectionHourlyActivitiesTable.c.maximumValue.key] = maximumValue
        if averageValue is not None:
            values[CollectionHourlyActivitiesTable.c.averageValue.key] = averageValue
        if len(values) > 0:
            values[CollectionHourlyActivitiesTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = CollectionHourlyActivitiesTable.update().where(CollectionHourlyActivitiesTable.c.collectionActivityId == collectionActivityId).values(values).returning(CollectionHourlyActivitiesTable.c.collectionActivityId)
        await self._execute(query=query, connection=connection)

    async def create_collection_total_activity(self, address: str, transferCount: int, saleCount: int, totalValue: int, mintCount: int, minimumValue: int, maximumValue: int, averageValue: int, connection: Optional[DatabaseConnection] = None) -> CollectionTotalActivity:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            CollectionTotalActivitiesTable.c.createdDate.key: createdDate,
            CollectionTotalActivitiesTable.c.updatedDate.key: updatedDate,
            CollectionTotalActivitiesTable.c.address.key: address,
            CollectionTotalActivitiesTable.c.transferCount.key: transferCount,
            CollectionTotalActivitiesTable.c.mintCount.key: mintCount,
            CollectionTotalActivitiesTable.c.saleCount.key: saleCount,
            CollectionTotalActivitiesTable.c.totalValue.key: totalValue,
            CollectionTotalActivitiesTable.c.minimumValue.key: minimumValue,
            CollectionTotalActivitiesTable.c.maximumValue.key: maximumValue,
            CollectionTotalActivitiesTable.c.averageValue.key: averageValue,
        }
        query = CollectionTotalActivitiesTable.insert().values(values).returning(CollectionTotalActivitiesTable.c.collectionTotalActivityId)
        result = await self._execute(query=query, connection=connection)
        collectionTotalActivityId = int(result.scalar_one())
        return CollectionTotalActivity(
            collectionTotalActivityId=collectionTotalActivityId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            address=address,
            transferCount=transferCount,
            mintCount=mintCount,
            saleCount=saleCount,
            totalValue=totalValue,
            minimumValue=minimumValue,
            maximumValue=maximumValue,
            averageValue=averageValue,
        )

    async def update_collection_total_activity(self, collectionTotalActivityId: int, address: Optional[str], transferCount: Optional[int] = None, mintCount: Optional[int] = None, saleCount: Optional[int] = None, totalValue: Optional[int] = None, minimumValue: Optional[int] = None, maximumValue: Optional[int] = None, averageValue: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if address is not None:
            values[CollectionTotalActivitiesTable.c.address.key] = address
        if transferCount is not None:
            values[CollectionTotalActivitiesTable.c.transferCount.key] = transferCount
        if mintCount is not None:
            values[CollectionTotalActivitiesTable.c.mintCount.key] = mintCount
        if saleCount is not None:
            values[CollectionTotalActivitiesTable.c.saleCount.key] = saleCount
        if totalValue is not None:
            values[CollectionTotalActivitiesTable.c.totalValue.key] = totalValue
        if minimumValue is not None:
            values[CollectionTotalActivitiesTable.c.minimumValue.key] = minimumValue
        if maximumValue is not None:
            values[CollectionTotalActivitiesTable.c.maximumValue.key] = maximumValue
        if averageValue is not None:
            values[CollectionTotalActivitiesTable.c.averageValue.key] = averageValue
        if len(values) > 0:
            values[CollectionTotalActivitiesTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = CollectionTotalActivitiesTable.update().where(CollectionTotalActivitiesTable.c.collectionTotalActivityId == collectionTotalActivityId).values(values).returning(CollectionTotalActivitiesTable.c.collectionTotalActivityId)
        await self._execute(query=query, connection=connection)

    async def create_user_interaction(self, date: datetime.datetime, userAddress: str, command: str, signature: str, message: JSON, connection: Optional[DatabaseConnection] = None) -> UserInteraction:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            UserInteractionsTable.c.createdDate.key: createdDate,
            UserInteractionsTable.c.updatedDate.key: updatedDate,
            UserInteractionsTable.c.date.key: date,
            UserInteractionsTable.c.userAddress.key: userAddress,
            UserInteractionsTable.c.command.key: command,
            UserInteractionsTable.c.signature.key: signature,
            UserInteractionsTable.c.message.key: message,
        }
        query = UserInteractionsTable.insert().values(values).returning(UserInteractionsTable.c.userInteractionId)
        result = await self._execute(query=query, connection=connection)
        userInteractionId = int(result.scalar_one())
        return UserInteraction(
            userInteractionId=userInteractionId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            date=date,
            userAddress=userAddress,
            command=command,
            signature=signature,
            message=message,
        )

    async def create_latest_update(self, date: datetime.datetime, key: str, name: Optional[str], connection: Optional[DatabaseConnection] = None) -> LatestUpdate:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            LatestUpdatesTable.c.createdDate.key: createdDate,
            LatestUpdatesTable.c.updatedDate.key: updatedDate,
            LatestUpdatesTable.c.date.key: date,
            LatestUpdatesTable.c.key.key: key,
            LatestUpdatesTable.c.name.key: name,
        }
        query = LatestUpdatesTable.insert().values(values).returning(LatestUpdatesTable.c.latestUpdateId)
        result = await self._execute(query=query, connection=connection)
        latestUpdateId = int(result.scalar_one())
        return LatestUpdate(
            latestUpdateId=latestUpdateId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            key=key,
            name=name,
            date=date,
        )

    async def update_latest_update(self, latestUpdateId: int, key: Optional[str] = None, name: Optional[str] = _EMPTY_STRING, date: Optional[datetime.datetime] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if key is not None:
            values[LatestUpdatesTable.c.key.key] = key
        if name != _EMPTY_STRING:
            values[LatestUpdatesTable.c.name.key] = name
        if date is not None:
            values[LatestUpdatesTable.c.date.key] = date
        if len(values) > 0:
            values[LatestUpdatesTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = LatestUpdatesTable.update().where(LatestUpdatesTable.c.latestUpdateId == latestUpdateId).values(values).returning(LatestUpdatesTable.c.latestUpdateId)
        await self._execute(query=query, connection=connection)

    @staticmethod
    def _get_create_token_attributes_values(retrievedTokenAttribute: RetrievedTokenAttribute, createdDate: datetime.datetime, updatedDate: datetime.datetime) -> CreateRecordDict:  # type: ignore[misc]
        return {
            TokenAttributesTable.c.createdDate.key: createdDate,
            TokenAttributesTable.c.updatedDate.key: updatedDate,
            TokenAttributesTable.c.registryAddress.key: retrievedTokenAttribute.registryAddress,
            TokenAttributesTable.c.tokenId.key: retrievedTokenAttribute.tokenId,
            TokenAttributesTable.c.name.key: retrievedTokenAttribute.name,
            TokenAttributesTable.c.value.key: retrievedTokenAttribute.value,
        }

    async def create_token_attribute(self, retrievedTokenAttribute: RetrievedTokenAttribute, connection: Optional[DatabaseConnection] = None) -> int:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = self._get_create_token_attributes_values(retrievedTokenAttribute=retrievedTokenAttribute, createdDate=createdDate, updatedDate=updatedDate)
        query = TokenAttributesTable.insert().values(values).returning(TokenAttributesTable.c.tokenAttributeId)
        result = await self._execute(query=query, connection=connection)
        tokenAttributeId = int(result.scalar_one())
        return tokenAttributeId

    async def create_token_attributes(self, retrievedTokenAttributes: Sequence[RetrievedTokenAttribute], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedTokenAttributes) == 0:
            return []
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        tokenAttributeIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenAttributes, chunkSize=100):
            values = [self._get_create_token_attributes_values(retrievedTokenAttribute=retrievedTokenAttribute, createdDate=createdDate, updatedDate=updatedDate) for retrievedTokenAttribute in chunk]
            query = TokenAttributesTable.insert().values(values).returning(TokenAttributesTable.c.tokenAttributeId)
            rows = await self._execute(query=query, connection=connection)
            tokenAttributeIds += [row[0] for row in rows]
        return tokenAttributeIds

    async def delete_token_attribute(self, tokenAttributeId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = TokenAttributesTable.delete().where(TokenAttributesTable.c.tokenAttributeId == tokenAttributeId).returning(TokenAttributesTable.c.tokenAttributeId)
        await self._execute(query=query, connection=connection)

    async def delete_token_attributes(self, tokenAttributeIds: Sequence[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(tokenAttributeIds) == 0:
            return
        query = TokenAttributesTable.delete().where(TokenAttributesTable.c.tokenAttributeId.in_(tokenAttributeIds)).returning(TokenAttributesTable.c.tokenAttributeId)
        await self._execute(query=query, connection=connection)

    @staticmethod
    def _get_create_latest_token_listing_values(retrievedTokenListing: RetrievedTokenListing, createdDate: datetime.datetime, updatedDate: datetime.datetime) -> CreateRecordDict:  # type: ignore[misc]
        return {
            LatestTokenListingsTable.c.createdDate.key: createdDate,
            LatestTokenListingsTable.c.updatedDate.key: updatedDate,
            LatestTokenListingsTable.c.registryAddress.key: retrievedTokenListing.registryAddress,
            LatestTokenListingsTable.c.tokenId.key: retrievedTokenListing.tokenId,
            LatestTokenListingsTable.c.offererAddress.key: retrievedTokenListing.offererAddress,
            LatestTokenListingsTable.c.startDate.key: retrievedTokenListing.startDate,
            LatestTokenListingsTable.c.endDate.key: retrievedTokenListing.endDate,
            LatestTokenListingsTable.c.isValueNative.key: retrievedTokenListing.isValueNative,
            LatestTokenListingsTable.c.value.key: retrievedTokenListing.value,
            LatestTokenListingsTable.c.source.key: retrievedTokenListing.source,
            LatestTokenListingsTable.c.sourceId.key: retrievedTokenListing.sourceId,
        }

    async def create_latest_token_listing(self, retrievedTokenListing: RetrievedTokenListing, connection: Optional[DatabaseConnection] = None) -> int:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = self._get_create_latest_token_listing_values(retrievedTokenListing=retrievedTokenListing, createdDate=createdDate, updatedDate=updatedDate)
        query = LatestTokenListingsTable.insert().values(values).returning(LatestTokenListingsTable.c.latestTokenListingId)
        result = await self._execute(query=query, connection=connection)
        latestTokenListingId = int(result.scalar_one())
        return latestTokenListingId

    async def create_latest_token_listings(self, retrievedTokenListings: Sequence[RetrievedTokenListing], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedTokenListings) == 0:
            return []
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        latestTokenListingIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenListings, chunkSize=100):
            values = [self._get_create_latest_token_listing_values(retrievedTokenListing=retrievedTokenListing, createdDate=createdDate, updatedDate=updatedDate) for retrievedTokenListing in chunk]
            query = LatestTokenListingsTable.insert().values(values).returning(LatestTokenListingsTable.c.latestTokenListingId)
            rows = await self._execute(query=query, connection=connection)
            latestTokenListingIds += [row[0] for row in rows]
        return latestTokenListingIds

    async def delete_latest_token_listing(self, latestTokenListingId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = LatestTokenListingsTable.delete().where(LatestTokenListingsTable.c.latestTokenListingId == latestTokenListingId).returning(LatestTokenListingsTable.c.latestTokenListingId)
        await self._execute(query=query, connection=connection)

    async def delete_latest_token_listings(self, latestTokenListingIds: Sequence[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(latestTokenListingIds) == 0:
            return
        query = LatestTokenListingsTable.delete().where(LatestTokenListingsTable.c.latestTokenListingId.in_(latestTokenListingIds)).returning(LatestTokenListingsTable.c.latestTokenListingId)
        await self._execute(query=query, connection=connection)

    async def create_token_customization(self, registryAddress: str, tokenId: str, creatorAddress: str, signature: str, blockNumber: int, name: Optional[str], description: Optional[str], connection: Optional[DatabaseConnection] = None) -> TokenCustomization:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            TokenCustomizationsTable.c.createdDate.key: createdDate,
            TokenCustomizationsTable.c.updatedDate.key: updatedDate,
            TokenCustomizationsTable.c.registryAddress.key: registryAddress,
            TokenCustomizationsTable.c.tokenId.key: tokenId,
            TokenCustomizationsTable.c.creatorAddress.key: creatorAddress,
            TokenCustomizationsTable.c.signature.key: signature,
            TokenCustomizationsTable.c.blockNumber.key: blockNumber,
            TokenCustomizationsTable.c.name.key: name,
            TokenCustomizationsTable.c.description.key: description,
        }
        query = TokenCustomizationsTable.insert().values(values).returning(TokenCustomizationsTable.c.tokenCustomizationId)
        result = await self._execute(query=query, connection=connection)
        tokenCustomizationId = int(result.scalar_one())
        return TokenCustomization(
            tokenCustomizationId=tokenCustomizationId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            tokenId=tokenId,
            creatorAddress=creatorAddress,
            blockNumber=blockNumber,
            signature=signature,
            name=name,
            description=description,
        )

    async def delete_token_customization(self, tokenCustomizationId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = TokenCustomizationsTable.delete().where(TokenCustomizationsTable.c.tokenCustomizationId == tokenCustomizationId).returning(TokenCustomizationsTable.c.tokenCustomizationId)
        await self._execute(query=query, connection=connection)

    async def create_lock(self, name: str, expiryDate: datetime.datetime, connection: Optional[DatabaseConnection] = None) -> Lock:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            LocksTable.c.createdDate.key: createdDate,
            LocksTable.c.updatedDate.key: updatedDate,
            LocksTable.c.name.key: name,
            LocksTable.c.expiryDate.key: expiryDate,
        }
        query = LocksTable.insert().values(values).returning(LocksTable.c.lockId)
        result = await self._execute(query=query, connection=connection)
        lockId = int(result.scalar_one())
        return Lock(
            lockId=lockId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            name=name,
            expiryDate=expiryDate,
        )

    async def delete_lock(self, lockId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = LocksTable.delete().where(LocksTable.c.lockId == lockId).returning(LocksTable.c.lockId)
        await self._execute(query=query, connection=connection)

    async def create_user_profile(self, address: str, twitterId: Optional[str], discordId: Optional[str], signatureDict: JSON, connection: Optional[DatabaseConnection] = None) -> UserProfile:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            UserProfilesTable.c.createdDate.key: createdDate,
            UserProfilesTable.c.updatedDate.key: updatedDate,
            UserProfilesTable.c.address.key: address,
            UserProfilesTable.c.twitterId.key: twitterId,
            UserProfilesTable.c.discordId.key: discordId,
            UserProfilesTable.c.signature.key: signatureDict,
        }
        query = UserProfilesTable.insert().values(values).returning(UserProfilesTable.c.userProfileId)
        result = await self._execute(query=query, connection=connection)
        userProfileId = int(result.scalar_one())
        return UserProfile(
            userProfileId=userProfileId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            address=address,
            twitterId=twitterId,
            discordId=discordId,
            signature=Signature.from_dict(signatureDict),
        )

    async def update_user_profile(self, userProfileId: int, twitterId: Optional[str] = _EMPTY_STRING, discordId: Optional[str] = _EMPTY_STRING, signatureDict: Optional[JSON] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if twitterId != _EMPTY_STRING:
            values[UserProfilesTable.c.twitterId.key] = twitterId
        if discordId != _EMPTY_STRING:
            values[UserProfilesTable.c.discordId.key] = discordId
        if signatureDict is not None:
            values[UserProfilesTable.c.signature.key] = signatureDict
        if len(values) > 0:
            values[UserProfilesTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = UserProfilesTable.update().where(UserProfilesTable.c.userProfileId == userProfileId).values(values).returning(UserProfilesTable.c.userProfileId)
        await self._execute(query=query, connection=connection)

    async def create_twitter_credential(self, twitterId: str, accessToken: str, refreshToken: str, expiryDate: datetime.datetime, connection: Optional[DatabaseConnection] = None) -> TwitterCredential:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            TwitterCredentialsTable.c.createdDate.key: createdDate,
            TwitterCredentialsTable.c.updatedDate.key: updatedDate,
            TwitterCredentialsTable.c.twitterId.key: twitterId,
            TwitterCredentialsTable.c.accessToken.key: accessToken,
            TwitterCredentialsTable.c.refreshToken.key: refreshToken,
            TwitterCredentialsTable.c.expiryDate.key: expiryDate,
        }
        query = TwitterCredentialsTable.insert().values(values).returning(TwitterCredentialsTable.c.twitterCredentialId)
        result = await self._execute(query=query, connection=connection)
        twitterCredentialId = int(result.scalar_one())
        return TwitterCredential(
            twitterCredentialId=twitterCredentialId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            twitterId=twitterId,
            accessToken=accessToken,
            refreshToken=refreshToken,
            expiryDate=expiryDate,
        )

    async def update_twitter_credential(self, twitterCredentialId: int, accessToken: Optional[str] = None, refreshToken: Optional[str] = None, expiryDate: Optional[datetime.datetime] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if accessToken is not None:
            values[TwitterCredentialsTable.c.accessToken.key] = accessToken
        if refreshToken is not None:
            values[TwitterCredentialsTable.c.refreshToken.key] = refreshToken
        if expiryDate is not None:
            values[TwitterCredentialsTable.c.expiryDate.key] = expiryDate
        if len(values) > 0:
            values[TwitterCredentialsTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TwitterCredentialsTable.update().where(TwitterCredentialsTable.c.twitterCredentialId == twitterCredentialId).values(values).returning(TwitterCredentialsTable.c.twitterCredentialId)
        await self._execute(query=query, connection=connection)

    async def create_twitter_profile(self, twitterId: str, username: str, name: str, description: str, isVerified: bool, pinnedTweetId: Optional[str], followerCount: int, followingCount: int, tweetCount: int, connection: Optional[DatabaseConnection] = None) -> TwitterProfile:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            TwitterProfilesTable.c.createdDate.key: createdDate,
            TwitterProfilesTable.c.updatedDate.key: updatedDate,
            TwitterProfilesTable.c.twitterId.key: twitterId,
            TwitterProfilesTable.c.username.key: username,
            TwitterProfilesTable.c.name.key: name,
            TwitterProfilesTable.c.description.key: description,
            TwitterProfilesTable.c.isVerified.key: isVerified,
            TwitterProfilesTable.c.pinnedTweetId.key: pinnedTweetId,
            TwitterProfilesTable.c.followerCount.key: followerCount,
            TwitterProfilesTable.c.followingCount.key: followingCount,
            TwitterProfilesTable.c.tweetCount.key: tweetCount,
        }
        query = TwitterProfilesTable.insert().values(values).returning(TwitterProfilesTable.c.twitterProfileId)
        result = await self._execute(query=query, connection=connection)
        twitterProfileId = int(result.scalar_one())
        return TwitterProfile(
            twitterProfileId=twitterProfileId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            twitterId=twitterId,
            username=username,
            name=name,
            description=description,
            isVerified=isVerified,
            pinnedTweetId=pinnedTweetId,
            followerCount=followerCount,
            followingCount=followingCount,
            tweetCount=tweetCount,
        )

    async def update_twitter_profile(self, twitterProfileId: int, username: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, isVerified: Optional[bool] = None, pinnedTweetId: Optional[str] = None, followerCount: Optional[int] = None, followingCount: Optional[int] = None, tweetCount: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values: UpdateRecordDict = {}
        if username is not None:
            values[TwitterProfilesTable.c.username.key] = username
        if name is not None:
            values[TwitterProfilesTable.c.name.key] = name
        if description is not None:
            values[TwitterProfilesTable.c.description.key] = description
        if isVerified is not None:
            values[TwitterProfilesTable.c.isVerified.key] = isVerified
        if pinnedTweetId is not None:
            values[TwitterProfilesTable.c.pinnedTweetId.key] = pinnedTweetId
        if followerCount is not None:
            values[TwitterProfilesTable.c.followerCount.key] = followerCount
        if followingCount is not None:
            values[TwitterProfilesTable.c.followingCount.key] = followingCount
        if tweetCount is not None:
            values[TwitterProfilesTable.c.tweetCount.key] = tweetCount
        if len(values) > 0:
            values[TwitterProfilesTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TwitterProfilesTable.update().where(TwitterProfilesTable.c.twitterProfileId == twitterProfileId).values(values).returning(TwitterProfilesTable.c.twitterProfileId)
        await self._execute(query=query, connection=connection)

    async def create_account_gm(self, address: str, delegateAddress: Optional[str], date: datetime.datetime, streakLength: int, collectionCount: int, signatureMessage: str, signature: str, connection: Optional[DatabaseConnection] = None) -> AccountGm:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            AccountGmsTable.c.createdDate.key: createdDate,
            AccountGmsTable.c.updatedDate.key: updatedDate,
            AccountGmsTable.c.address.key: address,
            AccountGmsTable.c.delegateAddress.key: delegateAddress,
            AccountGmsTable.c.date.key: date,
            AccountGmsTable.c.streakLength.key: streakLength,
            AccountGmsTable.c.collectionCount.key: collectionCount,
            AccountGmsTable.c.signatureMessage.key: signatureMessage,
            AccountGmsTable.c.signature.key: signature,
        }
        query = AccountGmsTable.insert().values(values).returning(AccountGmsTable.c.accountGmId)
        result = await self._execute(query=query, connection=connection)
        accountGmId = int(result.scalar_one())
        return AccountGm(
            accountGmId=accountGmId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            address=address,
            delegateAddress=delegateAddress,
            date=date,
            streakLength=streakLength,
            collectionCount=collectionCount,
            signatureMessage=signatureMessage,
            signature=signature,
        )

    async def create_account_collection_gm(self, registryAddress: str, accountAddress: str, accountDelegateAddress: Optional[str], date: datetime.datetime, signatureMessage: str, signature: str, connection: Optional[DatabaseConnection] = None) -> AccountCollectionGm:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            AccountCollectionGmsTable.c.createdDate.key: createdDate,
            AccountCollectionGmsTable.c.updatedDate.key: updatedDate,
            AccountCollectionGmsTable.c.registryAddress.key: registryAddress,
            AccountCollectionGmsTable.c.accountAddress.key: accountAddress,
            AccountCollectionGmsTable.c.accountDelegateAddress.key: accountDelegateAddress,
            AccountCollectionGmsTable.c.date.key: date,
            AccountCollectionGmsTable.c.signatureMessage.key: signatureMessage,
            AccountCollectionGmsTable.c.signature.key: signature,
        }
        query = AccountCollectionGmsTable.insert().values(values).returning(AccountCollectionGmsTable.c.accountCollectionGmId)
        result = await self._execute(query=query, connection=connection)
        accountCollectionGmId = int(result.scalar_one())
        return AccountCollectionGm(
            accountCollectionGmId=accountCollectionGmId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            accountAddress=accountAddress,
            accountDelegateAddress=accountDelegateAddress,
            date=date,
            signatureMessage=signatureMessage,
            signature=signature,
        )

    @staticmethod
    def _get_create_collection_overlaps_values(retrievedCollectionOverlap: RetrievedCollectionOverlap, createdDate: datetime.datetime, updatedDate: datetime.datetime) -> CreateRecordDict:  # type: ignore[misc]
        return {
            TokenCollectionOverlapsTable.c.createdDate.key: createdDate,
            TokenCollectionOverlapsTable.c.updatedDate.key: updatedDate,
            TokenCollectionOverlapsTable.c.registryAddress.key: retrievedCollectionOverlap.registryAddress,
            TokenCollectionOverlapsTable.c.otherRegistryAddress.key: retrievedCollectionOverlap.otherRegistryAddress,
            TokenCollectionOverlapsTable.c.ownerAddress.key: retrievedCollectionOverlap.ownerAddress,
            TokenCollectionOverlapsTable.c.registryTokenCount.key: retrievedCollectionOverlap.registryTokenCount,
            TokenCollectionOverlapsTable.c.otherRegistryTokenCount.key: retrievedCollectionOverlap.otherRegistryTokenCount,
        }

    async def create_collection_overlap(self, retrievedCollectionOverlap: RetrievedCollectionOverlap, connection: Optional[DatabaseConnection] = None) -> int:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = self._get_create_collection_overlaps_values(retrievedCollectionOverlap=retrievedCollectionOverlap, createdDate=createdDate, updatedDate=updatedDate)
        query = TokenCollectionOverlapsTable.insert().values(values).returning(TokenCollectionOverlapsTable.c.collectionOverlapId)
        result = await self._execute(query=query, connection=connection)
        collectionOverlapId = int(result.scalar_one())
        return collectionOverlapId

    async def create_collection_overlaps(self, retrievedCollectionOverlaps: Sequence[RetrievedCollectionOverlap], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedCollectionOverlaps) == 0:
            return []
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        latestCollectionOverlapsIds = []
        for chunk in list_util.generate_chunks(lst=retrievedCollectionOverlaps, chunkSize=100):
            values = [self._get_create_collection_overlaps_values(retrievedCollectionOverlap=retrievedCollectionOverlap, createdDate=createdDate, updatedDate=updatedDate) for retrievedCollectionOverlap in chunk]
            query = TokenCollectionOverlapsTable.insert().values(values).returning(TokenCollectionOverlapsTable.c.collectionOverlapId)
            rows = await self._execute(query=query, connection=connection)
            latestCollectionOverlapsIds += [row[0] for row in rows]
        return latestCollectionOverlapsIds

    async def delete_collection_overlap(self, collectionOverlapId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = TokenCollectionOverlapsTable.delete().where(TokenCollectionOverlapsTable.c.collectionOverlapId == collectionOverlapId).returning(TokenCollectionOverlapsTable.c.collectionOverlapId)
        await self._execute(query=query, connection=connection)

    async def delete_collection_overlaps(self, collectionOverlapIds: Sequence[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(collectionOverlapIds) == 0:
            return
        query = TokenCollectionOverlapsTable.delete().where(TokenCollectionOverlapsTable.c.collectionOverlapId.in_(collectionOverlapIds)).returning(TokenCollectionOverlapsTable.c.collectionOverlapId)
        await self._execute(query=query, connection=connection)

    @staticmethod
    def _get_create_gallery_badge_holders_values(retrievedGalleryBadgeHolder: RetrievedGalleryBadgeHolder, createdDate: datetime.datetime, updatedDate: datetime.datetime) -> CreateRecordDict:  # type: ignore[misc]
        return {
            GalleryBadgeHoldersTable.c.createdDate.key: createdDate,
            GalleryBadgeHoldersTable.c.updatedDate.key: updatedDate,
            GalleryBadgeHoldersTable.c.registryAddress.key: retrievedGalleryBadgeHolder.registryAddress,
            GalleryBadgeHoldersTable.c.ownerAddress.key: retrievedGalleryBadgeHolder.ownerAddress,
            GalleryBadgeHoldersTable.c.badgeKey.key: retrievedGalleryBadgeHolder.badgeKey,
            GalleryBadgeHoldersTable.c.achievedDate.key: retrievedGalleryBadgeHolder.achievedDate,
        }

    async def create_gallery_badge_holder(self, retrievedGalleryBadgeHolder: RetrievedGalleryBadgeHolder, connection: Optional[DatabaseConnection] = None) -> int:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = self._get_create_gallery_badge_holders_values(retrievedGalleryBadgeHolder=retrievedGalleryBadgeHolder, createdDate=createdDate, updatedDate=updatedDate)
        query = GalleryBadgeHoldersTable.insert().values(values).returning(GalleryBadgeHoldersTable.c.galleryBadgeHolderId)
        result = await self._execute(query=query, connection=connection)
        galleryBadgeHolderId = int(result.scalar_one())
        return galleryBadgeHolderId

    async def create_gallery_badge_holders(self, retrievedGalleryBadgeHolders: Sequence[RetrievedGalleryBadgeHolder], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedGalleryBadgeHolders) == 0:
            return []
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        latestGalleryBadgeHolderIds = []
        for chunk in list_util.generate_chunks(lst=retrievedGalleryBadgeHolders, chunkSize=100):
            values = [self._get_create_gallery_badge_holders_values(retrievedGalleryBadgeHolder=retrievedGalleryBadgeHolder, createdDate=createdDate, updatedDate=updatedDate) for retrievedGalleryBadgeHolder in chunk]
            query = GalleryBadgeHoldersTable.insert().values(values).returning(GalleryBadgeHoldersTable.c.galleryBadgeHolderId)
            rows = await self._execute(query=query, connection=connection)
            latestGalleryBadgeHolderIds += [row[0] for row in rows]
        return latestGalleryBadgeHolderIds

    async def delete_gallery_badge_holder(self, galleryBadgeHolderId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = GalleryBadgeHoldersTable.delete().where(GalleryBadgeHoldersTable.c.galleryBadgeHolderId == galleryBadgeHolderId).returning(GalleryBadgeHoldersTable.c.galleryBadgeHolderId)
        await self._execute(query=query, connection=connection)

    async def delete_gallery_badge_holders(self, galleryBadgeHolderIds: Sequence[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(galleryBadgeHolderIds) == 0:
            return
        query = GalleryBadgeHoldersTable.delete().where(GalleryBadgeHoldersTable.c.galleryBadgeHolderId.in_(galleryBadgeHolderIds)).returning(GalleryBadgeHoldersTable.c.galleryBadgeHolderId)
        await self._execute(query=query, connection=connection)

    async def create_gallery_badge_assignment(self, registryAddress: str, ownerAddress: str, assignerAddress: str, badgeKey: str, achievedDate: datetime.datetime, signatureMessage: str, signature: str, connection: Optional[DatabaseConnection] = None) -> GalleryBadgeAssignment:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values: CreateRecordDict = {
            GalleryBadgeAssignmentsTable.c.createdDate.key: createdDate,
            GalleryBadgeAssignmentsTable.c.updatedDate.key: updatedDate,
            GalleryBadgeAssignmentsTable.c.registryAddress.key: registryAddress,
            GalleryBadgeAssignmentsTable.c.ownerAddress.key: ownerAddress,
            GalleryBadgeAssignmentsTable.c.assignerAddress.key: assignerAddress,
            GalleryBadgeAssignmentsTable.c.badgeKey.key: badgeKey,
            GalleryBadgeAssignmentsTable.c.achievedDate.key: achievedDate,
            GalleryBadgeAssignmentsTable.c.signatureMessage.key: signatureMessage,
            GalleryBadgeAssignmentsTable.c.signature.key: signature,
        }
        query = GalleryBadgeAssignmentsTable.insert().values(values).returning(GalleryBadgeAssignmentsTable.c.galleryBadgeAssignmentId)
        result = await self._execute(query=query, connection=connection)
        galleryBadgeAssignmentId = int(result.scalar_one())
        return GalleryBadgeAssignment(
            galleryBadgeAssignmentId=galleryBadgeAssignmentId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            ownerAddress=ownerAddress,
            assignerAddress=assignerAddress,
            badgeKey=badgeKey,
            achievedDate=achievedDate,
            signatureMessage=signatureMessage,
            signature=signature,
        )

    @staticmethod
    def _get_create_token_staking_values(retrievedTokenStaking: RetrievedTokenStaking , createdDate: datetime.datetime, updatedDate: datetime.datetime) -> CreateRecordDict:  # type: ignore[misc]
        return {
            TokenStakingsTable.c.createdDate.key: createdDate,
            TokenStakingsTable.c.updatedDate.key: updatedDate,
            TokenStakingsTable.c.stakingAddress.key: retrievedTokenStaking.stakingAddress,
            TokenStakingsTable.c.ownerAddress.key: retrievedTokenStaking.ownerAddress,
            TokenStakingsTable.c.registryAddress.key: retrievedTokenStaking.registryAddress,
            TokenStakingsTable.c.tokenId.key: retrievedTokenStaking.tokenId,
            TokenStakingsTable.c.stakedDate.key: retrievedTokenStaking.stakedDate,
            TokenStakingsTable.c.transactionHash.key: retrievedTokenStaking.transactionHash,
        }

    async def create_token_staking(self, retrievedTokenStaking: RetrievedTokenStaking, connection: Optional[DatabaseConnection] = None) -> int:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = self._get_create_token_staking_values(retrievedTokenStaking=retrievedTokenStaking, createdDate=createdDate, updatedDate=updatedDate)
        query = TokenStakingsTable.insert().values(values).returning(TokenStakingsTable.c.tokenStakingId)
        result = await self._execute(query=query, connection=connection)
        tokenStakingId = int(result.scalar_one())
        return tokenStakingId

    async def create_token_stakings(self, retrievedTokenStakings: Sequence[RetrievedTokenStaking], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedTokenStakings) == 0:
            return []
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        tokenStakingIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenStakings, chunkSize=100):
            values = [self._get_create_token_staking_values(retrievedTokenStaking=retrievedTokenStaking, createdDate=createdDate, updatedDate=updatedDate) for retrievedTokenStaking in chunk]
            query = TokenStakingsTable.insert().values(values).returning(TokenStakingsTable.c.tokenStakingId)
            rows = await self._execute(query=query, connection=connection)
            tokenStakingIds += [row[0] for row in rows]
        return tokenStakingIds

    async def delete_token_staking(self, tokenStakingId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = TokenStakingsTable.delete().where(TokenStakingsTable.c.tokenStakingId == tokenStakingId).returning(TokenStakingsTable.c.tokenStakingId)
        await self._execute(query=query, connection=connection)

    async def delete_token_stakings(self, tokenStakingIds: Sequence[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(tokenStakingIds) == 0:
            return
        query = TokenStakingsTable.delete().where(TokenStakingsTable.c.tokenStakingId.in_(tokenStakingIds)).returning(TokenStakingsTable.c.tokenStakingId)
        await self._execute(query=query, connection=connection)
