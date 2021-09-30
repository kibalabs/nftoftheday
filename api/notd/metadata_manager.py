import json

import urllib.request
from core.web3.eth_client import EthClientInterface

_EMPTY_STRING = '_EMPTY_STRING'

class MetadataManager():

    def __init__(self, ethClient: EthClientInterface):
        self.ethClient = ethClient
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetdataUriFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'tokenURI'][0]
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]

    async def retrieve_token_metadata(self,registryAddress: str,tokenId: int):
        tokenMetadataUriResponse = await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetdataUriFunctionAbi, arguments={'tokenId': int(tokenId)})
        with urllib.request.urlopen(tokenMetadataUriResponse[0]) as response:
            data = json.loads(response.read())
            metadataUrl = tokenMetadataUriResponse[0]
            imageUrl = data.get('image',_EMPTY_STRING)
            name = data.get('name',_EMPTY_STRING)
            description =  data.get('description',_EMPTY_STRING)
            attributes = data.get('attributes',_EMPTY_STRING)

        return metadataUrl, imageUrl, name, description, attributes
