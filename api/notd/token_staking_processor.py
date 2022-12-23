import datetime
from typing import List
from typing import Tuple
from typing import Dict
from collections import defaultdict
import sqlalchemy

from notd.model import RetrievedTokenStaking
from notd.model import CREEPZ_STAKING_CONTRACT
from notd.store.retriever import Retriever
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable

class TokenStakingProcessor:

    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    async def calculate_staked_creepz_tokens(self, registryAddress: str) -> List[RetrievedTokenStaking]:
        stakedQuery = (
        sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.toAddress, BlocksTable.c.blockDate)
        .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        .where(TokenTransfersTable.c.registryAddress == registryAddress)
        .where(TokenTransfersTable.c.toAddress == CREEPZ_STAKING_CONTRACT)
        .order_by(BlocksTable.c.blockDate.asc())
        )
        stakedTokensResult = await self.retriever.database.execute(query=stakedQuery)
        stakedTokens = list(stakedTokensResult)
        unStakedQuery = (
            sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.toAddress, BlocksTable.c.blockDate)
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .where(TokenTransfersTable.c.fromAddress == CREEPZ_STAKING_CONTRACT)
            .order_by(BlocksTable.c.blockDate.asc())
            )
        unStakedTokensResult = await self.retriever.database.execute(query=unStakedQuery)
        unStakedTokens = list(unStakedTokensResult)
        # currentlyStakedTokens: Dict[str, Tuple[str, datetime.datetime]] = {}
        currentlyStakedTokens = defaultdict()
        for tokenId, ownerAddress, blockDate in stakedTokens:
            if tokenId == '9135':
                print('present')
            currentlyStakedTokens[tokenId] = (ownerAddress, blockDate)

        for tokenId, ownerAddress, blockDate in unStakedTokens:
            if tokenId == '9135':
                print('absent')
            if currentlyStakedTokens[tokenId][1] < blockDate:
                del currentlyStakedTokens[tokenId]

        retrievedStakedTokens = [RetrievedTokenStaking(registryAddress=registryAddress, tokenId=tokenId, stakingAddress=CREEPZ_STAKING_CONTRACT, ownerAddress=ownerAddress, stakingDate=stakingDate) for tokenId, (ownerAddress, stakingDate) in currentlyStakedTokens.items()]
        return retrievedStakedTokens
