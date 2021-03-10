import asyncio
import os
import json
import logging
from typing import Optional

import asyncclick as click
import boto3
from web3 import Web3
from databases import Database

from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.core.s3_manager import S3Manager
from notd.store.saver import Saver

# NOTE(krishan711): test CryptoPunks with block 11999450

@click.command()
@click.option('-b', '--block-number', 'blockNumber', required=False, type=int)
@click.option('-s', '--start-block-number', 'startBlockNumber', required=False, type=int, default=0)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=False, type=int)
async def run(blockNumber: Optional[int], startBlockNumber: Optional[int], endBlockNumber: Optional[int]):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/rdYIr6T2nBgJvtKlYQxmVH3bvjW2DLxi'))
    blockProcessor = BlockProcessor(web3Connection=w3)
    manager = NotdManager(blockProcessor=blockProcessor, saver=saver)

    await database.connect()
    if blockNumber:
        await manager.process_block(blockNumber=blockNumber)
    elif startBlockNumber and endBlockNumber:
        await manager.process_block_range(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber)
    else:
        raise Exception('Either blockNumber or startBlockNumber and endBlockNumber must be passed in.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run(_anyio_backend='asyncio')
