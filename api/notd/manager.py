import asyncio
import logging
from typing import List

from notd.chain_processor import ChainProcessor
from notd.store.saver import Saver
from notd.core.exceptions import DuplicateValueException

class NotdManager:

    def __init__(self, chainProcessor: ChainProcessor, saver: Saver):
        self.chainProcessor = chainProcessor
        self.saver = saver

    async def process_block_range(self, startBlockNumber: int, endBlockNumber: int) -> None:
        blockNumbers = list(range(startBlockNumber, endBlockNumber))
        await self.process_blocks(blockNumbers=blockNumbers)

    async def process_blocks(self, blockNumbers: List[int]) -> None:
        await asyncio.gather(*[self.process_block(blockNumber=blockNumber) for blockNumber in blockNumbers])

    async def process_block(self, blockNumber: int) -> None:
        retrievedTokenTransfers = await self.chainProcessor.get_transfers_in_block(blockNumber=blockNumber)
        logging.info(f'Found {len(retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        for retrievedTokenTransfer in retrievedTokenTransfers:
            logging.debug(f'Transferred {retrievedTokenTransfer.tokenId} from {retrievedTokenTransfer.fromAddress} to {retrievedTokenTransfer.toAddress}')
            logging.debug(f'Paid {retrievedTokenTransfer.value / 100000000000000000.0}Ξ ({retrievedTokenTransfer.gasUsed * retrievedTokenTransfer.gasPrice / 100000000000000000.0}Ξ) to {retrievedTokenTransfer.registryAddress}')
            logging.debug(f'OpenSea url: https://opensea.io/assets/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
            logging.debug(f'OpenSea api url: https://api.opensea.io/api/v1/asset/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
            try:
                await self.saver.create_token_transfer(transactionHash=retrievedTokenTransfer.transactionHash, registryAddress=retrievedTokenTransfer.registryAddress, fromAddress=retrievedTokenTransfer.fromAddress, toAddress=retrievedTokenTransfer.toAddress, tokenId=retrievedTokenTransfer.tokenId, value=retrievedTokenTransfer.value, gasLimit=retrievedTokenTransfer.gasLimit, gasPrice=retrievedTokenTransfer.gasPrice, gasUsed=retrievedTokenTransfer.gasUsed, blockNumber=retrievedTokenTransfer.blockNumber, blockHash=retrievedTokenTransfer.blockHash, blockDate=retrievedTokenTransfer.blockDate)
            except DuplicateValueException:
                logging.debug(f'Ignoring previously saved transaction')
