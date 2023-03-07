import json
from typing import List
from typing import Optional

from core.exceptions import BadRequestException
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter
from core.util.chain_util import BURN_ADDRESS
from core.web3.eth_client import EthClientInterface

from notd.model import COLLECTION_CREEPZ_ADDRESS
from notd.model import COLLECTION_CREEPZ_ARMOURIES_ADDRESS
from notd.model import COLLECTION_CREEPZ_MEGA_SHAPESHIFTER_ADDRESS
from notd.model import CREEPZ_STAKING_ADDRESS
from notd.model import STAKING_ADDRESSES
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
        self.creepzStakingGetStakerTokenFunctionAbi = [internalAbi for internalAbi in self.creepzStakingContractAbi if internalAbi.get('name') == 'getStakerTokens'][0]

    # TODO(krishan711): this function is def wrong if there are multiple staking addresses
    async def retrieve_updated_token_staking(self, registryAddress: str, tokenId: str) -> Optional[RetrievedTokenStaking]:
        for stakingAddress in STAKING_ADDRESSES:
            try:
                tokenOwnerResponse = (await self.ethClient.call_function(toAddress=stakingAddress, contractAbi=self.creepzStakingContractAbi, functionAbi=self.creepzStakingOwnerOfFunctionAbi, arguments={'tokenId': int(tokenId), 'contractAddress': registryAddress}))[0]
            except BadRequestException:
                raise InvalidTokenStakingContract()
            ownerAddress = tokenOwnerResponse
            if ownerAddress == BURN_ADDRESS:
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

    async def retrieve_owner_token_stakings(self, ownerAddress: str, stakingAddress: str) -> List[RetrievedTokenStaking]:
        retrievedTokenStakings: List[RetrievedTokenStaking] = []
        if stakingAddress == CREEPZ_STAKING_ADDRESS:
            stakedTokensResponse = (await self.ethClient.call_function(toAddress=stakingAddress, contractAbi=self.creepzStakingContractAbi, functionAbi=self.creepzStakingGetStakerTokenFunctionAbi, arguments={'staker': ownerAddress}))
            stakedCreepzToken = [(COLLECTION_CREEPZ_ADDRESS, tokenId) for tokenId in stakedTokensResponse[0]]
            stakedArmouriesToken = [(COLLECTION_CREEPZ_ARMOURIES_ADDRESS, tokenId) for tokenId in stakedTokensResponse[1]]
            stakedBlackBoxToken = [(COLLECTION_CREEPZ_MEGA_SHAPESHIFTER_ADDRESS, tokenId) for tokenId in stakedTokensResponse[2]]
            stakedTokens = stakedCreepzToken + stakedArmouriesToken + stakedBlackBoxToken
            for registryAddress, tokenId in stakedTokens:
                latestTokenTransfers = await self.retriever.list_token_transfers(
                    fieldFilters=[
                        StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=registryAddress),
                        StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=str(tokenId)),
                        StringFieldFilter(fieldName=TokenTransfersTable.c.toAddress.key, eq=stakingAddress),
                    ],
                    orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.DESCENDING)],
                    limit=1,
                )
                if len(latestTokenTransfers) > 0:
                    latestTokenTransfer = latestTokenTransfers[0]
                    retrievedTokenStakings += [RetrievedTokenStaking(
                            registryAddress=registryAddress,
                            tokenId=str(tokenId),
                            stakingAddress=stakingAddress,
                            ownerAddress=ownerAddress,
                            stakedDate=latestTokenTransfer.blockDate,
                            transactionHash=latestTokenTransfer.transactionHash
                        )]
        return retrievedTokenStakings
