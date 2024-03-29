import contextlib
import datetime
import json
import urllib.parse as urlparse
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Optional

import sqlalchemy
from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util import chain_util
from core.util import date_util
from core.util import list_util
from core.web3.eth_client import EthClientInterface
from eth_account.messages import defunct_hash_message
from sqlalchemy.sql import functions as sqlalchemyfunc
from web3 import Web3

from notd.api.endpoints_v1 import InQueryParam
from notd.badge_manager import BadgeManager
from notd.collection_manager import CollectionManager
from notd.model import COLLECTION_SPRITE_CLUB_ADDRESS
from notd.model import STAKING_ADDRESSES
from notd.model import SUPER_COLLECTIONS
from notd.model import Airdrop
from notd.model import CollectionAttribute
from notd.model import CollectionOverlap
from notd.model import CollectionOverlapOwner
from notd.model import CollectionOverlapSummary
from notd.model import GalleryBadgeHolder
from notd.model import GallerySuperCollectionUserRow
from notd.model import GalleryToken
from notd.model import GalleryUser
from notd.model import GalleryUserRow
from notd.model import ListResponse
from notd.model import OwnedCollection
from notd.model import Signature
from notd.model import SuperCollectionEntry
from notd.model import SuperCollectionOverlap
from notd.model import Token
from notd.model import TokenCustomization
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import CollectionTotalActivitiesTable
from notd.store.schema import GalleryBadgeHoldersView
from notd.store.schema import OrderedTokenListingsView
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCollectionOverlapsTable
from notd.store.schema import TokenCollectionsTable
from notd.store.schema import TokenCustomizationsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenOwnershipsView
from notd.store.schema import TokenStakingsTable
from notd.store.schema import TwitterProfilesTable
from notd.store.schema import UserProfilesTable
from notd.store.schema import UserRegistryFirstOwnershipsMaterializedView
from notd.store.schema import UserRegistryOrderedOwnershipsMaterializedView
from notd.store.schema_conversions import collection_from_row
from notd.store.schema_conversions import gallery_badge_holder_from_row
from notd.store.schema_conversions import token_customization_from_row
from notd.store.schema_conversions import token_listing_from_row
from notd.store.schema_conversions import token_metadata_from_row
from notd.store.schema_conversions import token_staking_from_row
from notd.store.schema_conversions import twitter_profile_from_row
from notd.store.schema_conversions import user_profile_from_row
from notd.twitter_manager import TwitterManager

SPRITE_CLUB_STORMDROP_REGISTRY_ADDRESS = '0x27C86e1c64622643049d3D7966580Cb832dCd1EF'


