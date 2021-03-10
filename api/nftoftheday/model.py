import datetime
from typing import Dict

from pydantic import dataclasses

@dataclasses.dataclass
class TokenTransfer:
    transactionHash: str
    registryAddress: str
    fromAddress: str
    toAddress: str
    tokenId: int
    value: int
    gasLimit: int
    gasPrice: int
    gasUsed: int
    blockNumber: int
    blockHash: str
    blockDate: datetime.datetime

    def to_dict(self) -> Dict:
        return {
            'transactionHash': self.transactionHash,
            'registryAddress': self.registryAddress,
            'fromAddress': self.fromAddress,
            'toAddress': self.toAddress,
            'tokenId': self.tokenId,
            'value': self.value,
            'gasLimit': self.gasLimit,
            'gasPrice': self.gasPrice,
            'gasUsed': self.gasUsed,
            'blockNumber': self.blockNumber,
            'blockHash': self.blockHash,
            'blockDate': self.blockDate.isoformat(),
        }
