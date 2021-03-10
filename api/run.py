import asyncio
import os
import json
import logging
from typing import Optional

import asyncclick as click
import boto3
from web3 import Web3

from nftoftheday.internal import NftOfTheDay
from nftoftheday.core.s3_manager import S3Manager

# NOTE(krishan711): test CryptoPunks with block 11999450

async def process_block(processor: NftOfTheDay, s3Manager: S3Manager, blockNumber: int) -> None:
    tokenTransfers = await processor.get_transfers_in_block(blockNumber=blockNumber)
    for tokenTransfer in tokenTransfers:
        logging.debug(f'Transferred {tokenTransfer.tokenId} from {tokenTransfer.fromAddress} to {tokenTransfer.toAddress}')
        logging.debug(f'Paid {tokenTransfer.value / 100000000000000000.0}Ξ ({tokenTransfer.gasUsed * tokenTransfer.gasPrice / 100000000000000000.0}Ξ) to {tokenTransfer.registryAddress}')
        logging.debug(f'OpenSea url: https://opensea.io/assets/{tokenTransfer.registryAddress}/{tokenTransfer.tokenId}')
        logging.debug(f'OpenSea api url: https://api.opensea.io/api/v1/asset/{tokenTransfer.registryAddress}/{tokenTransfer.tokenId}')
    logging.info(f'Found {len(tokenTransfers)} token transfers in block #{blockNumber}')
    if len(tokenTransfers):
        await s3Manager.write_file(content=json.dumps([tokenTransfer.to_dict() for tokenTransfer in tokenTransfers]).encode(), targetPath=f's3://nft-of-the-day/blocks/{blockNumber}.json')

@click.command()
@click.option('-b', '--block-number', 'blockNumber', required=False, type=int)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=False, type=int, default=0)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=False, type=int)
async def run(blockNumber: Optional[int], startBlockNumber: Optional[int], endBlockNumber: Optional[int]):
    w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/rdYIr6T2nBgJvtKlYQxmVH3bvjW2DLxi'))
    processor = NftOfTheDay(web3Connection=w3)

    s3Client = boto3.client(service_name='s3', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3Manager = S3Manager(s3Client=s3Client)

    blockNumbers = [blockNumber] if blockNumber else list(range(startBlockNumber, endBlockNumber))
    await asyncio.gather(*[process_block(processor=processor, s3Manager=s3Manager, blockNumber=blockNumber) for blockNumber in blockNumbers])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')
