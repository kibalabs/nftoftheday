import json
import logging
import os
import urllib.request

from web3 import Web3

from notd.model import TokenMetadata

_EMPTY_STRING = '_EMPTY_STRING'
w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}'))

def retrieve_token_metadata(registryAddress: str,tokenId:int):
    with open('./contracts/IERC721Metadata.json') as contractJsonFile:
        erc721MetdataContractJson = json.load(contractJsonFile)
        erc721MetdataContractAbi = erc721MetdataContractJson['abi']
    contract = w3.eth.contract(registryAddress,abi=erc721MetdataContractAbi)
    url = contract.functions.tokenURI(tokenId).call()
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
        metadataUrl = url
        imageUrl = data.get('image',_EMPTY_STRING)
        name = data.get('name',_EMPTY_STRING)
        description =  data.get('description',_EMPTY_STRING)
        attributes = data.get('attributes',_EMPTY_STRING)

    return TokenMetadata(
        registryAddress=registryAddress,
        tokenId=tokenId,
        metadataUrl=metadataUrl,
        imageUrl=imageUrl,
        name=name,
        description=description,
        attributes=attributes)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    retrieve_token_metadata() #pylint: disable = no-value-for-parameter
