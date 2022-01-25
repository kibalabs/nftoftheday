import base64
import logging
import os
import sys

from api.notd.model import RetrievedTokenMetadata


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from async_timeout import asyncio
import boto3

from core.aws_requester import AwsRequester
from core.requester import Requester
from core.s3_manager import S3Manager
from core.web3.eth_client import RestEthClient
from notd.block_processor import BlockProcessor
from notd.token_metadata_processor import TokenMetadataProcessor

async def main():
    s3Client = boto3.client(service_name='s3', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)

    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])

    result = tokenMetadataProcessor.get_default_token_metadata(registryAddress='0x57E9a39aE8eC404C08f88740A9e6E306f50c937f',tokenId=165)
    expected = RetrievedTokenMetadata(registryAddress='0x57E9a39aE8eC404C08f88740A9e6E306f50c937f',tokenId='165',metadataUrl=base64.b64encode('{}'.encode()),imageUrl=None,name='#164',description=None,attributes=[])
    assert (result == expected)
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())