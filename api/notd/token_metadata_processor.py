import json
import urllib.request

from core.requester import Requester
from core.util import date_util
from core.web3.eth_client import EthClientInterface

from notd.model import RetrievedTokenMetadata


class TokenMetadataProcessor():

    def __init__(self, requester: Requester, ethClient: EthClientInterface):
        self.requester = requester
        self.ethClient = ethClient
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetdataUriFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'tokenURI'][0]
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]

    async def retrieve_token_metadata(self,registryAddress: str,tokenId: str):
        createdDate = date_util.datetime_from_now()
        updatedDate = createdDate
        tokenMetadataUriResponse = await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetdataUriFunctionAbi, arguments={'tokenId': int(tokenId)})

        if tokenMetadataUriResponse[0][:4] == 'ipfs':
            tokenMetadataUriResponse[0] = tokenMetadataUriResponse[0].replace('ipfs://','https://ipfs.io/ipfs/')
        try:
            with urllib.request.urlopen(tokenMetadataUriResponse[0]) as response:
                data = json.loads(response.read())
                metadataUrl = tokenMetadataUriResponse[0]
                imageUrl = data.get('image')
                name = data.get('name')
                description =  data.get('description')
                attributes = data.get('attributes')

            return RetrievedTokenMetadata(
            createdDate=createdDate,
            updatedDate=updatedDate,
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            imageUrl=imageUrl,
            name=name,
            description=description,
            attributes=attributes
            )
        except: # pylint: disable=broad-except
            pass
