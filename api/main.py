import json
import logging

from web3 import Web3

from nftoftheday.internal import NftOfTheDay

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/rdYIr6T2nBgJvtKlYQxmVH3bvjW2DLxi'))
    processor = NftOfTheDay(web3Connection=w3)

    # s3Client = boto3.client(service_name='s3', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    # s3Manager = S3Manager(s3Client=s3Client)

    blockNumber = 6517190
    tokenTransfers = processor.get_transfers_in_block(blockNumber=blockNumber)
    for tokenTransfer in tokenTransfers:
        logging.debug(f'Transferred {tokenTransfer.tokenId} from {tokenTransfer.fromAddress} to {tokenTransfer.toAddress}')
        logging.debug(f'Paid {tokenTransfer.value / 100000000000000000.0}Ξ ({tokenTransfer.gasUsed * tokenTransfer.gasPrice / 100000000000000000.0}Ξ) to {tokenTransfer.registryAddress}')
        logging.debug(f'OpenSea url: https://opensea.io/assets/{tokenTransfer.registryAddress}/{tokenTransfer.tokenId}')
        logging.debug(f'OpenSea api url: https://api.opensea.io/api/v1/asset/{tokenTransfer.registryAddress}/{tokenTransfer.tokenId}')
    logging.info(f'Found {len(tokenTransfers)} token transfers')
    if len(tokenTransfers):
        with open(f'./blocks/{blockNumber}.json', 'w') as outputFile:
            outputFile.write(json.dumps([tokenTransfer.to_dict() for tokenTransfer in tokenTransfers]))
