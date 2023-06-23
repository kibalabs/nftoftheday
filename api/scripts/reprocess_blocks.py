import asyncio
import math
import os
import sys
import time

import asyncclick as click
import sqlalchemy
from core import logging
from core.http.basic_authentication import BasicAuthentication
from core.queues.sqs import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient
from core.store.database import Database
from core.util import list_util
from core.web3.eth_client import RestEthClient
from pablo import PabloClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.activity_manager import ActivityManager
from notd.attribute_manager import AttributeManager
from notd.badge_manager import BadgeManager
from notd.badge_processor import BadgeProcessor
from notd.block_manager import BlockManager
from notd.block_processor import BlockProcessor
from notd.collection_activity_processor import CollectionActivityProcessor
from notd.collection_manager import CollectionManager
from notd.collection_overlap_manager import CollectionOverlapManager
from notd.collection_overlap_processor import CollectionOverlapProcessor
from notd.collection_processor import CollectionProcessor
from notd.delegation_manager import DelegationManager
from notd.listing_manager import ListingManager
from notd.lock_manager import LockManager
from notd.manager import NotdManager
from notd.notd_message_processor import NotdMessageProcessor
from notd.ownership_manager import OwnershipManager
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import BlocksTable
from notd.token_attributes_processor import TokenAttributeProcessor
from notd.token_listing_processor import TokenListingProcessor
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor
from notd.token_ownership_processor import TokenOwnershipProcessor
from notd.token_staking_manager import TokenStakingManager
from notd.token_staking_processor import TokenStakingProcessor
from notd.twitter_manager import TwitterManager


async def reprocess_block(notdManager: NotdManager, blockNumber: int):
    try:
        await notdManager.process_block(blockNumber=blockNumber, shouldSkipProcessingTokens=True, shouldSkipUpdatingOwnerships=True)
    except Exception as exception:
        logging.error(f'Failed to process block {blockNumber}: {exception}')


