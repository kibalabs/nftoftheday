import os
import sys
import time

from core.store.retriever import IntegerFieldFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging

import asyncclick as click
from core.aws_requester import AwsRequester
from core.requester import Requester
from core.slack_client import SlackClient
from core.web3.eth_client import RestEthClient
from databases.core import Database

from notd.block_processor import BlockProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable


async def _reprocess_transfers(startBlockNumber: int, endBlockNumber: int, blockProcessor: BlockProcessor, database: Database, retriever: Retriever, saver: Saver):
    currentBlockNumber = startBlockNumber
    while currentBlockNumber < endBlockNumber:
        logging.info(f'Working on {currentBlockNumber}')
        try:
            retrievedTokenTransfers = await blockProcessor.get_transfers_in_block(blockNumber=currentBlockNumber)
        except Exception as exception:
            logging.info(f'Got exception whilst getting blocks: {str(exception)}. Will retry in 10 secs.')
            time.sleep(60)
            currentBlockNumber -= 1
            continue
        dbTokenTransfers = await retriever.list_token_transfers(fieldFilters=[IntegerFieldFilter(fieldName=TokenTransfersTable.c.blockNumber.key, eq=currentBlockNumber)], shouldIgnoreRegistryBlacklist=True)
        dbTuples = [(dbTokenTransfer.transactionHash, dbTokenTransfer.registryAddress.lower(), dbTokenTransfer.tokenId, dbTokenTransfer.fromAddress.lower(), dbTokenTransfer.toAddress.lower()) for dbTokenTransfer in dbTokenTransfers]
        savedTuples = []
        for retrievedTokenTransfer in retrievedTokenTransfers:
            tuple = (retrievedTokenTransfer.transactionHash, retrievedTokenTransfer.registryAddress.lower(), retrievedTokenTransfer.tokenId, retrievedTokenTransfer.fromAddress.lower(), retrievedTokenTransfer.toAddress.lower())
            if tuple in savedTuples:
                logging.info(f'Ignoring duplicate tuple: {tuple}')
                continue
            if tuple not in dbTuples:
                logging.info('Saving new')
                await saver.create_token_transfer(retrievedTokenTransfer=retrievedTokenTransfer)
                savedTuples.append(tuple)
            else:
                query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == dbTokenTransfers[dbTuples.index(tuple)].tokenTransferId)
                values = {
                    TokenTransfersTable.c.toAddress.key: retrievedTokenTransfer.toAddress,
                    TokenTransfersTable.c.fromAddress.key: retrievedTokenTransfer.fromAddress,
                    TokenTransfersTable.c.registryAddress.key: retrievedTokenTransfer.registryAddress,
                    TokenTransfersTable.c.operatorAddress.key: retrievedTokenTransfer.operatorAddress,
                    TokenTransfersTable.c.amount.key: retrievedTokenTransfer.amount,
                    TokenTransfersTable.c.tokenType.key: retrievedTokenTransfer.tokenType,
                }
                logging.info('Updating old')
                await database.execute(query=query, values=values)
        currentBlockNumber = currentBlockNumber + 1


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
async def reprocess_transfers(startBlockNumber: int, endBlockNumber: int):
    database = Database(f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}')
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    requester = Requester()
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')

    # infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
    # infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
    # ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)

    await database.connect()
    await slackClient.post(text=f'reprocess_transfers → 🚧 started: {startBlockNumber}-{endBlockNumber}')
    try:
        await _reprocess_transfers(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber, blockProcessor=blockProcessor, database=database, retriever=retriever, saver=saver)
        await slackClient.post(text=f'reprocess_transfers → ✅ completed : {startBlockNumber}-{endBlockNumber}')
    except Exception as exception:
        await slackClient.post(text=f'reprocess_transfers → ❌ error: {startBlockNumber}-{endBlockNumber}\n```{str(exception)}```')
        raise exception
    finally:
        await database.disconnect()
        await requester.close_connections()
        await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_transfers())
