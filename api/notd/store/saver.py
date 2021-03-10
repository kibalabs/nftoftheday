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
            # if ('Duplicate entry' in str(exception)):
            raise InternalServerErrorException(message='Error running save operation')

    async def create_token_transfer(self, transactionHash: str, registryAddress: str, fromAddress: str, toAddress: str, tokenId: int, value: int, gasLimit: int, gasPrice: int, gasUsed: int, blockNumber: int, blockHash: str, blockDate: datetime.datetime) -> TokenTransfer:
        tokenTransferId = await self._execute(query=TokenTransfersTable.insert(), values={
            TokenTransfersTable.c.transaction_hash.name: transactionHash,
            TokenTransfersTable.c.registry_address.name: registryAddress,
            TokenTransfersTable.c.from_address.name: fromAddress,
            TokenTransfersTable.c.to_address.name: toAddress,
            TokenTransfersTable.c.token_id.name: tokenId,
            TokenTransfersTable.c.value.name: value,
            TokenTransfersTable.c.gas_limit.name: gasLimit,
            TokenTransfersTable.c.gas_price.name: gasPrice,
            TokenTransfersTable.c.gas_used.name: gasUsed,
            TokenTransfersTable.c.block_number.name: blockNumber,
            TokenTransfersTable.c.block_hash.name: blockHash,
            TokenTransfersTable.c.block_date.name: blockDate,
        })
        return TokenTransfer(tokenTransferId=tokenTransferId, transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, tokenId=tokenId, value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=gasUsed, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate)
