import datetime

from notd.model import TokenTransfer
from notd.store.schema import TokenTransfersTable

def token_transfer_from_row(row: TokenTransfersTable) -> TokenTransfer:
    return TokenTransfer(
        transactionHash=row.transaction_hash,
        registryAddress=row.registry_address,
        fromAddress=row.from_address,
        toAddress=row.to_address,
        tokenId=row.token_id,
        value=row.value,
        gasLimit=row.gas_limit,
        gasPrice=row.gas_price,
        gasUsed=row.gas_used,
        blockNumber=row.block_number,
        blockHash=row.block_hash,
        blockDate=row.block_date.replace(tzinfo=datetime.timezone.utc),
    )