class GalleryManager:

    def __init__(self, ethClient: EthClientInterface, retriever: Retriever, saver: Saver, twitterManager: TwitterManager, collectionManager: CollectionManager, badgeManager: BadgeManager) -> None:
        self.ethClient = ethClient
        self.retriever = retriever
        self.saver = saver
        self.twitterManager = twitterManager
        self.collectionManager = collectionManager
        self.badgeManager = badgeManager
        with open('./contracts/SpriteClub.json', 'r') as contractJsonFile:
            self.spriteClubContract = json.load(contractJsonFile)
        with open('./contracts/SpriteClubStormdrop.json', 'r') as contractJsonFile:
            self.spriteClubStormdropContract = json.load(contractJsonFile)
        self.spriteClubStormdropClaimedFunctionAbi = [internalAbi for internalAbi in self.spriteClubStormdropContract['abi'] if internalAbi.get('name') == 'claimedSpriteItemIdMap'][0]
        with open('./contracts/SpriteClubStormdropIdMap.json', 'r') as contractJsonFile:
            self.spriteClubStormdropIdMap = json.load(contractJsonFile)
        self.web3 = Web3()

    async def twitter_login(self, account: str, signatureJson: str, initialUrl: str) -> None:
        # TODO(krishan711): validate the signatureJson
        signature = Signature.from_dict(signatureDict=json.loads(urlparse.unquote(signatureJson)))
        await self.twitterManager.login(account=account, signature=signature, initialUrl=initialUrl)

    async def twitter_login_callback(self, state: str, code: Optional[str], error: Optional[str]) -> None:
        await self.twitterManager.login_callback(state=state, code=code, error=error)

    async def get_gallery_token(self, registryAddress: str, tokenId: str) -> GalleryToken:
        query = (
            sqlalchemy.select(TokenMetadatasTable, TokenCustomizationsTable, OrderedTokenListingsView, sqlalchemyfunc.sum(TokenOwnershipsView.c.quantity).label('quantity'))
                .join(TokenCustomizationsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenCustomizationsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenCustomizationsTable.c.tokenId), isouter=True)
                .join(TokenOwnershipsView, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenOwnershipsView.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenOwnershipsView.c.tokenId))
                .join(OrderedTokenListingsView, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == OrderedTokenListingsView.c.registryAddress, TokenMetadatasTable.c.tokenId == OrderedTokenListingsView.c.tokenId, OrderedTokenListingsView.c.tokenListingIndex == 1), isouter=True)
                .where(TokenMetadatasTable.c.registryAddress == registryAddress)
                .where(TokenMetadatasTable.c.tokenId == tokenId)
                .group_by(TokenMetadatasTable.c.tokenMetadataId, TokenCustomizationsTable.c.tokenCustomizationId, OrderedTokenListingsView.c, TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId)  # type: ignore[arg-type]
        )
        result = await self.retriever.database.execute(query=query)
        row = result.mappings().first()
        if not row:
            raise NotFoundException(message=f'GalleryToken with registry:{registryAddress} tokenId:{tokenId} not found')
        galleryToken = GalleryToken(
            tokenMetadata=token_metadata_from_row(row),
            tokenCustomization=token_customization_from_row(row) if row[TokenCustomizationsTable.c.tokenCustomizationId] else None,
            tokenListing=token_listing_from_row(row, OrderedTokenListingsView) if row[OrderedTokenListingsView.c.latestTokenListingId] else None,
            tokenStaking=None,
            quantity=row['quantity'],
        )
        return galleryToken

    async def list_collection_token_airdrops(self, registryAddress: str, tokenId: str) -> List[Airdrop]:
        registryAddress = chain_util.normalize_address(registryAddress)
        tokenKey = Token(registryAddress=registryAddress, tokenId=tokenId)
        if registryAddress == COLLECTION_SPRITE_CLUB_ADDRESS:
            claimedTokenId = (await self.ethClient.call_function(toAddress=SPRITE_CLUB_STORMDROP_REGISTRY_ADDRESS, contractAbi=self.spriteClubStormdropContract['abi'], functionAbi=self.spriteClubStormdropClaimedFunctionAbi, arguments={'': int(tokenId)}))[0]
            isClaimed = claimedTokenId > 0
            claimTokenId = claimedTokenId or self.spriteClubStormdropIdMap[tokenId]
            claimTokenKey = Token(registryAddress=SPRITE_CLUB_STORMDROP_REGISTRY_ADDRESS, tokenId=claimTokenId)
            return [Airdrop(name='Stormdrop ⚡️⚡️', tokenKey=tokenKey, isClaimed=isClaimed, claimTokenKey=claimTokenKey, claimUrl='https://stormdrop.spriteclubnft.com')]
        return []

    async def get_collection_attributes(self, registryAddress: str) -> List[CollectionAttribute]:
        # NOTE(krishan711): deal with none values better!
        registryAddress = chain_util.normalize_address(value=registryAddress)
        query = (
            sqlalchemy.select(TokenAttributesTable.c.name, TokenAttributesTable.c.value)
            .distinct()
            .where(TokenAttributesTable.c.registryAddress == registryAddress)
            .where(TokenAttributesTable.c.value.is_not(None))
            .order_by(TokenAttributesTable.c.name.asc(), TokenAttributesTable.c.value.asc())
        )
        result = await self.retriever.database.execute(query=query)
        collectionAttributeNameMap: Dict[str, CollectionAttribute] = {}
        for name, value in result:
            collectionAttribute = collectionAttributeNameMap.get(name)
            if not collectionAttribute:
                collectionAttribute = CollectionAttribute(name=name, values=[])
                collectionAttributeNameMap[name] = collectionAttribute
            collectionAttribute.values.append(value)
        return list(collectionAttributeNameMap.values())

    async def query_collection_tokens(self, registryAddress: str, limit: int, offset: int, ownerAddress: Optional[str] = None, minPrice: Optional[int] = None, maxPrice: Optional[int] = None, isListed: Optional[bool] = None, tokenIdIn: Optional[List[str]] = None, attributeFilters: Optional[List[InQueryParam]] = None, order: Optional[str] = None) -> List[GalleryToken]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        await self.collectionManager.get_collection_by_address(address=registryAddress)
        usesListings = isListed or minPrice or maxPrice
        query = (
            sqlalchemy.select(TokenMetadatasTable, TokenCustomizationsTable, OrderedTokenListingsView, TokenStakingsTable, sqlalchemyfunc.sum(TokenOwnershipsView.c.quantity).label('quantity'))
                .join(TokenOwnershipsView, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenOwnershipsView.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenOwnershipsView.c.tokenId))
                .join(TokenCustomizationsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenCustomizationsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenCustomizationsTable.c.tokenId), isouter=True)
                .join(OrderedTokenListingsView, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == OrderedTokenListingsView.c.registryAddress, TokenMetadatasTable.c.tokenId == OrderedTokenListingsView.c.tokenId, OrderedTokenListingsView.c.tokenListingIndex == 1), isouter=True)
                .join(TokenStakingsTable, sqlalchemy.and_(TokenOwnershipsView.c.registryAddress == TokenStakingsTable.c.registryAddress, TokenOwnershipsView.c.ownerAddress == TokenStakingsTable.c.stakingAddress, TokenOwnershipsView.c.tokenId == TokenStakingsTable.c.tokenId), isouter=True)
                .where(TokenMetadatasTable.c.registryAddress == registryAddress)
                .where(TokenOwnershipsView.c.quantity > 0)
                .group_by(TokenMetadatasTable.c.tokenMetadataId, TokenCustomizationsTable.c.tokenCustomizationId, OrderedTokenListingsView.c, TokenStakingsTable.c, TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId)  # type: ignore[arg-type]
                .limit(limit)
                .offset(offset)
        )
        order = order or 'TOKENID_ASC'
        if  order == "TOKENID_ASC":
            query = query.order_by(sqlalchemy.cast(TokenMetadatasTable.c.tokenId, sqlalchemy.Integer).asc())
        elif order == "TOKENID_DESC":
            query = query.order_by(sqlalchemy.cast(TokenMetadatasTable.c.tokenId, sqlalchemy.Integer).desc())
        elif order == "QUANTITY_ASC":
            query = query.order_by(sqlalchemyfunc.sum(TokenOwnershipsView.c.quantity).asc(), sqlalchemy.cast(TokenMetadatasTable.c.tokenId, sqlalchemy.Integer).asc())
        elif order == "QUANTITY_DESC":
            query = query.order_by(sqlalchemyfunc.sum(TokenOwnershipsView.c.quantity).desc(), sqlalchemy.cast(TokenMetadatasTable.c.tokenId, sqlalchemy.Integer).asc())
        elif order == "PRICE_ASC":
            query = query.order_by(sqlalchemy.nulls_last(sqlalchemy.cast(OrderedTokenListingsView.c.value, sqlalchemy.NUMERIC).asc()), sqlalchemy.cast(TokenMetadatasTable.c.tokenId, sqlalchemy.Integer).asc())
        elif order == "PRICE_DESC":
            query = query.order_by(sqlalchemy.nulls_last(sqlalchemy.cast(OrderedTokenListingsView.c.value, sqlalchemy.NUMERIC).desc()), sqlalchemy.cast(TokenMetadatasTable.c.tokenId, sqlalchemy.Integer).asc())
        else:
            raise BadRequestException('Unknown order')
        if usesListings:
            query = query.where(OrderedTokenListingsView.c.latestTokenListingId.is_not(None))
        if minPrice:
            query = query.where(OrderedTokenListingsView.c.value >= sqlalchemy.sql.expression.cast(minPrice, sqlalchemy.Numeric(precision=256, scale=0)))
        if maxPrice:
            query = query.where(OrderedTokenListingsView.c.value <= sqlalchemy.sql.expression.cast(maxPrice, sqlalchemy.Numeric(precision=256, scale=0)))
        if ownerAddress:
            query = query.where(sqlalchemy.or_(TokenOwnershipsView.c.ownerAddress == ownerAddress, TokenStakingsTable.c.ownerAddress == ownerAddress))
        if tokenIdIn:
            query = query.where(TokenMetadatasTable.c.tokenId.in_(tokenIdIn))
        if attributeFilters:
            for index, attributeFilter in enumerate(attributeFilters):
                query = query.join(TokenAttributesTable.alias(f'attributes-{index}'), sqlalchemy.and_(
                    TokenMetadatasTable.c.registryAddress == TokenAttributesTable.alias(f'attributes-{index}').c.registryAddress,
                    TokenMetadatasTable.c.tokenId == TokenAttributesTable.alias(f'attributes-{index}').c.tokenId,
                    TokenAttributesTable.alias(f'attributes-{index}').c.name == attributeFilter.fieldName,
                    TokenAttributesTable.alias(f'attributes-{index}').c.value.in_(attributeFilter.values),
                ))
        result = await self.retriever.database.execute(query=query)
        galleryTokens = []
        for row in result.mappings():
            galleryTokens.append(GalleryToken(
                tokenMetadata=token_metadata_from_row(row),
                tokenCustomization=token_customization_from_row(row) if row[TokenCustomizationsTable.c.tokenCustomizationId] else None,
                tokenListing=token_listing_from_row(row, OrderedTokenListingsView) if row[OrderedTokenListingsView.c.latestTokenListingId] else None,
                tokenStaking=token_staking_from_row(row) if row[TokenStakingsTable.c.tokenStakingId] else None,
                quantity=row['quantity'],
            ))
        return galleryTokens

    async def submit_treasure_hunt_for_collection_token(self, registryAddress: str, tokenId: str, userAddress: str, signature: str) -> None:
        if registryAddress != COLLECTION_SPRITE_CLUB_ADDRESS:
            raise BadRequestException(f'Collection does not have an active treasure hunt')
        if tokenId != '101':
            raise BadRequestException(f'Incorrect token')
        command = 'COMPLETE_TREASURE_HUNT'
        message = {
            'registryAddress': registryAddress,
            'tokenId': tokenId,
        }
        signedMessage = json.dumps({ 'command': command, 'message': message }, separators=(',', ':'))
        messageHash = defunct_hash_message(text=signedMessage)
        signer = self.web3.eth.account._recover_hash(message_hash=messageHash, signature=signature)  # pylint: disable=protected-access
        if signer != userAddress:
            raise BadRequestException('Invalid signature')
        await self.saver.create_user_interaction(date=date_util.datetime_from_now(), userAddress=userAddress, command=command, signature=signature, message=message)

    async def create_customization_for_collection_token(self, registryAddress: str, tokenId: str, creatorAddress: str, signature: str, blockNumber: int, name: Optional[str], description: Optional[str]) -> TokenCustomization:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        if registryAddress != COLLECTION_SPRITE_CLUB_ADDRESS:
            raise BadRequestException(f'Collection does not support customization')
        # if name and _is_profane(value=name):
        #     raise BadRequestException(f'Name cannot contain profanities')
        # if description and _is_profane(value=description):
        #     raise BadRequestException(f'Description cannot contain profanities')
        creatorAddress = chain_util.normalize_address(value=creatorAddress)
        command = 'CREATE_CUSTOMIZATION'
        message = {
            'registryAddress': registryAddress,
            'tokenId': tokenId,
            'creatorAddress': creatorAddress,
            'blockNumber': blockNumber,
            'name': name,
            'description': description,
        }
        signedMessage = json.dumps({ 'command': command, 'message': message }, indent=2, ensure_ascii=False)
        messageHash = defunct_hash_message(text=signedMessage)
        signer = self.web3.eth.account._recover_hash(message_hash=messageHash, signature=signature)  # pylint: disable=protected-access
        if signer != creatorAddress:
            raise BadRequestException('Invalid signature')
        latestBlockNumber = await self.ethClient.get_latest_block_number()
        blockDifference = latestBlockNumber - blockNumber
        if blockDifference < 0 or blockDifference > 20:
            raise BadRequestException('Signature too old')
        ownership = await self.retriever.get_token_ownership_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        if ownership.ownerAddress != creatorAddress:
            raise BadRequestException('Signer is not owner')
        async with self.saver.create_transaction() as connection:
            tokenCustomization = None
            with contextlib.suppress(NotFoundException):
                tokenCustomization = await self.retriever.get_token_customization_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId, connection=connection)
            if tokenCustomization:
                await self.saver.delete_token_customization(tokenCustomizationId=tokenCustomization.tokenCustomizationId)
            tokenCustomization = await self.saver.create_token_customization(registryAddress=registryAddress, tokenId=tokenId, creatorAddress=creatorAddress, signature=signature, blockNumber=blockNumber, name=name, description=description, connection=connection)
        return tokenCustomization

    async def get_gallery_user(self, registryAddress: str, userAddress: str) -> GalleryUser:
        ownedCountColumn = sqlalchemyfunc.sum(UserRegistryOrderedOwnershipsMaterializedView.c.quantity).label('ownedTokenCount')
        uniqueOwnedCountColumn = sqlalchemyfunc.count(UserRegistryOrderedOwnershipsMaterializedView.c.tokenId).label('uniqueOwnedTokenCount')
        userQuery = (
            sqlalchemy.select(ownedCountColumn, uniqueOwnedCountColumn, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserProfilesTable, TwitterProfilesTable, UserRegistryFirstOwnershipsMaterializedView.c.joinDate)
                .join(UserProfilesTable, UserProfilesTable.c.address == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, isouter=True)
                .join(TwitterProfilesTable, TwitterProfilesTable.c.twitterId == UserProfilesTable.c.twitterId, isouter=True)
                .join(UserRegistryFirstOwnershipsMaterializedView, sqlalchemy.and_(UserRegistryFirstOwnershipsMaterializedView.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserRegistryFirstOwnershipsMaterializedView.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress), isouter=True)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress == userAddress)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 0)
                .group_by(UserProfilesTable.c.userProfileId, TwitterProfilesTable.c.twitterProfileId, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserRegistryFirstOwnershipsMaterializedView.c.joinDate)
        )
        userResult = await self.retriever.database.execute(query=userQuery)
        userRow = userResult.mappings().first()
        galleryUser = GalleryUser(
            address=userAddress,
            registryAddress=registryAddress,
            userProfile=user_profile_from_row(userRow) if userRow and userRow[UserProfilesTable.c.userProfileId] else None,
            twitterProfile=twitter_profile_from_row(userRow) if userRow and userRow[TwitterProfilesTable.c.twitterProfileId] else None,
            joinDate=userRow[UserRegistryFirstOwnershipsMaterializedView.c.joinDate] if userRow else None,
        )
        return galleryUser

    async def list_gallery_user_badges(self, registryAddress: str, userAddress: str) -> List[GalleryBadgeHolder]:
        galleryUserBadgesQuery = (
            sqlalchemy.select(GalleryBadgeHoldersView, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
                .join(UserRegistryOrderedOwnershipsMaterializedView, sqlalchemy.and_(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == GalleryBadgeHoldersView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress == GalleryBadgeHoldersView.c.ownerAddress))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
                .where(GalleryBadgeHoldersView.c.ownerAddress == userAddress)
        )
        galleryUserBadgesResult = await self.retriever.database.execute(query=galleryUserBadgesQuery)
        galleryBadgeHolders: Dict[str, List[GalleryBadgeHolder]] = defaultdict(list)
        for galleryBadgeHolderRow in galleryUserBadgesResult.mappings():
            galleryBadgeHolders[userAddress].append(gallery_badge_holder_from_row(galleryBadgeHolderRow))
        galleryBadges=galleryBadgeHolders[userAddress]
        return galleryBadges

    async def query_collection_users(self, registryAddress: str, order: Optional[str], limit: int, offset: int) -> ListResponse[GalleryUserRow]:
        ownedCountColumn = sqlalchemyfunc.sum(UserRegistryOrderedOwnershipsMaterializedView.c.quantity).label('ownedTokenCount')
        uniqueOwnedCountColumn = sqlalchemyfunc.count(UserRegistryOrderedOwnershipsMaterializedView.c.tokenId).label('uniqueOwnedTokenCount')
        usersQueryBase = (
            sqlalchemy.select(ownedCountColumn, uniqueOwnedCountColumn, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserProfilesTable, TwitterProfilesTable, UserRegistryFirstOwnershipsMaterializedView.c.joinDate)
                .join(UserProfilesTable, UserProfilesTable.c.address == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, isouter=True)
                .join(TwitterProfilesTable, TwitterProfilesTable.c.twitterId == UserProfilesTable.c.twitterId, isouter=True)
                .join(UserRegistryFirstOwnershipsMaterializedView, sqlalchemy.and_(UserRegistryFirstOwnershipsMaterializedView.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserRegistryFirstOwnershipsMaterializedView.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress), isouter=True)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 0)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.not_in(STAKING_ADDRESSES))
                .group_by(UserProfilesTable.c.userProfileId, TwitterProfilesTable.c.twitterProfileId, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserRegistryFirstOwnershipsMaterializedView.c.joinDate)
        )
        usersQuery = usersQueryBase.limit(limit).offset(offset)
        if not order or order == 'TOKENCOUNT_DESC':
            usersQuery = usersQuery.order_by(ownedCountColumn.desc())
        elif order == 'TOKENCOUNT_ASC':
            usersQuery = usersQuery.order_by(ownedCountColumn.asc(), UserRegistryFirstOwnershipsMaterializedView.c.joinDate.desc())
        elif order == 'UNIQUETOKENCOUNT_DESC':
            usersQuery = usersQuery.order_by(uniqueOwnedCountColumn.desc())
        elif order == 'UNIQUETOKENCOUNT_ASC':
            usersQuery = usersQuery.order_by(uniqueOwnedCountColumn.asc(), UserRegistryFirstOwnershipsMaterializedView.c.joinDate.desc())
        elif order == 'FOLLOWERCOUNT_DESC':
            usersQuery = usersQuery.order_by(sqlalchemyfunc.coalesce(TwitterProfilesTable.c.followerCount, 0).desc(), ownedCountColumn.desc())
        elif order == 'FOLLOWERCOUNT_ASC':
            usersQuery = usersQuery.order_by(sqlalchemyfunc.coalesce(TwitterProfilesTable.c.followerCount, 0).asc(), ownedCountColumn.desc())
        # NOTE(krishan711): joindate ordering is inverse because its displayed as time ago so oldest is highest
        elif order == 'JOINDATE_DESC':
            usersQuery = usersQuery.order_by(UserRegistryFirstOwnershipsMaterializedView.c.joinDate.asc(), ownedCountColumn.desc())
        elif order == 'JOINDATE_ASC':
            usersQuery = usersQuery.order_by(UserRegistryFirstOwnershipsMaterializedView.c.joinDate.desc(), ownedCountColumn.desc())
        else:
            raise BadRequestException('Unknown order')
        usersResult = await self.retriever.database.execute(query=usersQuery)
        userRows = list(usersResult.mappings())
        ownerAddresses = [userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress] for userRow in userRows]
        userCountsQuery = (
            sqlalchemy.select(sqlalchemyfunc.count(sqlalchemy.distinct(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
        )
        userCountsResult = await self.retriever.database.execute(query=userCountsQuery)
        totalCountRow = userCountsResult.first()
        chosenTokensQuery = (
            sqlalchemy.select(TokenMetadatasTable, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
                .join(UserRegistryOrderedOwnershipsMaterializedView, sqlalchemy.and_(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == TokenMetadatasTable.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.tokenId == TokenMetadatasTable.c.tokenId))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == registryAddress)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.in_(ownerAddresses))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex <= 5)
                .order_by(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex.asc())
        )
        chosenTokensResult = await self.retriever.database.execute(query=chosenTokensQuery)
        chosenTokens: Dict[str, List[TokenMetadata]] = defaultdict(list)
        for chosenTokenRow in chosenTokensResult.mappings():
            chosenTokens[chosenTokenRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]].append(token_metadata_from_row(chosenTokenRow))
        galleryBadgeHoldersQuery = (
            sqlalchemy.select(GalleryBadgeHoldersView)
                .where(GalleryBadgeHoldersView.c.registryAddress == registryAddress)
                .where(GalleryBadgeHoldersView.c.ownerAddress.in_(ownerAddresses))
        )
        galleryBadgeHoldersResult = await self.retriever.database.execute(query=galleryBadgeHoldersQuery)
        galleryBadgeHolders: Dict[str, List[GalleryBadgeHolder]] = defaultdict(list)
        for galleryBadgeHolderRow in galleryBadgeHoldersResult.mappings():
            galleryBadgeHolders[galleryBadgeHolderRow[GalleryBadgeHoldersView.c.ownerAddress]].append(gallery_badge_holder_from_row(galleryBadgeHolderRow))
        items = [GalleryUserRow(
            galleryUser=GalleryUser(
                address=userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress],
                registryAddress=registryAddress,
                userProfile=user_profile_from_row(userRow) if userRow and userRow[UserProfilesTable.c.userProfileId] else None,
                twitterProfile=twitter_profile_from_row(userRow) if userRow and userRow[TwitterProfilesTable.c.twitterProfileId] else None,
                joinDate=userRow[UserRegistryFirstOwnershipsMaterializedView.c.joinDate],
            ),
            ownedTokenCount=userRow['ownedTokenCount'],
            uniqueOwnedTokenCount=userRow['uniqueOwnedTokenCount'],
            chosenOwnedTokens=chosenTokens[userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]],
            galleryBadgeHolders=galleryBadgeHolders.get(userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress], []),
        ) for userRow in userRows]
        return ListResponse(items=items, totalCount=int(totalCountRow[0] if totalCountRow else 0))

    async def query_super_collection_users(self, superCollectionName: str, order: Optional[str], limit: int, offset: int) -> ListResponse[GallerySuperCollectionUserRow]:
        superCollectionAddresses = SUPER_COLLECTIONS.get(superCollectionName)
        if not superCollectionAddresses or len(superCollectionAddresses) == 0:
            emptyGallerySuperCollectionUserRow: List[GallerySuperCollectionUserRow] = []
            return ListResponse(items=emptyGallerySuperCollectionUserRow, totalCount=0)
        ownedCountColumn = sqlalchemyfunc.sum(UserRegistryOrderedOwnershipsMaterializedView.c.quantity).label('ownedTokenCount')
        uniqueOwnedCountColumn = sqlalchemyfunc.count(UserRegistryOrderedOwnershipsMaterializedView.c.tokenId).label('uniqueOwnedTokenCount')
        countQuery = (
            sqlalchemy.select(ownedCountColumn, uniqueOwnedCountColumn, UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress.in_(superCollectionAddresses))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 0)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.not_in(STAKING_ADDRESSES))
                .group_by(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        countResult = await self.retriever.database.execute(query=countQuery)
        countRows = list(countResult.mappings())
        registryOwnedTokenCount: Dict[str, Dict[str, int]] =  defaultdict(lambda: defaultdict(int))
        registryUniqueOwnedTokenCount: Dict[str, Dict[str, int]] =  defaultdict(lambda: defaultdict(int))
        for userRow in countRows:
            registryOwnedTokenCount[userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]][userRow[UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress]] = userRow['ownedTokenCount']
            registryUniqueOwnedTokenCount[userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]][userRow[UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress]]= userRow['uniqueOwnedTokenCount']
        ownedCountColumn = sqlalchemyfunc.sum(UserRegistryOrderedOwnershipsMaterializedView.c.quantity).label('ownedTokenCount')
        uniqueOwnedCountColumn = sqlalchemyfunc.count(UserRegistryOrderedOwnershipsMaterializedView.c.tokenId).label('uniqueOwnedTokenCount')
        minimumJoinDate = sqlalchemyfunc.min(UserRegistryFirstOwnershipsMaterializedView.c.joinDate).label('minimumJoinDate')
        usersQueryBase = (
            sqlalchemy.select(ownedCountColumn, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserProfilesTable, TwitterProfilesTable, minimumJoinDate)
                .join(UserProfilesTable, UserProfilesTable.c.address == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, isouter=True)
                .join(TwitterProfilesTable, TwitterProfilesTable.c.twitterId == UserProfilesTable.c.twitterId, isouter=True)
                .join(UserRegistryFirstOwnershipsMaterializedView, sqlalchemy.and_(UserRegistryFirstOwnershipsMaterializedView.c.ownerAddress == UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress, UserRegistryFirstOwnershipsMaterializedView.c.registryAddress == UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress), isouter=True)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress.in_(superCollectionAddresses))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.quantity > 0)
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.not_in(STAKING_ADDRESSES))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress != chain_util.BURN_ADDRESS)
                .group_by(UserProfilesTable.c.userProfileId, TwitterProfilesTable.c.twitterProfileId, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
        )
        usersQuery = usersQueryBase.limit(limit).offset(offset)
        if not order or order == 'TOKENCOUNT_DESC':
            usersQuery = usersQuery.order_by(ownedCountColumn.desc())
        elif order == 'TOKENCOUNT_ASC':
            usersQuery = usersQuery.order_by(ownedCountColumn.asc(), minimumJoinDate.desc())
        elif order == 'UNIQUETOKENCOUNT_DESC':
            usersQuery = usersQuery.order_by(uniqueOwnedCountColumn.desc())
        elif order == 'UNIQUETOKENCOUNT_ASC':
            usersQuery = usersQuery.order_by(uniqueOwnedCountColumn.asc(), minimumJoinDate.desc())
        elif order == 'FOLLOWERCOUNT_DESC':
            usersQuery = usersQuery.order_by(sqlalchemyfunc.coalesce(TwitterProfilesTable.c.followerCount, 0).desc(), ownedCountColumn.desc())
        elif order == 'FOLLOWERCOUNT_ASC':
            usersQuery = usersQuery.order_by(sqlalchemyfunc.coalesce(TwitterProfilesTable.c.followerCount, 0).asc(), ownedCountColumn.desc())
        # NOTE(krishan711): joindate ordering is inverse because its displayed as time ago so oldest is highest
        elif order == 'JOINDATE_DESC':
            usersQuery = usersQuery.order_by(minimumJoinDate.asc(), ownedCountColumn.desc())
        elif order == 'JOINDATE_ASC':
            usersQuery = usersQuery.order_by(minimumJoinDate.desc(), ownedCountColumn.desc())
        else:
            raise BadRequestException('Unknown order')
        usersResult = await self.retriever.database.execute(query=usersQuery)
        userRows = list(usersResult.mappings())
        ownerAddresses = {userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress] for userRow in userRows}
        userCountsQuery = (
            sqlalchemy.select(sqlalchemyfunc.count(sqlalchemy.distinct(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)))
            .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress.in_(superCollectionAddresses))
        )
        userCountsResult = await self.retriever.database.execute(query=userCountsQuery)
        totalCountRow = userCountsResult.first()
        chosenTokensQuery = (
            sqlalchemy.select(TokenMetadatasTable, UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress)
                .join(UserRegistryOrderedOwnershipsMaterializedView, sqlalchemy.and_(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress == TokenMetadatasTable.c.registryAddress, UserRegistryOrderedOwnershipsMaterializedView.c.tokenId == TokenMetadatasTable.c.tokenId))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress.in_(superCollectionAddresses))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress.in_(ownerAddresses))
                .where(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex <= 5)
                .order_by(UserRegistryOrderedOwnershipsMaterializedView.c.ownerTokenIndex.asc())
        )
        chosenTokensResult = await self.retriever.database.execute(query=chosenTokensQuery)
        chosenTokens: Dict[str, Dict[str, List[TokenMetadata]]] = defaultdict(lambda: defaultdict(list))
        for chosenTokenRow in chosenTokensResult.mappings():
            chosenTokens[chosenTokenRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]][chosenTokenRow[TokenMetadatasTable.c.registryAddress]].append(token_metadata_from_row(chosenTokenRow))
        galleryBadgeHoldersQuery = (
            sqlalchemy.select(GalleryBadgeHoldersView)
                .where(GalleryBadgeHoldersView.c.registryAddress.in_(superCollectionAddresses))
                .where(GalleryBadgeHoldersView.c.ownerAddress.in_(ownerAddresses))
        )
        galleryBadgeHoldersResult = await self.retriever.database.execute(query=galleryBadgeHoldersQuery)
        galleryBadgeHolders: Dict[str, List[GalleryBadgeHolder]] = defaultdict(list)
        for galleryBadgeHolderRow in galleryBadgeHoldersResult.mappings():
            galleryBadgeHolders[galleryBadgeHolderRow[GalleryBadgeHoldersView.c.ownerAddress]].append(gallery_badge_holder_from_row(galleryBadgeHolderRow))
        items = [GallerySuperCollectionUserRow(
            galleryUser=GalleryUser(
                address=userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress],
                registryAddress=superCollectionName,#userRow[UserRegistryOrderedOwnershipsMaterializedView.c.registryAddress],
                userProfile=user_profile_from_row(userRow) if userRow and userRow[UserProfilesTable.c.userProfileId] else None,
                twitterProfile=twitter_profile_from_row(userRow) if userRow and userRow[TwitterProfilesTable.c.twitterProfileId] else None,
                joinDate=userRow['minimumJoinDate'],
            ),
            ownedTokenCountMap=registryOwnedTokenCount[userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]],
            uniqueOwnedTokenCountMap=registryUniqueOwnedTokenCount[userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]],
            chosenOwnedTokensMap=chosenTokens[userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress]],
            galleryBadgeHolders=galleryBadgeHolders.get(userRow[UserRegistryOrderedOwnershipsMaterializedView.c.ownerAddress], []),
        ) for userRow in userRows]
        return ListResponse(items=items, totalCount=int(totalCountRow[0] if totalCountRow else 0))

    async def follow_gallery_user(self, registryAddress: str, userAddress: str, account: str, signatureMessage: str, signature: str) -> None:  # pylint: disable=unused-argument
        # TODO(krishan711): validate signature
        accountProfile = await self.retriever.get_user_profile_by_address(address=account)
        if not accountProfile.twitterId:
            raise BadRequestException('NO_TWITTER_ID')
        userProfile = await self.retriever.get_user_profile_by_address(address=userAddress)
        if not userProfile.twitterId:
            raise BadRequestException('NO_TWITTER_ID')
        await self.twitterManager.follow_user_from_user(userTwitterId=accountProfile.twitterId, targetTwitterId=userProfile.twitterId)

    async def get_gallery_user_owned_collections(self, registryAddress: str, userAddress: str) -> List[OwnedCollection]:
        collectionsQuery = (
            sqlalchemy.select(TokenOwnershipsView)
                .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenOwnershipsView.c.registryAddress)
                .where(TokenOwnershipsView.c.ownerAddress == userAddress)
                .where(TokenOwnershipsView.c.registryAddress != registryAddress)
                .where(TokenOwnershipsView.c.quantity > 0)
                .order_by(CollectionTotalActivitiesTable.c.totalValue.desc(), TokenOwnershipsView.c.latestTransferDate.asc())
        )
        collectionsResult = await self.retriever.database.execute(query=collectionsQuery)
        collectionTokenIds = [(row[TokenOwnershipsView.c.registryAddress], row[TokenOwnershipsView.c.tokenId]) for row in collectionsResult.mappings()]
        registryAddresses = list(dict.fromkeys([collectionTokenId[0] for collectionTokenId in collectionTokenIds]))
        collections = await self.retriever.list_collections(fieldFilters=[StringFieldFilter(fieldName=TokenCollectionsTable.c.address.key, containedIn=registryAddresses)])
        collectionMap = {collection.address: collection for collection in collections}
        collectionTokenMap: Dict[str, List[TokenMetadata]] = defaultdict(list)
        for chunkedCollectionTokenIds in list_util.generate_chunks(lst=list(collectionTokenIds), chunkSize=1000):
            tokensQuery = (
                TokenMetadatasTable.select()
                    .where(sqlalchemy.tuple_(TokenMetadatasTable.c.registryAddress, TokenMetadatasTable.c.tokenId).in_(chunkedCollectionTokenIds))
            )
            tokens = await self.retriever.query_token_metadatas(query=tokensQuery)
            for token in tokens:
                collectionTokenMap[token.registryAddress].append(token)
        return [
            OwnedCollection(
                collection=collectionMap[registryAddress],
                tokenMetadatas=collectionTokenMap[registryAddress],
            ) for registryAddress in registryAddresses
        ]

    async def list_gallery_collection_overlaps(self, registryAddress: str, otherRegistryAddress: Optional[str]) -> List[CollectionOverlap]:
        filters = [
            StringFieldFilter(fieldName=TokenCollectionOverlapsTable.c.registryAddress.key, eq=registryAddress),
        ]
        if otherRegistryAddress:
            filters.append(StringFieldFilter(fieldName=TokenCollectionOverlapsTable.c.otherRegistryAddress.key, eq=otherRegistryAddress))
        return await self.retriever.list_collection_overlaps(fieldFilters=filters, orders=[Order(fieldName=TokenCollectionOverlapsTable.c.otherRegistryTokenCount.key, direction=Direction.DESCENDING)])

    async def list_gallery_collection_overlap_summaries(self, registryAddress: str) -> List[CollectionOverlapSummary]:
        query = (
            sqlalchemy.select(
                TokenCollectionOverlapsTable.c.registryAddress,
                TokenCollectionOverlapsTable.c.otherRegistryAddress,
                TokenCollectionsTable,
                sqlalchemyfunc.count(TokenCollectionOverlapsTable.c.ownerAddress).label('ownerCount'),
                sqlalchemyfunc.sum(TokenCollectionOverlapsTable.c.registryTokenCount).label('registryTokenCount'),
                sqlalchemyfunc.sum(TokenCollectionOverlapsTable.c.otherRegistryTokenCount).label('otherRegistryTokenCount'),
            )
            .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenCollectionOverlapsTable.c.otherRegistryAddress)
            .join(TokenCollectionsTable, TokenCollectionsTable.c.address == TokenCollectionOverlapsTable.c.otherRegistryAddress)
            .where(TokenCollectionOverlapsTable.c.registryAddress == registryAddress)
            .order_by(CollectionTotalActivitiesTable.c.totalValue.desc())
            .group_by(TokenCollectionOverlapsTable.c.registryAddress, TokenCollectionOverlapsTable.c.otherRegistryAddress, TokenCollectionsTable.c, CollectionTotalActivitiesTable.c.totalValue)  # type: ignore[arg-type]
            .limit(100)
        )
        result = await self.retriever.database.execute(query=query)
        return [
            CollectionOverlapSummary(
                registryAddress=row[TokenCollectionOverlapsTable.c.registryAddress],
                otherCollection=collection_from_row(row),
                ownerCount=row['ownerCount'],
                registryTokenCount=row['registryTokenCount'],
                otherRegistryTokenCount=row['otherRegistryTokenCount'],
            ) for row in result.mappings()
        ]

    async def list_gallery_collection_overlap_owners(self, registryAddress: str) -> List[CollectionOverlapOwner]:
        query = (
            sqlalchemy.select(
                TokenCollectionOverlapsTable.c.registryAddress,
                TokenCollectionOverlapsTable.c.otherRegistryAddress,
                TokenCollectionOverlapsTable.c.ownerAddress,
                TokenCollectionsTable,
                sqlalchemyfunc.sum(TokenCollectionOverlapsTable.c.registryTokenCount).label('registryTokenCount'),
                sqlalchemyfunc.sum(TokenCollectionOverlapsTable.c.otherRegistryTokenCount).label('otherRegistryTokenCount'),
            )
            .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenCollectionOverlapsTable.c.otherRegistryAddress)
            .join(TokenCollectionsTable, TokenCollectionsTable.c.address == TokenCollectionOverlapsTable.c.otherRegistryAddress)
            .where(TokenCollectionOverlapsTable.c.registryAddress == registryAddress)
            .order_by(CollectionTotalActivitiesTable.c.totalValue.desc())
            .group_by(TokenCollectionOverlapsTable.c.registryAddress, TokenCollectionOverlapsTable.c.otherRegistryAddress, TokenCollectionsTable.c, CollectionTotalActivitiesTable.c.totalValue, TokenCollectionOverlapsTable.c.ownerAddress)  # type: ignore[arg-type]
        )
        result = await self.retriever.database.execute(query=query)
        return [
            CollectionOverlapOwner(
                registryAddress=row[TokenCollectionOverlapsTable.c.registryAddress],
                otherCollection=collection_from_row(row),
                ownerAddress=row[TokenCollectionOverlapsTable.c.ownerAddress],
                registryTokenCount=row['registryTokenCount'],
                otherRegistryTokenCount=row['otherRegistryTokenCount'],
            ) for row in result.mappings()
        ]

    async def assign_badge(self, registryAddress: str, ownerAddress: str, badgeKey: str, assignerAddress: str, achievedDate: datetime.datetime, signature: str) -> None:
        await self.badgeManager.assign_badge(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey=badgeKey, assignerAddress=assignerAddress, achievedDate=achievedDate, signature=signature)

    async def list_gallery_super_collection_overlaps(self, superCollectionName: str, otherRegistryAddress: str) -> List[SuperCollectionOverlap]:
        superCollectionAddresses = SUPER_COLLECTIONS.get(superCollectionName)
        filters = [
            StringFieldFilter(fieldName=TokenCollectionOverlapsTable.c.registryAddress.key, containedIn=superCollectionAddresses),
            StringFieldFilter(fieldName=TokenCollectionOverlapsTable.c.otherRegistryAddress.key, eq=otherRegistryAddress)
        ]
        collectionOverlaps = await self.retriever.list_collection_overlaps(fieldFilters=filters, orders=[Order(fieldName=TokenCollectionOverlapsTable.c.otherRegistryTokenCount.key, direction=Direction.DESCENDING)])
        superCollectionOverlapsTokenCountDict: Dict[str, Dict[str,int]] = defaultdict(lambda: defaultdict(int))
        for collectionOverlap in collectionOverlaps:
            if superCollectionAddresses and collectionOverlap.registryAddress in superCollectionAddresses:
                superCollectionOverlapsTokenCountDict[collectionOverlap.ownerAddress][collectionOverlap.registryAddress] = collectionOverlap.registryTokenCount
        overlaps = []
        for collectionOverlap in collectionOverlaps:
            overlaps += [
                SuperCollectionOverlap(
                    ownerAddress=collectionOverlap.ownerAddress,
                    otherRegistryAddress=otherRegistryAddress,
                    otherRegistryTokenCount=collectionOverlap.otherRegistryTokenCount,
                    registryTokenCountMap=superCollectionOverlapsTokenCountDict[collectionOverlap.ownerAddress]
                )
            ]
        return overlaps

    async def list_gallery_super_collection_overlap_summaries(self, superCollectionName: str) -> List[CollectionOverlapSummary]:
        superCollectionAddresses = SUPER_COLLECTIONS.get(superCollectionName)
        if not superCollectionAddresses or len(superCollectionAddresses) == 0:
            return []
        query = (
            sqlalchemy.select(
                TokenCollectionOverlapsTable.c.otherRegistryAddress,
                TokenCollectionsTable,
                sqlalchemyfunc.count(TokenCollectionOverlapsTable.c.ownerAddress).label('ownerCount'),
                sqlalchemyfunc.sum(TokenCollectionOverlapsTable.c.registryTokenCount).label('registryTokenCount'),
                sqlalchemyfunc.sum(TokenCollectionOverlapsTable.c.otherRegistryTokenCount).label('otherRegistryTokenCount'),
            )
            .join(CollectionTotalActivitiesTable, CollectionTotalActivitiesTable.c.address == TokenCollectionOverlapsTable.c.otherRegistryAddress)
            .join(TokenCollectionsTable, TokenCollectionsTable.c.address == TokenCollectionOverlapsTable.c.otherRegistryAddress)
            .where(TokenCollectionOverlapsTable.c.registryAddress.in_(superCollectionAddresses))
            .where(TokenCollectionOverlapsTable.c.otherRegistryAddress.not_in(superCollectionAddresses))
            .order_by(CollectionTotalActivitiesTable.c.totalValue.desc())
            .group_by(TokenCollectionOverlapsTable.c.otherRegistryAddress, TokenCollectionsTable.c, CollectionTotalActivitiesTable.c.totalValue)  # type: ignore[arg-type]
            .limit(100)
        )
        result = await self.retriever.database.execute(query=query)
        return [
            CollectionOverlapSummary(
                registryAddress=superCollectionName,
                otherCollection=collection_from_row(row),
                ownerCount=row['ownerCount'],
                registryTokenCount=row['registryTokenCount'],
                otherRegistryTokenCount=row['otherRegistryTokenCount'],
            ) for row in result.mappings()
        ]

    async def list_entries_in_super_collection(self, superCollectionName: str) -> List[SuperCollectionEntry]:
        superCollectionAddresses = SUPER_COLLECTIONS.get(superCollectionName, [])
        superCollectionAttributes = []
        for collectionAddress in superCollectionAddresses:
            superCollectionAttributes.append(
                SuperCollectionEntry(
                    collectionAddress=collectionAddress,
                    collectionAttributes=(await self.get_collection_attributes(registryAddress=collectionAddress))
                )
            )
        return superCollectionAttributes
