import contextlib
import datetime
import json
import urllib.parse as urlparse
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

import sqlalchemy
from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.util import chain_util
from core.util import date_util
from core.web3.eth_client import EthClientInterface
from eth_account.messages import defunct_hash_message
from web3 import Web3

from notd.api.endpoints_v1 import InQueryParam
from notd.model import COLLECTION_SPRITE_CLUB_ADDRESS
from notd.model import Airdrop
from notd.model import CollectionAttribute
from notd.model import GalleryToken
from notd.model import GalleryUser
from notd.model import GalleryUserRow
from notd.model import ListResponse
from notd.model import Signature
from notd.model import Token
from notd.model import TokenCustomization
from notd.model import TokenMetadata
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import LatestTokenListingsTable
from notd.store.schema import TokenAttributesTable
from notd.store.schema import TokenCustomizationsTable
from notd.store.schema import TokenMetadatasTable
from notd.store.schema import TokenOwnershipsTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import TwitterProfilesTable
from notd.store.schema import UserProfilesTable
from notd.store.schema_conversions import token_customization_from_row
from notd.store.schema_conversions import token_listing_from_row
from notd.store.schema_conversions import token_metadata_from_row
from notd.store.schema_conversions import twitter_profile_from_row
from notd.store.schema_conversions import user_profile_from_row

from .twitter_manager import TwitterManager

SPRITE_CLUB_REGISTRY_ADDRESS = '0x2744fE5e7776BCA0AF1CDEAF3bA3d1F5cae515d3'
SPRITE_CLUB_STORMDROP_REGISTRY_ADDRESS = '0x27C86e1c64622643049d3D7966580Cb832dCd1EF'



