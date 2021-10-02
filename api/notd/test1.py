import json
import logging
import os

import urllib.request
from core.http.basic_authentication import BasicAuthentication
from core.requester import Requester
from core.web3.eth_client import EthClientInterface, RestEthClient
from sqlalchemy.sql.expression import update
import asyncio



infuraAuth = BasicAuthentication(username='', password=os.environ['INFURA_PROJECT_SECRET'])
infuraRequester = Requester(headers={'authorization': f'Basic {infuraAuth.to_string()}'})
ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=infuraRequester)
ethClient = ethClient
with open('./contracts/IERC721Metadata.json') as contractJsonFile:
    erc721MetdataContractJson = json.load(contractJsonFile)
erc721MetdataContractAbi = erc721MetdataContractJson['abi']
erc721MetdataUriFunctionAbi = [internalAbi for internalAbi in erc721MetdataContractAbi if internalAbi['name'] == 'tokenURI'][0]
erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]

async def retrieve_token_metadata(registryAddress: str,tokenId: str):
    tokenMetadataUriResponse = await ethClient.call_function(toAddress=registryAddress, contractAbi=erc721MetdataContractAbi, functionAbi=erc721MetdataUriFunctionAbi, arguments={'tokenId': int(tokenId)})        
    with urllib.request.urlopen(tokenMetadataUriResponse[0]) as response:
        data = json.loads(response.read())
        metadataUrl = tokenMetadataUriResponse[0]
        imageUrl = data.get('image')
        name = data.get('name')
        description =  data.get('description')
        attributes = data.get('attributes')

        print(type(attributes))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(retrieve_token_metadata(registryAddress='0xFBB6684EbD6093989740e8ef3e7D57cf3813E5a4',tokenId='9991'))