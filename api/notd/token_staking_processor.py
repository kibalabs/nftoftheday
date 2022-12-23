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
        sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.fromAddress, TokenTransfersTable.c.transactionHash, BlocksTable.c.blockDate)
        .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
        .where(TokenTransfersTable.c.registryAddress == registryAddress)
        .where(TokenTransfersTable.c.toAddress == CREEPZ_STAKING_CONTRACT)
        .order_by(BlocksTable.c.blockDate.asc())
        )
        stakedTokensResult = await self.retriever.database.execute(query=stakedQuery)
        stakedTokens = list(stakedTokensResult)
        unStakedQuery = (
            sqlalchemy.select(TokenTransfersTable.c.tokenId, TokenTransfersTable.c.toAddress, TokenTransfersTable.c.transactionHash, BlocksTable.c.blockDate)
            .join(BlocksTable, BlocksTable.c.blockNumber == TokenTransfersTable.c.blockNumber)
            .where(TokenTransfersTable.c.registryAddress == registryAddress)
            .where(TokenTransfersTable.c.fromAddress == CREEPZ_STAKING_CONTRACT)
            .order_by(BlocksTable.c.blockDate.asc())
            )
        unStakedTokensResult = await self.retriever.database.execute(query=unStakedQuery)
        unStakedTokens = list(unStakedTokensResult)
        # currentlyStakedTokens: Dict[str, Tuple[str, datetime.datetime]] = {}
        currentlyStakedTokens = defaultdict()
        for tokenId, ownerAddress, transactionHash, blockDate in stakedTokens:
            currentlyStakedTokens[tokenId] = (ownerAddress, transactionHash, blockDate)
        for tokenId, ownerAddress, transactionHash, blockDate in unStakedTokens:
            if tokenId not in currentlyStakedTokens.keys():
                continue
            if currentlyStakedTokens[tokenId][2] < blockDate:
                del currentlyStakedTokens[tokenId]
        retrievedStakedTokens = [RetrievedTokenStaking(registryAddress=registryAddress, tokenId=tokenId, stakingAddress=CREEPZ_STAKING_CONTRACT, ownerAddress=ownerAddress, stakingDate=stakingDate, transactionHash=transactionHash) for tokenId, (ownerAddress, transactionHash, stakingDate) in currentlyStakedTokens.items()]
        return retrievedStakedTokens
