import json

from core.exceptions import NotFoundException
from core.requester import Requester
from core.web3.eth_client import EthClientInterface

from notd.model import RegistryToken


class TokenClient:

    def __init__(self, requester: Requester, ethClient: EthClientInterface):
        self.requester = requester
        self.ethClient = ethClient
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetdataUriFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'tokenURI'][0]
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]

    async def retrieve_registry_token(self, registryAddress: str, tokenId: str) -> RegistryToken:
        tokenMetadataUriResponse = await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetdataUriFunctionAbi, arguments={'tokenId': int(tokenId)})
        tokenMetadataUri = tokenMetadataUriResponse[0]
        if not tokenMetadataUri:
            raise NotFoundException()
        tokenMetadataResponse = await self.requester.get(url=tokenMetadataUri)
        tokenMetadataResponseJson = tokenMetadataResponse.json()
        tokenMetadataNameResponse = await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetadataNameFunctionAbi)
        collectionName = tokenMetadataNameResponse[0]
        registryToken = RegistryToken(
            registryAddress=registryAddress,
            tokenId=tokenId,
            name=tokenMetadataResponseJson['name'] or f"{collectionName} #{tokenId}",
            imageUrl=tokenMetadataResponseJson['image'],
            openSeaUrl=f"https://opensea.io/assets/{registryAddress}/{tokenId}?ref=0x18090cda49b21deaffc21b4f886aed3eb787d032",
            externalUrl=tokenMetadataResponseJson['external_url'],
            lastSaleDate=None,
            lastSalePrice=None,
            collectionName=collectionName,
            collectionImageUrl=None,
            collectionOpenSeaUrl=None,
            collectionExternalUrl=f'https://etherscan.io/address/{registryAddress}',
        )
        return registryToken
