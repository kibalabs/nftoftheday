import asyncio
import logging
import os
import sys

import asyncclick as click
from core.aws_requester import AwsRequester
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.database import Database
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.collection_processor import CollectionProcessor
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenCollectionsTable
from notd.store.schema_conversions import collection_from_row
from notd.token_manager import TokenManager


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=True, type=int)
@click.option('-e', '--end-id-number', 'endId', required=True, type=int)
@click.option('-b', '--batch-size', 'batchSize', required=False, type=int, default=100)
async def reprocess_collections(startId: int, endId: int, batchSize: int):
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database)
    retriever = Retriever(database)
    openseaApiKey = os.environ['OPENSEA_API_KEY']
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    requester = Requester()
    # ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    s3manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    requester = Requester()
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, openseaApiKey=openseaApiKey, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    tokenManager = TokenManager(saver=saver, retriever=retriever, tokenQueue=None, collectionProcessor=collectionProcessor, tokenMetadataProcessor=None)

    await database.connect()
    await s3manager.connect()
    currentId = startId
    while currentId < endId:
        start = currentId
        end = min(currentId + batchSize, endId)
        logging.info(f'Working on {start} to {end}...')
        async with database.transaction():
            query = TokenCollectionsTable.select()
            query = query.where(TokenCollectionsTable.c.collectionId >= start)
            query = query.where(TokenCollectionsTable.c.collectionId < end)
            collectionsToChange = [collection_from_row(row) async for row in database.iterate(query=query)]
            logging.info(f'Updating {len(collectionsToChange)} collections...')
            for collection in collectionsToChange:
                logging.info(f'Updating collection: {collection.address}')
                try:
                   await tokenManager.update_collection(address=collection.address, shouldForce=True)
                except Exception as e:
                    logging.exception(f'Error processing {collection.collectionId}: {e}')
        currentId = currentId + batchSize

    await database.disconnect()
    await s3manager.disconnect()
    await requester.close_connections()
    await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_collections())
