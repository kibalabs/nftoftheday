import datetime

from core.store.saver import Saver as CoreSaver

from notd.model import TokenTransfer
from notd.store.schema import TokenTransfersTable


class Saver(CoreSaver):

    async def create_token_transfer(self, transactionHash: str, registryAddress: str, fromAddress: str, toAddress: str, tokenId: int, value: int, gasLimit: int, gasPrice: int, gasUsed: int, blockNumber: int, blockHash: str, blockDate: datetime.datetime) -> TokenTransfer:
        tokenTransferId = await self._execute(query=TokenTransfersTable.insert(), values={  # pylint: disable=no-value-for-parameter
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