class GalleryManager:

    def __init__(self, ethClient: EthClientInterface, retriever: Retriever, saver: Saver, twitterManager: TwitterManager) -> None:
        self.ethClient = ethClient
        self.retriever = retriever
        self.saver = saver
        self.twitterManager = twitterManager
        with open('./contracts/SpriteClub.json', 'r') as contractJsonFile:
            self.spriteClubContract = json.load(contractJsonFile)
        with open('./contracts/SpriteClubStormdrop.json', 'r') as contractJsonFile:
            self.spriteClubStormdropContract = json.load(contractJsonFile)
        self.spriteClubStormdropClaimedFunctionAbi = [internalAbi for internalAbi in self.spriteClubStormdropContract['abi'] if internalAbi.get('name') == 'claimedSpriteItemIdMap'][0]
        with open('./contracts/SpriteClubStormdropIdMap.json', 'r') as contractJsonFile:
            self.spriteClubStormdropIdMap = json.load(contractJsonFile)
        self.web3 = Web3()

    async def twitter_login(self, account: str, signatureJson: str, initialUrl: str) -> None:
        signature = Signature.from_dict(signatureDict=json.loads(urlparse.unquote(signatureJson)))
        await self.twitterManager.login(account=account, signature=signature, initialUrl=initialUrl)

    async def twitter_login_callback(self, state: str, code: Optional[str], error: Optional[str]) -> None:
        await self.twitterManager.login_callback(state=state, code=code, error=error)

    async def get_gallery_token(self, registryAddress: str, tokenId: str) -> GalleryToken:
        query = (
            sqlalchemy.select(TokenMetadatasTable, TokenCustomizationsTable, LatestTokenListingsTable)
                .join(TokenCustomizationsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenCustomizationsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenCustomizationsTable.c.tokenId), isouter=True)
                .join(TokenOwnershipsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenOwnershipsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenOwnershipsTable.c.tokenId))
                .join(LatestTokenListingsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == LatestTokenListingsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == LatestTokenListingsTable.c.tokenId, LatestTokenListingsTable.c.offererAddress == TokenOwnershipsTable.c.ownerAddress, LatestTokenListingsTable.c.endDate >= datetime.datetime.now()), isouter=True)
                .where(TokenMetadatasTable.c.registryAddress == registryAddress)
                .where(TokenMetadatasTable.c.tokenId == tokenId)
        )
        result = await self.retriever.database.execute(query=query)
        row = result.first()
        if not row:
            raise NotFoundException(message=f'GalleryToken with registry:{registryAddress} tokenId:{tokenId} not found')
        galleryToken = GalleryToken(
            tokenMetadata=token_metadata_from_row(row),
            tokenCustomization=token_customization_from_row(row) if row[TokenCustomizationsTable.c.tokenCustomizationId] else None,
            tokenListing=token_listing_from_row(row) if row[LatestTokenListingsTable.c.latestTokenListingId] else None,
        )
        return galleryToken

    async def list_collection_token_airdrops(self, registryAddress: str, tokenId: str) -> List[Airdrop]:
        registryAddress = chain_util.normalize_address(registryAddress)
        tokenKey = Token(registryAddress=registryAddress, tokenId=tokenId)
        if registryAddress == SPRITE_CLUB_REGISTRY_ADDRESS:
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
            TokenAttributesTable.select()
                .distinct()
                .with_only_columns([TokenAttributesTable.c.name, TokenAttributesTable.c.value])
                .where(TokenAttributesTable.c.registryAddress == registryAddress)
                .where(TokenAttributesTable.c.value.isnot(None))
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

    async def query_collection_tokens(self, registryAddress: str, limit: int, offset: int, ownerAddress: Optional[str] = None, minPrice: Optional[int] = None, maxPrice: Optional[int] = None, isListed: Optional[bool] = None, tokenIdIn: Optional[List[str]] = None, attributeFilters: Optional[List[InQueryParam]] = None) -> Sequence[GalleryToken]:
        registryAddress = chain_util.normalize_address(value=registryAddress)
        # TODO(krishan711): this shouldn't join on single ownerships for erc1155
        query = (
            sqlalchemy.select(TokenMetadatasTable, TokenCustomizationsTable, LatestTokenListingsTable)
                .join(TokenCustomizationsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenCustomizationsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenCustomizationsTable.c.tokenId), isouter=True)
                .join(TokenOwnershipsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == TokenOwnershipsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == TokenOwnershipsTable.c.tokenId))
                .join(LatestTokenListingsTable, sqlalchemy.and_(TokenMetadatasTable.c.registryAddress == LatestTokenListingsTable.c.registryAddress, TokenMetadatasTable.c.tokenId == LatestTokenListingsTable.c.tokenId, LatestTokenListingsTable.c.offererAddress == TokenOwnershipsTable.c.ownerAddress, LatestTokenListingsTable.c.endDate >= datetime.datetime.now()), isouter=True)
                .where(TokenMetadatasTable.c.registryAddress == registryAddress)
                .order_by(sqlalchemy.cast(TokenMetadatasTable.c.tokenId, sqlalchemy.Integer).asc())
                .limit(limit)
                .offset(offset)
        )
        usesListings = isListed or minPrice or maxPrice
        if usesListings:
            query = query.where(LatestTokenListingsTable.c.latestTokenListingId.is_not(None))
        if minPrice:
            query = query.where(LatestTokenListingsTable.c.value >= sqlalchemy.func.cast(minPrice, sqlalchemy.Numeric(precision=256, scale=0)))
        if maxPrice:
            query = query.where(LatestTokenListingsTable.c.value <= sqlalchemy.func.cast(maxPrice, sqlalchemy.Numeric(precision=256, scale=0)))
        if ownerAddress:
            query = query.where(TokenOwnershipsTable.c.ownerAddress == ownerAddress)
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
        for row in result:
            galleryTokens.append(GalleryToken(tokenMetadata=token_metadata_from_row(row), tokenCustomization=token_customization_from_row(row) if row[TokenCustomizationsTable.c.tokenCustomizationId] else None, tokenListing=token_listing_from_row(row) if row[LatestTokenListingsTable.c.latestTokenListingId] else None))
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
        signer = self.web3.eth.account.recoverHash(message_hash=messageHash, signature=signature)
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
        signer = self.web3.eth.account.recoverHash(message_hash=messageHash, signature=signature)
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
        userQuery = (
            sqlalchemy.select(sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).label('ownedTokenCount'), UserProfilesTable, TwitterProfilesTable)
                .join(UserProfilesTable, UserProfilesTable.c.address == TokenOwnershipsTable.c.ownerAddress, isouter=True)
                .join(TwitterProfilesTable, TwitterProfilesTable.c.twitterId == UserProfilesTable.c.twitterId, isouter=True)
                .where(TokenOwnershipsTable.c.registryAddress == registryAddress)
                .where(TokenOwnershipsTable.c.ownerAddress == userAddress)
                .group_by(UserProfilesTable.c.userProfileId, TwitterProfilesTable.c.twitterProfileId)
        )
        userResult = await self.retriever.database.execute(query=userQuery)
        userRow = userResult.first()
        joinDateQuery = (
            sqlalchemy.select(sqlalchemy.func.min(BlocksTable.c.blockDate).label("joinDate"))
            .join(TokenTransfersTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .where(TokenTransfersTable.c.toAddress == userAddress)
        )
        joinDateResult = await self.retriever.database.execute(query=joinDateQuery)
        joinDateRow = joinDateResult.first()
        galleryUser = GalleryUser(
            address=userAddress,
            registryAddress=registryAddress,
            userProfile=user_profile_from_row(userRow) if userRow and userRow[UserProfilesTable.c.userProfileId] else None,
            twitterProfile=twitter_profile_from_row(userRow) if userRow and userRow[TwitterProfilesTable.c.twitterProfileId] else None,
            ownedTokenCount=userRow['ownedTokenCount'] if userRow else 0,
            joinDate=joinDateRow['joinDate'] if joinDateRow else None,
        )
        return galleryUser

    async def query_collection_users(self, registryAddress, order: Optional[str], limit: int, offset: int) -> ListResponse[GalleryUserRow]:
        joinDateQuery = (
            sqlalchemy.select(TokenTransfersTable.c.toAddress.label("userAddress"), sqlalchemy.func.min(BlocksTable.c.blockDate).label("joinDate"))
            .join(TokenTransfersTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .group_by(TokenTransfersTable.c.toAddress)
        ).subquery()
        usersQueryBase = (
            sqlalchemy.select(sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).label('ownedTokenCount'), TokenOwnershipsTable.c.ownerAddress, UserProfilesTable, TwitterProfilesTable, joinDateQuery.c.joinDate)
                .join(UserProfilesTable, UserProfilesTable.c.address == TokenOwnershipsTable.c.ownerAddress, isouter=True)
                .join(TwitterProfilesTable, TwitterProfilesTable.c.twitterId == UserProfilesTable.c.twitterId, isouter=True)
                .join(joinDateQuery, joinDateQuery.c.userAddress == TokenOwnershipsTable.c.ownerAddress, isouter=True)
                .where(TokenOwnershipsTable.c.registryAddress == registryAddress)
                .group_by(UserProfilesTable.c.userProfileId, TwitterProfilesTable.c.twitterProfileId, TokenOwnershipsTable.c.ownerAddress, joinDateQuery.c.joinDate)
        )
        usersQuery = usersQueryBase.limit(limit).offset(offset)
        if not order or order == 'TOKENCOUNT_DESC':
            usersQuery = usersQuery.order_by(sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).desc())
        elif order == 'TOKENCOUNT_ASC':
            usersQuery = usersQuery.order_by(sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).asc(), joinDateQuery.c.joinDate.desc())
        elif order == 'FOLLOWERCOUNT_DESC':
            usersQuery = usersQuery.order_by(TwitterProfilesTable.c.followerCount.desc(), sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).desc())
        elif order == 'FOLLOWERCOUNT_ASC':
            usersQuery = usersQuery.order_by(TwitterProfilesTable.c.followerCount.asc(), sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).desc())
        # NOTE(krishan711): joindate odering is inverse because its displayed as time ago so oldest is highest
        elif order == 'JOINDATE_DESC':
            usersQuery = usersQuery.order_by(joinDateQuery.c.joinDate.asc(), sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).desc())
        elif order == 'JOINDATE_ASC':
            usersQuery = usersQuery.order_by(joinDateQuery.c.joinDate.desc(), sqlalchemy.func.count(TokenOwnershipsTable.c.tokenId).desc())
        else:
            raise BadRequestException('Unknown order')
        usersResult = await self.retriever.database.execute(query=usersQuery)
        userRows = list(usersResult)
        userCountsResult = await self.retriever.database.execute(query=sqlalchemy.select(sqlalchemy.func.count()).select_from(usersQueryBase.subquery()))
        (totalCount, ) = userCountsResult.first()
        ownerAddresses = [userRow[TokenOwnershipsTable.c.ownerAddress] for userRow in userRows]
        orderedTokensQuery = (
            sqlalchemy.select(TokenMetadatasTable.c.tokenMetadataId, TokenOwnershipsTable.c.ownerAddress, sqlalchemy.func.row_number().over(partition_by=TokenOwnershipsTable.c.ownerAddress, order_by=TokenOwnershipsTable.c.transferDate).label('tokenIndex'))
                .join(TokenOwnershipsTable, sqlalchemy.and_(TokenOwnershipsTable.c.tokenId == TokenMetadatasTable.c.tokenId, TokenOwnershipsTable.c.registryAddress == TokenMetadatasTable.c.registryAddress))
                .where(TokenMetadatasTable.c.registryAddress == registryAddress)
        ).subquery()
        chosenTokensQuery = (
            sqlalchemy.select(TokenMetadatasTable, orderedTokensQuery.c.ownerAddress)
                .join(orderedTokensQuery, orderedTokensQuery.c.tokenMetadataId == TokenMetadatasTable.c.tokenMetadataId)
                .where(orderedTokensQuery.c.tokenIndex <= 5)
                .where(orderedTokensQuery.c.ownerAddress.in_(ownerAddresses))
        )
        chosenTokensResult = await self.retriever.database.execute(query=chosenTokensQuery)
        chosenTokenRows = list(chosenTokensResult)
        chosenTokens: Dict[str, List[TokenMetadata]] = defaultdict(list)
        for chosenTokenRow in chosenTokenRows:
            chosenTokens[chosenTokenRow['ownerAddress']].append(token_metadata_from_row(chosenTokenRow))
        items = [GalleryUserRow(
            galleryUser=GalleryUser(
                address=userRow[TokenOwnershipsTable.c.ownerAddress],
                registryAddress=registryAddress,
                userProfile=user_profile_from_row(userRow) if userRow and userRow[UserProfilesTable.c.userProfileId] else None,
                twitterProfile=twitter_profile_from_row(userRow) if userRow and userRow[TwitterProfilesTable.c.twitterProfileId] else None,
                ownedTokenCount=userRow['ownedTokenCount'],
                joinDate=userRow['joinDate'],
            ),
            chosenOwnedTokens=chosenTokens[userRow[TokenOwnershipsTable.c.ownerAddress]],
        ) for userRow in userRows]
        return ListResponse(items=items, totalCount=totalCount)
