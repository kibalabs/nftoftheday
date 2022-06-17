import os
import sys
import asyncio
import logging
import sqlalchemy
from collections import defaultdict
import asyncclick as click

from core.store.database import Database
from core.util import chain_util
from core import logging
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.token_manager import TokenManager
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema_conversions import token_transfer_from_row

@click.command()
@click.option('-s', '--start-block-number', 'startBlock', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlock', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
async def reprocess_multi_transfers(startBlock: int, endBlock: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    workQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/FemiKiBa')
    tokenQueue = SqsMessageQueue(region='us-east-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/FemiKiBa')
    requester = Requester()
    requester = Requester()
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    revueApiKey = os.environ['REVUE_API_KEY']
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=workQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None, collectionActivityProcessor=None)
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=tokenQueue, tokenManager=tokenManager, requester=requester, revueApiKey=revueApiKey)

    await database.connect()
    currentBlockNumber = startBlock
    while currentBlockNumber < endBlock:
        start = currentBlockNumber
        end = min(currentBlockNumber + batchSize, endBlock)
        logging.info(f'Working on {start} to {end}...')
        async with saver.create_transaction() as connection:
            subquery = TokenTransfersTable.select() \
                        .with_only_columns([TokenTransfersTable.c.transactionHash]) \
                        .filter(TokenTransfersTable.c.blockNumber >= start) \
                        .filter(TokenTransfersTable.c.blockNumber < end) \
                        .group_by(TokenTransfersTable.c.transactionHash) \
                        .having(sqlalchemy.func.count(TokenTransfersTable.c.transactionHash) > 1).subquery()
            query = TokenTransfersTable.select() \
                        .with_only_columns([TokenTransfersTable.c.blockNumber])\
                        .where(sqlalchemy.or_(TokenTransfersTable.c.transactionHash.in_(sqlalchemy.select(subquery)), TokenTransfersTable.c.registryAddress == '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85'))
            result = await database.execute(query=query)
            blocksToReprocess = {row[0] for row in result}
            print(len(blocksToReprocess))
            for blockNumber in blocksToReprocess:
                await notdManager.process_block_deferred(blockNumber=blockNumber, shouldSkipProcessingTokens=True)

            subquery = TokenTransfersTable.select() \
                        .with_only_columns([TokenTransfersTable.c.transactionHash]) \
                        .filter(TokenTransfersTable.c.blockNumber >= start) \
                        .filter(TokenTransfersTable.c.blockNumber < end) \
                        .group_by(TokenTransfersTable.c.transactionHash) \
                        .having(sqlalchemy.func.count(TokenTransfersTable.c.transactionHash) == 1).subquery()
            query = TokenTransfersTable.select() \
                        .where(sqlalchemy.and_(TokenTransfersTable.c.transactionHash.in_(sqlalchemy.select(subquery)), TokenTransfersTable.c.registryAddress != '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85'))
            result = await database.execute(query=query)
            tokenTransfersToSet = {row[0] for row in result}
            print(len(tokenTransfersToSet))

            break 
            # transactionHashTokenTransferMap = defaultdict(list)
            # for tokenTransfer in tokenTransfers:
            #     transactionHashTokenTransferMap[tokenTransfer.transactionHash].append(tokenTransfer)
            
            # for transactionHash, tokenTransfers in transactionHashTokenTransferMap.items():
            #     tokens =[(retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId) for retrievedEvent in tokenTransfers]
            #     tokensCount = {(retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId):tokens.count((retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId)) for retrievedEvent in tokenTransfers}
            #     count = len(tokensCount)
            #     setOfAddresses = {tokenTransfer.registryAddress for tokenTransfer in tokenTransfers}
            #     setOfFromAddress = {tokenTransfer.fromAddress for tokenTransfer in tokenTransfers if len(tokenTransfers)>1}
            #     setOfToAddress = {tokenTransfer.toAddress for tokenTransfer in tokenTransfers if len(tokenTransfers)>1}
            #     isSwapTransfer = False
            #     isBatchTransfer = False
            #     logging.info(f'Updating {(len(tokenTransfers))} transfers...')
            #     for tokenTransfer in tokenTransfers:
            #         isMultiAddress = (bool(len(setOfAddresses) > 1))
            #         isSwapTransfer =  bool(tokenTransfer.operatorAddress in setOfFromAddress and tokenTransfer.operatorAddress in setOfToAddress or isSwapTransfer)
            #         if tokensCount[(tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId)] > 1:
            #             isInterstitialTransfer = True
            #             tokensCount[(tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId)] -= 1
            #         else:
            #             isInterstitialTransfer = False
            #             isBatchTransfer = count != tokensCount[(tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId)]

            #         values = {}
            #         values[TokenTransfersTable.c.value.key] = tokenTransfer.value/count if tokenTransfer.value>0 and not (isInterstitialTransfer or isMultiAddress or isSwapTransfer)  else 0
            #         values[TokenTransfersTable.c.isMultiAddress.key] = isMultiAddress
            #         values[TokenTransfersTable.c.isInterstitialTransfer.key] = isInterstitialTransfer
            #         values[TokenTransfersTable.c.isSwapTransfer.key] =   bool(isSwapTransfer and tokenTransfer.toAddress != chain_util.BURN_ADDRESS and tokenTransfer.fromAddress != chain_util.BURN_ADDRESS)
            #         values[TokenTransfersTable.c.isBatchTransfer.key] = isBatchTransfer
            #         query = TokenTransfersTable.update(TokenTransfersTable.c.tokenTransferId == tokenTransfer.tokenTransferId).values(values)
      
            #         await database.execute(query=query, connection=connection)
        currentBlockNumber = currentBlockNumber + batchSize

    await database.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_multi_transfers())
