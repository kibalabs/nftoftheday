import asyncio
import datetime
import logging
import os
import sys
from typing import Optional

import asyncclick as click
import sqlalchemy
from core.aws_requester import AwsRequester
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.util import list_util
from core.web3.eth_client import RestEthClient


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_processor import BlockProcessor
from notd.manager import NotdManager
from notd.store.retriever import Retriever
from notd.token_manager import TokenManager
from notd.store.saver import Saver
from notd.store.schema import BlocksTable, TokenMetadatasTable
from notd.store.schema import TokenTransfersTable
from notd.store.schema import TokenCollectionsTable



@click.command()
@click.option('-r', '--registry-addess', 'registryAddress', required=False, type=str)
async def run(registryAddress: Optional[str]):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    requester = Requester()
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=None, tokenMetadataProcessor=None, tokenOwnershipProcessor=None)
    # NOTE(krishan711): use tokenqueue so its lower prioritized work
    notdManager = NotdManager(blockProcessor=blockProcessor, saver=saver, retriever=retriever, workQueue=tokenQueue, tokenManager=tokenManager, requester=requester, revueApiKey=None)

    await database.connect()
    await workQueue.connect()
    await tokenQueue.connect()

    if registryAddress:
        registryAddresses = [registryAddress]
    else:
        query = sqlalchemy.select(TokenCollectionsTable.c.address).filter(TokenCollectionsTable.c.doesSupportErc1155 == True).order_by(TokenCollectionsTable.c.collectionId)
        results = await database.execute(query=query)
        registryAddresses = [registryAddress for (registryAddress, ) in results]
    print(f'Starting to reprocess blocks for {len(registryAddresses)} collections')

    for registryAddress in registryAddresses:
        print(f'Reprocessing blocks for collection: {registryAddress}')
        minDate = datetime.datetime(2022, 4, 8, 9, 0)
        query = (
            sqlalchemy.select(sqlalchemy.distinct(BlocksTable.c.blockNumber)) \
            .join(TokenTransfersTable, TokenTransfersTable.c.blockNumber == BlocksTable.c.blockNumber) \
            .filter(TokenTransfersTable.c.registryAddress == registryAddress)
            .filter(BlocksTable.c.updatedDate < minDate)
        )
        results = await database.execute(query=query)
        blockNumbers = set(blockNumber for (blockNumber, ) in results)
        print(f'Processing {len(blockNumbers)} blocks')
        # await notdManager.process_blocks_deferred(blockNumbers=blockNumbers)
        for blockNumberChunk in list_util.generate_chunks(lst=list(blockNumbers), chunkSize=5):
            await asyncio.gather(*[notdManager.process_block(blockNumber=blockNumber) for blockNumber in blockNumberChunk])
        query = (
            sqlalchemy.select(TokenMetadatasTable.c.tokenId) \
            .filter(TokenMetadatasTable.c.registryAddress == registryAddress)
        )
        results = await database.execute(query=query)
        collectionTokenIds = [(registryAddress, tokenId) for (tokenId, ) in results]
        await tokenManager.update_token_ownerships_deferred(collectionTokenIds=collectionTokenIds)
    await database.disconnect()
    await workQueue.disconnect()
    await tokenQueue.disconnect()
    await requester.close_connections()
    await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
