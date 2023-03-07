import datetime
import json
from typing import Dict
from typing import Set
from typing import Optional
from typing import Tuple

import sqlalchemy
from core.exceptions import BadRequestException
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.web3.eth_client import EthClientInterface

from notd.model import STAKING_ADDRESSES
from notd.model import CREEPZ_STAKING_ADDRESS
from notd.model import RetrievedTokenStaking
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable


class InvalidTokenStakingContract(BadRequestException):
    pass

class TokenStakingProcessor:

    def __init__(self, ethClient: EthClientInterface, retriever: Retriever) -> None:
        self.retriever = retriever
        self.ethClient = ethClient
        with open('./contracts/CreepzStaking.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.creepzStakingContractAbi = contractJson['abi']
        self.creepzStakingOwnerOfFunctionAbi = [internalAbi for internalAbi in self.creepzStakingContractAbi if internalAbi.get('name') == 'ownerOf'][0]

    async def retrieve_token_staking(self, registryAddress: str, tokenId: str) -> Optional[RetrievedTokenStaking]:
        tokenOwnership = await self.retriever.get_token_ownership_by_registry_address_token_id(registryAddress=registryAddress, tokenId=tokenId)
        if tokenOwnership.ownerAddress == CREEPZ_STAKING_ADDRESS:
            stakingAddress = CREEPZ_STAKING_ADDRESS
            ownerAddress = (await self.ethClient.call_function(toAddress=CREEPZ_STAKING_ADDRESS, contractAbi=self.creepzStakingContractAbi, functionAbi=self.creepzStakingOwnerOfFunctionAbi, arguments={'tokenId': int(tokenId), 'contractAddress': registryAddress}))[0]
        else:
            return None
        latestTokenTransfers = await self.retriever.list_token_transfers(
                fieldFilters=[
                    StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=tokenId),
                    StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=stakingAddress),
                ],
                orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.DESCENDING)],
                limit=1,
            )
        latestTokenTransfer = latestTokenTransfers[0]
        retrievedTokenStaking = RetrievedTokenStaking(
            registryAddress=registryAddress,
            tokenId=tokenId,
            stakingAddress=stakingAddress,
            ownerAddress=ownerAddress,
            stakedDate=latestTokenTransfer.blockDate,
            transactionHash=latestTokenTransfer.transactionHash
        )
        return retrievedTokenStaking

    async def retrieve_collection_token_staking_ids(self, registryAddress: str) -> Set[Tuple[str, str]]:
        for stakingAddress in STAKING_ADDRESSES:
            stakedQuery = (
                sqlalchemy.select(TokenTransfersTable.c.tokenId, BlocksTable.c.blockDate)
                .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                .where(TokenTransfersTable.c.registryAddress == registryAddress)
                .where(TokenTransfersTable.c.toAddress == stakingAddress)
                .order_by(TokenTransfersTable.c.blockNumber.asc())
            )
            stakedTokensResult = await self.retriever.database.execute(query=stakedQuery)
            stakedTokens = list(stakedTokensResult)
            unStakedQuery = (
                sqlalchemy.select(TokenTransfersTable.c.tokenId, BlocksTable.c.blockDate)
                .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                .where(TokenTransfersTable.c.registryAddress == registryAddress)
                .where(TokenTransfersTable.c.fromAddress == stakingAddress)
                .order_by(TokenTransfersTable.c.blockNumber.asc())
            )
            unStakedTokensResult = await self.retriever.database.execute(query=unStakedQuery)
            unStakedTokens = list(unStakedTokensResult)
            currentlyStakedTokens: Dict[str, Tuple[str, datetime.datetime]] = {}
            for tokenId, blockDate in stakedTokens:
                currentlyStakedTokens[tokenId] = blockDate
            for tokenId, blockDate in unStakedTokens:
                if currentlyStakedTokens[tokenId] < blockDate:
                    del currentlyStakedTokens[tokenId]
            stakingCollectionTokenIds = {(registryAddress, tokenId) for tokenId in currentlyStakedTokens.keys()}
        return stakingCollectionTokenIds
