import json
import os

import asyncclick as click
from core import logging
# from core.aws_requester import AwsRequester
from core.http.basic_authentication import BasicAuthentication
from core.queues.sqs import SqsMessageQueue
from core.requester import Requester
from core.s3_manager import S3Manager
from core.store.database import Database
from core.web3.eth_client import RestEthClient
from mdtp.image_manager import ImageManager
from mdtp.ipfs_manager import IpfsManager
from mdtp.manager import MdtpManager
from mdtp.store.retriever import Retriever
from mdtp.store.saver import Saver

from contracts import create_contract_store

GWEI = 1000000000

@click.command()
async def run():
    logging.init_basic_logging()
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)

    workQueue = SqsMessageQueue(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'], queueUrl='https://sqs.eu-west-1.amazonaws.com/097520841056/mdtp-work-queue')
    s3Manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])

    # awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    # ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)
    requester = Requester()
    ethClient = RestEthClient(url=os.environ['ALCHEMY_MAINNET_URL'], requester=requester)
    rinkebyEthClient = RestEthClient(url=os.environ['ALCHEMY_URL'], requester=requester)
    mumbaiEthClient = RestEthClient(url='https://matic-mumbai.chainstacklabs.com', requester=requester)
    contractStore = create_contract_store(ethClient=ethClient, rinkebyEthClient=rinkebyEthClient, mumbaiEthClient=mumbaiEthClient)

    infuraUsername = os.environ['INFURA_IPFS_PROJECT_ID']
    infuraPassword = os.environ['INFURA_IPFS_PROJECT_SECRET']
    infuraAuth = BasicAuthentication(username=infuraUsername, password=infuraPassword)
    infuraRequester = Requester(headers={'Authorization': f'Basic {infuraAuth.to_string()}'})
    ipfsManager = IpfsManager(infuraRequester=infuraRequester)

    imageManager = ImageManager(requester=requester, s3Manager=s3Manager, ipfsManager=ipfsManager)
    manager = MdtpManager(requester=requester, retriever=retriever, saver=saver, s3Manager=s3Manager, contractStore=contractStore, workQueue=workQueue, imageManager=imageManager, ipfsManager=ipfsManager)
    await database.connect()
    await workQueue.connect()
    await s3Manager.connect()

    pinataApiKey = os.environ['PINATA_API_KEY']
    pinataRequester = Requester(headers={'Authorization': f'Bearer {pinataApiKey}'})
    offset = 0
    while True:
        response = await pinataRequester.get(url='https://api.pinata.cloud/data/pinList', dataDict={'includesCount': False, 'pageLimit': 210, 'pageOffset': offset, 'status': 'pinned', 'pinEnd': '2022-05-07T00:00:00.00Z', 'pinStart': '2022-05-06T00:00:00.00Z'})
        responseDict = json.loads(response.text)
        print('count:', responseDict['count'])
        if responseDict['count'] == 0:
            break
        for row in responseDict['rows']:
            print('file', row['ipfs_pin_hash'], row['size'], row['date_pinned'])
            try:
                await ipfsManager.pin_cid(cid=row['ipfs_pin_hash'])
                await pinataRequester.make_request(method='DELETE', url=f'https://api.pinata.cloud/pinning/unpin/{row["ipfs_pin_hash"]}')
            except:
                print('Failed to pin:', row['ipfs_pin_hash'])
                offset += 1
    await pinataRequester.close_connections()

    # await awsRequester.close_connections()
    await requester.close_connections()
    await infuraRequester.close_connections()
    await workQueue.disconnect()
    await s3Manager.disconnect()
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run(_anyio_backend='asyncio')
