import os
import sys

from core.store.retriever import IntegerFieldFilter


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
import boto3
from core.queues.sqs_message_queue import SqsMessageQueue
from core.http.basic_authentication import BasicAuthentication
from core.requester import Requester
from core.s3_manager import S3Manager

from core.web3.eth_client import RestEthClient
from databases.core import Database

# from notd.messages import UpdateTokenMetadataMessageContent
from notd.store.saver import Saver
from notd.store.schema import  TokenTransfersTable
from notd.block_processor import BlockProcessor
from notd.store.retriever import Retriever


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=5)
async def reprocess_transfers(startBlockNumber: int, endBlockNumber: int, batchSize: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    
    infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
    infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    
    await database.connect()
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        logging.info(f'Working on {currentBlockNumber}')
        retrievedTokenTransfers = await blockProcessor.get_transfers_in_block(blockNumber=currentBlockNumber)
        dbTokenTransfers = await retriever.list_token_transfers(
            fieldFilters=[
                IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, eq=currentBlockNumber),
            ])
        retrievedTuples = [(retrievedTokenTransfer.transactionHash, retrievedTokenTransfer.registryAddress, retrievedTokenTransfer.tokenId, retrievedTokenTransfer.fromAddress, retrievedTokenTransfer.toAddress) for retrievedTokenTransfer in retrievedTokenTransfers]
        dbTuples = [(dbTokenTransfer.transactionHash, dbTokenTransfer.registryAddress, dbTokenTransfer.tokenId, dbTokenTransfer.fromAddress, dbTokenTransfer.toAddress) for dbTokenTransfer in dbTokenTransfers]
        for index,tuple in enumerate(retrievedTuples):
            if tuple not in dbTuples:
                await saver.create_token_transfer(retrievedTokenTransfer=retrievedTokenTransfers[index])
            else:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == dbTokenTransfers[dbTuples.index(tuple)].tokenTransferId)
                values = {}
                values[TokenTransfersTable.c.operatorAddress.key] = retrievedTokenTransfers[index].operatorAddress
                values[TokenTransfersTable.c.amount.key] = retrievedTokenTransfers[index].amount
                values[TokenTransfersTable.c.tokenType.key] = retrievedTokenTransfers[index].tokenType
                await database.execute(query=query, values=values)

        currentBlockNumber = currentBlockNumber + 1
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_transfers())
