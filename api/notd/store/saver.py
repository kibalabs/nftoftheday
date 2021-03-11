import logging
from typing import Optional
from typing import Dict

import asyncpg
from databases import Database
from sqlalchemy.sql import ClauseElement
from sqlalchemy.exc import IntegrityError

from notd.model import *
from notd.core.exceptions import *
from notd.store.schema import *

class Saver:

    def __init__(self, database: Database):
        self.database = database

    async def _execute(self, query: ClauseElement, values: Optional[Dict]):
        try:
            return await self.database.execute(query=query, values=values)
        except asyncpg.exceptions.UniqueViolationError as exception:
            raise DuplicateValueException(message=str(exception))
        except Exception as exception:
            logging.error(exception)
            raise InternalServerErrorException(message='Error running save operation')

    async def create_token_transfer(self, transactionHash: str, registryAddress: str, fromAddress: str, toAddress: str, tokenId: int, value: int, gasLimit: int, gasPrice: int, gasUsed: int, blockNumber: int, blockHash: str, blockDate: datetime.datetime) -> TokenTransfer:
        tokenTransferId = await self._execute(query=TokenTransfersTable.insert(), values={
            TokenTransfersTable.c.transactionHash.key: transactionHash,
            TokenTransfersTable.c.registryAddress.key: registryAddress,
            TokenTransfersTable.c.fromAddress.key: fromAddress,
            TokenTransfersTable.c.toAddress.key: toAddress,
            TokenTransfersTable.c.tokenId.key: tokenId,
            TokenTransfersTable.c.value.key: value,
            TokenTransfersTable.c.gasLimit.key: gasLimit,
            TokenTransfersTable.c.gasPrice.key: gasPrice,
            TokenTransfersTable.c.gasUsed.key: gasUsed,
            TokenTransfersTable.c.blockNumber.key: blockNumber,
            TokenTransfersTable.c.blockHash.key: blockHash,
            TokenTransfersTable.c.blockDate.key: blockDate,
        })
        return TokenTransfer(tokenTransferId=tokenTransferId, transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, tokenId=tokenId, value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=gasUsed, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate)
