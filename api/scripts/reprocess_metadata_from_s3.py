import asyncio
import json
import logging
import os
import sys
from typing import Optional

import asyncclick as click
import boto3
from core.s3_manager import S3Manager
from core.store.database import Database
from core.requester import Requester
from core.s3_manager import S3Manager
from core.aws_requester import AwsRequester
from core.store.database import Database
from core.web3.eth_client import RestEthClient

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.retriever import Retriever
from notd.store.saver import Saver
from notd.store.schema import TokenMetadataTable
from notd.store.schema_conversions import token_metadata_from_row
from notd.token_manager import TokenManager
from notd.token_metadata_processor import TokenMetadataProcessor


@click.command()
@click.option('-s', '--start-id-number', 'startId', required=False, type=int)
@click.option('-e', '--end-id-number', 'endId', required=False, type=int)
async def reprocess_metadata(startId: Optional[int], endId: Optional[int]):

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)

    s3Client = boto3.client(service_name='s3', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    requester = Requester()

    #ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)

    requester = Requester()
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])
    tokenManger = TokenManager(saver=saver, retriever=retriever, tokenQueue=None, collectionProcessor=None, tokenMetadataProcessor=tokenMetadataProcessor)

    await database.connect()
    query = TokenMetadataTable.select()
    if startId:
        query = query.where(TokenMetadataTable.c.tokenMetadataId >= startId)
    if endId:
        query = query.where(TokenMetadataTable.c.tokenMetadataId < endId)
    tokenMetadatasToChange = [token_metadata_from_row(row) for row in await database.execute(query=query)]
    logging.info(f'Updating {len(tokenMetadatasToChange)} transfers...')
    for tokenMetadata in tokenMetadatasToChange:
        tokenDirectory = f'{os.environ["S3_BUCKET"]}/token-metadatas/{tokenMetadata.registryAddress}/{tokenMetadata.tokenId}/'
        tokenFile = None
        tokenMetadataFiles = [file async for file in s3manager.generate_directory_files(s3Directory=tokenDirectory)]
        if len(tokenMetadataFiles) > 0:
            tokenFile=(tokenMetadataFiles[len(tokenMetadataFiles)-1])
            tokenMetadataJson = await s3manager.read_file(sourcePath=f'{tokenFile.bucket}/{tokenFile.path}')
            tokenMetadataDict = json.loads(tokenMetadataJson)
            retrievedTokenMetadata = await tokenMetadataProcessor._get_token_metadata_from_data(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, metadataUrl=tokenMetadata.metadataUrl, tokenMetadataDict=tokenMetadataDict)
            logging.info(f'Updating {(tokenMetadata.tokenMetadataId)}')
            await tokenManger.save_token_metadata(retrievedTokenMetadata=retrievedTokenMetadata)
        else:
            logging.info(f'Saving Token Metadata for {tokenMetadata.tokenMetadataId}')
            await tokenManger.update_token_metadata(registryAddress=tokenMetadata.registryAddress, tokenId=tokenMetadata.tokenId, shouldForce=True)

    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(reprocess_metadata())
