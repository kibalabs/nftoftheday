import asyncio
import json
import logging
import os
import sys

import asyncclick as click
from core.aws_requester import AwsRequester
from core.web3.eth_client import RestEthClient
from core.requester import Requester
from core.exceptions import BadRequestException

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@click.command()
@click.option('-a', '--collection-address', 'address', required=True, type=str)
async def update_collection(address: str):
    requester = Requester()
    awsRequester = AwsRequester(accessKeyId=os.environ['AWS_KEY'], accessKeySecret=os.environ['AWS_SECRET'])
    ethClient = RestEthClient(url='https://nd-foldvvlb25awde7kbqfvpgvrrm.ethereum.managedblockchain.eu-west-1.amazonaws.com', requester=awsRequester)

    with open('./contracts/IERC721.json') as contractJsonFile:
        erc721ContractJson = json.load(contractJsonFile)
    erc721ContractAbi = erc721ContractJson['abi']
    with open('./contracts/IERC721Metadata.json') as contractJsonFile:
        erc721MetadataContractJson = json.load(contractJsonFile)
    erc721MetadataContractAbi = erc721MetadataContractJson['abi']
    with open('./contracts/IERC721Enumerable.json') as contractJsonFile:
        erc721EnumerableContractJson = json.load(contractJsonFile)
    erc721EnumerableContractAbi = erc721EnumerableContractJson['abi']
    erc721TotalSupplyFunctionAbi = [internalAbi for internalAbi in erc721EnumerableContractAbi if internalAbi.get('name') == 'totalSupply'][0]
    erc721MetadataUriFunctionAbi = [internalAbi for internalAbi in erc721MetadataContractAbi if internalAbi.get('name') == 'tokenURI'][0]

    totalSupply = (await ethClient.call_function(toAddress=address, contractAbi=erc721EnumerableContractAbi, functionAbi=erc721TotalSupplyFunctionAbi))[0]
    for tokenId in range(int(totalSupply)):
        try:
            await ethClient.call_function(toAddress=address, contractAbi=erc721MetadataContractAbi, functionAbi=erc721MetadataUriFunctionAbi, arguments={'tokenId': int(tokenId)})
        except BadRequestException:
            continue
        await requester.get(url=f'https://api.opensea.io/api/v1/asset/${address}/${tokenId}?force_update=true', headers={'X-API-KEY': os.environ['OPENSEA_API_KEY']})

    await awsRequester.close_connections()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(update_collection())
