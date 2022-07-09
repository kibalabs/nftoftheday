import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from core.store.database import DatabaseConnection
from core.store.saver import Saver as CoreSaver
from core.util import date_util
from core.util import list_util
from sqlalchemy import JSON

from notd.model import Block
from notd.model import Collection
from notd.model import CollectionHourlyActivity
from notd.model import LatestUpdate
from notd.model import RetrievedTokenMultiOwnership
from notd.model import RetrievedTokenTransfer
from notd.model import TokenAttribute
from notd.model import TokenMetadata
from notd.model import TokenOwnership
from notd.model import UserInteraction
from notd.store.schema import BlocksTable
from notd.store.schema import CollectionHourlyActivityTable
from notd.store.schema import LatestUpdatesTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenMultiOwnershipsTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import UserInteractionsTable

_EMPTY_STRING = '_EMPTY_STRING'
_EMPTY_OBJECT = '_EMPTY_OBJECT'

class Saver(CoreSaver):

    @staticmethod
    def _get_create_token_transfer_values(retrievedTokenTransfer: RetrievedTokenTransfer) -> Dict[str, Union[str, int, float, None, bool]]:
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
            TokenTransfersTable.c.isMultiAddress: retrievedTokenTransfer.isMultiAddress,
            TokenTransfersTable.c.isInterstitial: retrievedTokenTransfer.isInterstitial,
            TokenTransfersTable.c.isSwap: retrievedTokenTransfer.isSwap,
            TokenTransfersTable.c.isBatch: retrievedTokenTransfer.isBatch,
            TokenTransfersTable.c.isOutbound: retrievedTokenTransfer.isOutbound,
        }

    async def create_token_transfer(self, retrievedTokenTransfer: RetrievedTokenTransfer, connection: Optional[DatabaseConnection] = None) -> int:
        values = self._get_create_token_transfer_values(retrievedTokenTransfer=retrievedTokenTransfer)
        query = TokenTransfersTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        tokenTransferId = result.inserted_primary_key[0]
        return tokenTransferId

    async def create_token_transfers(self, retrievedTokenTransfers: List[RetrievedTokenTransfer], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedTokenTransfers) == 0:
            return
        tokenTransferIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenTransfers, chunkSize=100):
            values = [self._get_create_token_transfer_values(retrievedTokenTransfer=retrievedTokenTransfer) for retrievedTokenTransfer in chunk]
            query = TokenTransfersTable.insert().values(values).returning(TokenTransfersTable.c.tokenTransferId)
            rows = await self._execute(query=query, connection=connection)
            tokenTransferIds += [row[0] for row in rows]
        return tokenTransferIds

    async def delete_token_transfer(self, tokenTransferId: int, connection: Optional[DatabaseConnection] = None) -> None:
        query = TokenTransfersTable.delete().where(TokenTransfersTable.c.tokenTransferId == tokenTransferId)
        await self._execute(query=query, connection=connection)

    async def delete_token_transfers(self, tokenTransferIds: List[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(tokenTransferIds) == 0:
            return
        query = TokenTransfersTable.delete().where(TokenTransfersTable.c.tokenTransferId.in_(tokenTransferIds))
        await self._execute(query=query, connection=connection)

    async def create_block(self, blockNumber: int, blockHash: str, blockDate: datetime.datetime, connection: Optional[DatabaseConnection] = None) -> Block:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            BlocksTable.c.createdDate.key: createdDate,
            BlocksTable.c.updatedDate.key: updatedDate,
            BlocksTable.c.blockNumber.key: blockNumber,
            BlocksTable.c.blockHash.key: blockHash,
            BlocksTable.c.blockDate.key: blockDate,
        }
        query = BlocksTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        blockId = result.inserted_primary_key[0]
        return Block(
            blockId=blockId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            blockNumber=blockNumber,
            blockHash=blockHash,
            blockDate=blockDate,
        )

    async def update_block(self, blockId: int, blockHash: Optional[str] = None, blockDate: Optional[datetime.datetime] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
        if blockHash is not None:
            values[BlocksTable.c.blockHash.key] = blockHash
        if blockDate is not None:
            values[BlocksTable.c.blockDate.key] = blockDate
        if len(values) > 0:
            values[BlocksTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = BlocksTable.update(BlocksTable.c.blockId == blockId).values(values)
        await self._execute(query=query, connection=connection)

    async def create_token_metadata(self, tokenId: int, registryAddress: str, metadataUrl: str, name: Optional[str], description: Optional[str], imageUrl: Optional[str], animationUrl: Optional[str], youtubeUrl: Optional[str], backgroundColor: Optional[str], frameImageUrl: Optional[str], attributes: Union[None, Dict, List], connection: Optional[DatabaseConnection] = None) -> TokenMetadata:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            TokenMetadatasTable.c.createdDate.key: createdDate,
            TokenMetadatasTable.c.updatedDate.key: updatedDate,
            TokenMetadatasTable.c.registryAddress.key: registryAddress,
            TokenMetadatasTable.c.tokenId.key: tokenId,
            TokenMetadatasTable.c.metadataUrl.key: metadataUrl,
            TokenMetadatasTable.c.name.key: name,
            TokenMetadatasTable.c.description.key: description,
            TokenMetadatasTable.c.imageUrl.key: imageUrl,
            TokenMetadatasTable.c.animationUrl.key: animationUrl,
            TokenMetadatasTable.c.youtubeUrl.key: youtubeUrl,
            TokenMetadatasTable.c.backgroundColor.key: backgroundColor,
            TokenMetadatasTable.c.frameImageUrl.key: frameImageUrl,
            TokenMetadatasTable.c.attributes.key: attributes,
        }
        query = TokenMetadatasTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        tokenMetadataId = result.inserted_primary_key[0]
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
            animationUrl=animationUrl,
            youtubeUrl=youtubeUrl,
            backgroundColor=backgroundColor,
            frameImageUrl=frameImageUrl,
            attributes=attributes,
        )

    async def update_token_metadata(self, tokenMetadataId: int, metadataUrl: Optional[str] = None, name: Optional[str] = _EMPTY_STRING, description: Optional[str] = _EMPTY_STRING, imageUrl: Optional[str] = _EMPTY_STRING, animationUrl: Optional[str] = _EMPTY_STRING, youtubeUrl: Optional[str] = _EMPTY_STRING, backgroundColor: Optional[str] = _EMPTY_STRING, frameImageUrl: Optional[str] = _EMPTY_STRING, attributes: Union[None, Dict, List] = _EMPTY_OBJECT, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
        if metadataUrl is not None:
            values[TokenMetadatasTable.c.metadataUrl.key] = metadataUrl
        if name != _EMPTY_STRING:
            values[TokenMetadatasTable.c.name.key] = name
        if description != _EMPTY_STRING:
            values[TokenMetadatasTable.c.description.key] = description
        if imageUrl != _EMPTY_STRING:
            values[TokenMetadatasTable.c.imageUrl.key] = imageUrl
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
        query = TokenMetadatasTable.update(TokenMetadatasTable.c.tokenMetadataId == tokenMetadataId).values(values)
        await self._execute(query=query, connection=connection)

    async def create_collection(self, address: str, name: Optional[str], symbol: Optional[str], description: Optional[str], imageUrl: Optional[str] , twitterUsername: Optional[str], instagramUsername: Optional[str], wikiUrl: Optional[str], openseaSlug: Optional[str], url: Optional[str], discordUrl: Optional[str], bannerImageUrl: Optional[str], doesSupportErc721: bool, doesSupportErc1155: bool, connection: Optional[DatabaseConnection] = None) -> Collection:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
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
        query = TokenCollectionsTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        collectionId = result.inserted_primary_key[0]
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
        values = {}
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
        query = TokenCollectionsTable.update(TokenCollectionsTable.c.collectionId == collectionId).values(values)
        await self._execute(query=query, connection=connection)

    async def create_token_ownership(self, registryAddress: str, tokenId: str, ownerAddress: str, transferValue: int, transferDate: datetime.datetime, transferTransactionHash: str, connection: Optional[DatabaseConnection] = None) -> TokenOwnership:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            TokenOwnershipsTable.c.createdDate.key: createdDate,
            TokenOwnershipsTable.c.updatedDate.key: updatedDate,
            TokenOwnershipsTable.c.registryAddress.key: registryAddress,
            TokenOwnershipsTable.c.tokenId.key: tokenId,
            TokenOwnershipsTable.c.ownerAddress.key: ownerAddress,
            TokenOwnershipsTable.c.transferValue.key: transferValue,
            TokenOwnershipsTable.c.transferDate.key: transferDate,
            TokenOwnershipsTable.c.transferTransactionHash.key: transferTransactionHash,
        }
        query = TokenOwnershipsTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        tokenOwnershipId = result.inserted_primary_key[0]
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

    async def update_token_ownership(self, tokenOwnershipId: int, ownerAddress: Optional[str] = None, transferDate: Optional[str] = None, transferValue: Optional[int] = None, transferTransactionHash: Optional[str] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
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
        query = TokenOwnershipsTable.update(TokenOwnershipsTable.c.tokenOwnershipId == tokenOwnershipId).values(values)
        await self._execute(query=query, connection=connection)

    @staticmethod
    def _get_create_token_multi_ownership(creationDate: datetime.datetime, retrievedTokenMultiOwnership: RetrievedTokenMultiOwnership) -> Dict[str, Union[str, int, float, None, bool, datetime.datetime]]:
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
        query = TokenMultiOwnershipsTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        tokenTransferId = result.inserted_primary_key[0]
        return tokenTransferId


    async def create_token_multi_ownerships(self, retrievedTokenMultiOwnerships: List[RetrievedTokenMultiOwnership], connection: Optional[DatabaseConnection] = None) -> List[int]:
        if len(retrievedTokenMultiOwnerships) == 0:
            return
        creationDate = date_util.datetime_from_now()
        tokenMultiOwnershipIds = []
        for chunk in list_util.generate_chunks(lst=retrievedTokenMultiOwnerships, chunkSize=100):
            values = [self._get_create_token_multi_ownership(creationDate=creationDate, retrievedTokenMultiOwnership=retrievedTokenMultiOwnership) for retrievedTokenMultiOwnership in chunk]
            query = TokenMultiOwnershipsTable.insert().values(values).returning(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId)
            rows = await self._execute(query=query, connection=connection)
            tokenMultiOwnershipIds += [row[0] for row in rows]
        return tokenMultiOwnershipIds

    async def update_token_multi_ownership(self, tokenMultiOwnershipId: int, ownerAddress: Optional[str] = None, quantity: Optional[int] = None, averageTransferValue: Optional[int] = None, latestTransferDate: Optional[str] = None, latestTransferTransactionHash: Optional[str] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
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
        query = TokenMultiOwnershipsTable.update(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId == tokenMultiOwnershipId).values(values)
        await self._execute(query=query, connection=connection)

    async def delete_token_multi_ownerships(self, tokenMultiOwnershipIds: List[int], connection: Optional[DatabaseConnection] = None) -> None:
        if len(tokenMultiOwnershipIds) == 0:
            return
        query = TokenMultiOwnershipsTable.delete().where(TokenMultiOwnershipsTable.c.tokenMultiOwnershipId.in_(tokenMultiOwnershipIds))
        await self._execute(query=query, connection=connection)

    async def create_collection_hourly_activity(self, address: str, date: datetime.datetime, transferCount: int, saleCount: int, totalValue: int, minimumValue: int, maximumValue: int, averageValue: int, connection: Optional[DatabaseConnection] = None) -> CollectionHourlyActivity:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            CollectionHourlyActivityTable.c.createdDate.key: createdDate,
            CollectionHourlyActivityTable.c.updatedDate.key: updatedDate,
            CollectionHourlyActivityTable.c.address.key: address,
            CollectionHourlyActivityTable.c.date.key: date,
            CollectionHourlyActivityTable.c.transferCount.key: transferCount,
            CollectionHourlyActivityTable.c.saleCount.key: saleCount,
            CollectionHourlyActivityTable.c.totalValue.key: totalValue,
            CollectionHourlyActivityTable.c.minimumValue.key: minimumValue,
            CollectionHourlyActivityTable.c.maximumValue.key: maximumValue,
            CollectionHourlyActivityTable.c.averageValue.key: averageValue,
        }
        query = CollectionHourlyActivityTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        collectionActivityId = result.inserted_primary_key[0]
        return CollectionHourlyActivity(
            collectionActivityId=collectionActivityId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            address=address,
            date=date,
            transferCount=transferCount,
            saleCount=saleCount,
            totalValue=totalValue,
            minimumValue=minimumValue,
            maximumValue=maximumValue,
            averageValue=averageValue,
        )

    async def update_collection_hourly_activity(self, collectionActivityId: int, address: Optional[str], date: Optional[datetime.datetime], transferCount: Optional[int] = None, saleCount: Optional[int] = None, totalValue: Optional[int] = None, minimumValue: Optional[int] = None, maximumValue: Optional[int] = None, averageValue: Optional[int] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
        if address is not None:
            values[CollectionHourlyActivityTable.c.address.key] = address
        if date is not None:
            values[CollectionHourlyActivityTable.c.date.key] = date
        if transferCount is not None:
            values[CollectionHourlyActivityTable.c.transferCount.key] = transferCount
        if saleCount is not None:
            values[CollectionHourlyActivityTable.c.saleCount.key] = saleCount
        if totalValue is not None:
            values[CollectionHourlyActivityTable.c.totalValue.key] = totalValue
        if minimumValue is not None:
            values[CollectionHourlyActivityTable.c.minimumValue.key] = minimumValue
        if maximumValue is not None:
            values[CollectionHourlyActivityTable.c.maximumValue.key] = maximumValue
        if averageValue is not None:
            values[CollectionHourlyActivityTable.c.averageValue.key] = averageValue
        if len(values) > 0:
            values[CollectionHourlyActivityTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = CollectionHourlyActivityTable.update(CollectionHourlyActivityTable.c.collectionActivityId == collectionActivityId).values(values)
        await self._execute(query=query, connection=connection)

    async def create_user_interaction(self, date: datetime.datetime, userAddress: str, command: str, signature: str, message: JSON, connection: Optional[DatabaseConnection] = None) -> UserInteraction:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            UserInteractionsTable.c.createdDate.key: createdDate,
            UserInteractionsTable.c.updatedDate.key: updatedDate,
            UserInteractionsTable.c.date.key: date,
            UserInteractionsTable.c.userAddress.key: userAddress,
            UserInteractionsTable.c.command.key: command,
            UserInteractionsTable.c.signature.key: signature,
            UserInteractionsTable.c.message.key: message,
        }
        query = UserInteractionsTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        userInteractionId = result.inserted_primary_key[0]
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
        values = {
            LatestUpdatesTable.c.createdDate.key: createdDate,
            LatestUpdatesTable.c.updatedDate.key: updatedDate,
            LatestUpdatesTable.c.date.key: date,
            LatestUpdatesTable.c.key.key: key,
            LatestUpdatesTable.c.name.key: name,
        }
        query = LatestUpdatesTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        latestUpdateId = result.inserted_primary_key[0]
        return LatestUpdate(
            latestUpdateId=latestUpdateId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            key=key,
            name=name,
            date=date,
        )

    async def update_latest_update(self, latestUpdateId: int, key: Optional[str] = None, name: Optional[str] = _EMPTY_STRING, date: Optional[datetime.datetime] = None, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
        if key is not None:
            values[LatestUpdatesTable.c.key.key] = key
        if name != _EMPTY_STRING:
            values[LatestUpdatesTable.c.name.key] = name
        if date is not None:
            values[LatestUpdatesTable.c.date.key] = date
        if len(values) > 0:
            values[LatestUpdatesTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = LatestUpdatesTable.update(LatestUpdatesTable.c.latestUpdateId == latestUpdateId).values(values)
        await self._execute(query=query, connection=connection)

    async def create_token_attribute(self, registryAddress: str, tokenId: str, attributeName: Optional[str], attributeValue: Optional[str], connection: Optional[DatabaseConnection] = None) -> TokenAttribute:
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        values = {
            TokenAttributesTable.c.createdDate.key: createdDate,
            TokenAttributesTable.c.updatedDate.key: updatedDate,
            TokenAttributesTable.c.registryAddress.key: registryAddress,
            TokenAttributesTable.c.tokenId.key: tokenId,
            TokenAttributesTable.c.attributeName.key: attributeName,
            TokenAttributesTable.c.attributeValue.key: attributeValue,
        }
        query = TokenAttributesTable.insert().values(values)
        result = await self._execute(query=query, connection=connection)
        tokenAttributeId = result.inserted_primary_key[0]
        return TokenAttribute(
            tokenAttributeId=tokenAttributeId,
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            tokenId=tokenId,
            attributeName=attributeName,
            attributeValue=attributeValue,
        )

    async def update_token_attribute(self, tokenAttributeId: int, attributeName: Optional[str] = _EMPTY_STRING, attributeValue: Optional[str] = _EMPTY_STRING, connection: Optional[DatabaseConnection] = None) -> None:
        values = {}
        if attributeName != _EMPTY_STRING:
            values[TokenAttributesTable.c.attributeName.key] = attributeName
        if attributeValue is not None:
            values[TokenAttributesTable.c.attributeValue.key] = attributeValue
        if len(values) > 0:
            values[TokenAttributesTable.c.updatedDate.key] = date_util.datetime_from_now()
        query = TokenAttributesTable.update(TokenAttributesTable.c.tokenAttributeId == tokenAttributeId).values(values)
        await self._execute(query=query, connection=connection)
