import json
import logging
from core.requester import Requester
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
        tokenMetadataUriResponse = await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetdataUriFunctionAbi, arguments={'tokenId': int(tokenId)})
        tokenMetadataUri = tokenMetadataUriResponse[0]
        metadataUrl = tokenMetadataUri
        if tokenMetadataUri.startswith('ipfs://'):
            tokenMetadataUri = tokenMetadataUri.replace('ipfs://', 'https://ipfs.io/ipfs/')
        try:
            tokenMetadataResponse = await self.requester.get(url=tokenMetadataUri)
            tokenMetadataResponseJson = tokenMetadataResponse.json()
        except Exception as exception:
            logging.info(f'Failed to pull metadata from {metadataUrl}: {exception}')
            tokenMetadataResponseJson = {}
        imageUrl = tokenMetadataResponseJson.get('image')
        name = tokenMetadataResponseJson.get('name')
        description = tokenMetadataResponseJson.get('description')
        attributes = tokenMetadataResponseJson.get('attributes', [])
        retrievedTokenMetadata = RetrievedTokenMetadata(
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            imageUrl=imageUrl,
            name=name,
            description=description,
            attributes=attributes,
        )
        return retrievedTokenMetadata
