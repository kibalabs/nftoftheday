import datetime
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import sqlalchemy
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import StringFieldFilter

from notd.model import RetrievedTokenStaking
from notd.store.retriever import Retriever
from notd.model import STAKING_CONTRACTS
from notd.store.schema import BlocksTable
from notd.store.schema import TokenStakingsTable
from notd.store.schema import TokenTransfersTable


class TokenStakingProcessor:

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    async def get_staked_token(self, registryAddress: str, tokenId: str) -> Optional[RetrievedTokenStaking]:
        for stakingAddress in STAKING_CONTRACTS:
            latestTokenTransfers = await self.retriever.list_token_transfers(fieldFilters=[
                    StringFieldFilter(fieldName=TokenStakingsTable.c.registryAddress.key, eq=registryAddress),
                    StringFieldFilter(fieldName=TokenStakingsTable.c.tokenId.key, eq=tokenId)
                ],
            orders=[Order(fieldName=BlocksTable.c.blockDate.key, direction=Direction.DESCENDING)],
            limit=1)
            latestTokenTransfer = latestTokenTransfers[0]
            if latestTokenTransfer.fromAddress == stakingAddress:
                return None
            retrievedTokenStaking = RetrievedTokenStaking(
                registryAddress=registryAddress,
                tokenId=tokenId,
                stakingAddress=stakingAddress,
                ownerAddress=latestTokenTransfer.toAddress,
                stakedDate=latestTokenTransfer.blockDate,
                transactionHash=latestTokenTransfer.transactionHash
            )
        return retrievedTokenStaking

    async def get_all_staked_creepz_tokens(self, registryAddress: str) -> List[RetrievedTokenStaking]:
        retrievedStakedTokens = []
        for stakingAddresses in STAKING_CONTRACTS:
            stakedQuery = (
                sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.fromAddress, TokenTransfersTable.c.transactionHash, BlocksTable.c.blockDate)
                .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                .where(TokenTransfersTable.c.registryAddress == registryAddress)
                .where(TokenTransfersTable.c.toAddress == stakingAddresses)
                .order_by(TokenTransfersTable.c.blockNumber.asc())
            )
            stakedTokensResult = await self.retriever.database.execute(query=stakedQuery)
            stakedTokens = list(stakedTokensResult)
            unStakedQuery = (
                sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.toAddress, TokenTransfersTable.c.transactionHash, BlocksTable.c.blockDate)
                .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
                .where(TokenTransfersTable.c.registryAddress == registryAddress)
                .where(TokenTransfersTable.c.fromAddress == stakingAddresses)
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
            retrievedStakedTokens += [RetrievedTokenStaking(registryAddress=registryAddress, tokenId=tokenId, stakingAddress=stakingAddresses, ownerAddress=ownerAddress, stakedDate=stakedDate, transactionHash=transactionHash) for tokenId, (ownerAddress, transactionHash, stakedDate) in currentlyStakedTokens.items()]
        return retrievedStakedTokens
