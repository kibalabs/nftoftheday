import datetime
import json
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import sqlalchemy
from core.exceptions import BadRequestException
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util.chain_util import BURN_ADDRESS
from core.web3.eth_client import EthClientInterface

from notd.model import COLLECTION_CREEPZ_ADDRESS
from notd.model import STAKING_ADDRESSES
from notd.model import RetrievedTokenStaking
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenStakingsTable
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

    async def get_updated_token_staking(self, registryAddress: str, tokenId: str) -> Optional[RetrievedTokenStaking]:
        for stakingAddress in STAKING_ADDRESSES:
            try:
                tokenOwnerResponse = (await self.ethClient.call_function(toAddress=stakingAddress, contractAbi=self.creepzStakingContractAbi, functionAbi=self.creepzStakingOwnerOfFunctionAbi, arguments={'tokenId': int(tokenId), 'contractAddress': registryAddress}))
            except BadRequestException:
                raise InvalidTokenStakingContract()
            ownerAddress = tokenOwnerResponse[0]
            if ownerAddress == BURN_ADDRESS:
                return None
            latestTokenTransfers = await self.retriever.list_token_transfers(
                    fieldFilters=[
                        StringFieldFilter(fieldName=TokenStakingsTable.c.registryAddress.key, eq=registryAddress),
                        StringFieldFilter(fieldName=TokenStakingsTable.c.tokenId.key, eq=tokenId),
                        StringFieldFilter(fieldName=TokenStakingsTable.c.toAddress.key, eq=stakingAddress),
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

    async def get_all_staked_tokens(self, registryAddress: str) -> List[RetrievedTokenStaking]:
        retrievedStakedTokens: List[RetrievedTokenStaking] = []
        if registryAddress != COLLECTION_CREEPZ_ADDRESS:
            return retrievedStakedTokens
        for stakingAddress in STAKING_ADDRESSES:
            stakedQuery = (
                sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.fromAddress, TokenTransfersTable.c.transactionHash, BlocksTable.c.blockDate)
                .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                .where(TokenTransfersTable.c.registryAddress == registryAddress)
                .where(TokenTransfersTable.c.toAddress == stakingAddress)
                .order_by(TokenTransfersTable.c.blockNumber.asc())
            )
            stakedTokensResult = await self.retriever.database.execute(query=stakedQuery)
            stakedTokens = list(stakedTokensResult)
            unStakedQuery = (
                sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.toAddress, TokenTransfersTable.c.transactionHash, BlocksTable.c.blockDate)
                .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                .where(TokenTransfersTable.c.registryAddress == registryAddress)
                .where(TokenTransfersTable.c.fromAddress == stakingAddress)
                .order_by(TokenTransfersTable.c.blockNumber.asc())
                )
            unStakedTokensResult = await self.retriever.database.execute(query=unStakedQuery)
            unStakedTokens = list(unStakedTokensResult)
            currentlyStakedTokens: Dict[str, Tuple[str, str, datetime.datetime]] = {}
            for tokenId, ownerAddress, transactionHash, blockDate in stakedTokens:
                currentlyStakedTokens[tokenId] = (ownerAddress,transactionHash, blockDate)
            for tokenId, ownerAddress, transactionHash, blockDate in unStakedTokens:
                if currentlyStakedTokens[tokenId][2] < blockDate:
                    del currentlyStakedTokens[tokenId]
            retrievedStakedTokens += [RetrievedTokenStaking(registryAddress=registryAddress, tokenId=tokenId, stakingAddress=stakingAddress, ownerAddress=ownerAddress, stakedDate=stakedDate, transactionHash=transactionHash) for tokenId, (ownerAddress, transactionHash, stakedDate) in currentlyStakedTokens.items()]
        return retrievedStakedTokens