@click.command()
@click.option('-s', '--start-block-number', 'startBlockNumber', required=True, type=int)
@click.option('-e', '--end-block-number', 'endBlockNumber', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=1000)
@click.option('-x', '--exclude-existing', 'shouldExcludeExisting', default=False, is_flag=True)
async def reprocess_blocks(startBlockNumber: int, endBlockNumber: int, batchSize: int, shouldExcludeExisting: bool):
    openseaApiKey = os.environ['OPENSEA_API_KEY']
    revueApiKey = os.environ['REVUE_API_KEY']
    accessKeyId = os.environ['AWS_KEY']
    accessKeySecret = os.environ['AWS_SECRET']
    twitterBearerToken = os.environ["TWITTER_BEARER_TOKEN"]
    ethNodeUsername = os.environ["ETH_NODE_USERNAME"]
    ethNodePassword = os.environ["ETH_NODE_PASSWORD"]
    ethNodeUrl = os.environ["ETH_NODE_URL"]

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-work-queue')
    tokenQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=accessKeyId, accessKeySecret=accessKeySecret, queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/notd-token-queue')
    ethNodeAuth = BasicAuthentication(username=ethNodeUsername, password=ethNodePassword)
    ethNodeRequester = Requester(headers={'Authorization': f'Basic {ethNodeAuth.to_string()}'})
    ethClient = RestEthClient(url=ethNodeUrl, requester=ethNodeRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    pabloClient = PabloClient(requester=requester)
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, pabloClient=pabloClient)
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey)
    tokenOwnershipProcessor = TokenOwnershipProcessor(retriever=retriever)
    collectionActivityProcessor = CollectionActivityProcessor(retriever=retriever)
    openseaRequester = Requester(headers={"Accept": "application/json", "X-API-KEY": openseaApiKey})
    lockManager = LockManager(retriever=retriever, saver=saver)
    tokenAttributeProcessor = TokenAttributeProcessor(retriever=retriever)
    collectionOverlapProcessor = CollectionOverlapProcessor(retriever=retriever)
    activityManager = ActivityManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, collectionActivityProcessor=collectionActivityProcessor)
    attributeManager = AttributeManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenQueue=tokenQueue, tokenAttributeProcessor=tokenAttributeProcessor)
    collectionManager = CollectionManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, collectionProcessor=collectionProcessor)
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=openseaRequester, lockManager=lockManager, collectionManger=collectionManager)
    collectionOverlapManager = CollectionOverlapManager(saver=saver, retriever=retriever, workQueue=workQueue, collectionOverlapProcessor=collectionOverlapProcessor)
    ownershipManager = OwnershipManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenOwnershipProcessor=tokenOwnershipProcessor, lockManager=lockManager, collectionManager=collectionManager)
    listingManager = ListingManager(saver=saver, retriever=retriever, workQueue=workQueue, tokenListingProcessor=tokenListingProcessor)
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=tokenQueue, tokenMetadataProcessor=tokenMetadataProcessor, collectionManager=collectionManager, ownershipManager=ownershipManager)
    twitterManager = TwitterManager(saver=saver, retriever=retriever, requester=requester, workQueue=workQueue, twitterBearerToken=twitterBearerToken)
    badgeProcessor = BadgeProcessor(retriever=retriever, saver=saver)
    badgeManager = BadgeManager(retriever=retriever, saver=saver, workQueue=workQueue, badgeProcessor=badgeProcessor)
    delegationManager = DelegationManager(ethClient=ethClient)
    tokenStakingProcessor = TokenStakingProcessor(ethClient=ethClient, retriever=retriever)
    tokenStakingManager = TokenStakingManager(retriever=retriever, saver=saver, tokenQueue=tokenQueue, workQueue=workQueue, tokenStakingProcessor=tokenStakingProcessor)
    blockManager = BlockManager(saver=saver, retriever=retriever, workQueue=workQueue, blockProcessor=blockProcessor, tokenManager=tokenManager, collectionManager=collectionManager, ownershipManager=ownershipManager, tokenStakingManager=tokenStakingManager)
    notdManager = NotdManager(saver=saver, retriever=retriever, workQueue=workQueue, blockManager=blockManager, tokenManager=tokenManager, activityManager=activityManager, attributeManager=attributeManager, collectionManager=collectionManager, ownershipManager=ownershipManager, listingManager=listingManager, twitterManager=twitterManager, collectionOverlapManager=collectionOverlapManager, badgeManager=badgeManager, delegationManager=delegationManager, tokenStakingManager=tokenStakingManager, requester=requester, revueApiKey=revueApiKey)
    processor = NotdMessageProcessor(notdManager=notdManager)
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')

    await database.connect()
    await workQueue.connect()
    await tokenQueue.connect()
    await slackClient.post(text=f'reprocess_blocks → 🚧 started: {startBlockNumber}-{endBlockNumber}')
    try:
        currentBlockNumber = startBlockNumber
        milestoneBlockSize = math.ceil((endBlockNumber - startBlockNumber) / 100)
        nextMilestoneBlockNumber = currentBlockNumber + milestoneBlockSize
        while currentBlockNumber < endBlockNumber:
            start = currentBlockNumber
            end = min(currentBlockNumber + batchSize, endBlockNumber)
            logging.info(f'Working on {start} to {end}...')
            blocksToReprocess = set(list(range(start, end)))
            if shouldExcludeExisting:
                existingBlocksQuery = (
                    sqlalchemy.select(BlocksTable.c.blockNumber)
                    .where(BlocksTable.c.blockNumber >= start)
                    .where(BlocksTable.c.blockNumber < end)
                )
                existingBlocksResult = await database.execute(query=existingBlocksQuery)
                blocksAlreadyProcessed = {row[BlocksTable.c.blockNumber] for row in existingBlocksResult.mappings()}
                logging.info(f'Skipping {len(blocksAlreadyProcessed)} already processed blocks')
                blocksToReprocess = blocksToReprocess - blocksAlreadyProcessed
            logging.info(f'Reprocessing {len(blocksToReprocess)} blocks')
            for chunk in list_util.generate_chunks(lst=list(blocksToReprocess), chunkSize=50):
                await asyncio.gather(*[reprocess_block(notdManager=notdManager, blockNumber=blockNumber) for blockNumber in chunk])
            currentBlockNumber = currentBlockNumber + batchSize
            if currentBlockNumber > nextMilestoneBlockNumber:
                await slackClient.post(text=f'reprocess_blocks → 🚧 still going: {currentBlockNumber} / {startBlockNumber}-{endBlockNumber}')
                nextMilestoneBlockNumber = currentBlockNumber + milestoneBlockSize
        await slackClient.post(text=f'reprocess_blocks → ✅ completed : {startBlockNumber}-{endBlockNumber}')
    except Exception as exception:
        await slackClient.post(text=f'reprocess_blocks → ❌ error: {startBlockNumber}-{endBlockNumber}\n```{str(exception)}```')
        raise exception
    finally:
        await database.disconnect()
        await workQueue.disconnect()
        await tokenQueue.disconnect()
        await requester.close_connections()
        await ethNodeRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_blocks())
