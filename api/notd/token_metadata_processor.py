import json
import logging

from core.requester import Requester
from core.web3.eth_client import EthClientInterface
from core.exceptions import BadRequestException, NotFoundException

from notd.model import RetrievedTokenMetadata


class TokenDoesNotExistException(NotFoundException):
    pass


class TokenHasNoMetadataException(NotFoundException):
    pass


class TokenMetadataProcessor():

    def __init__(self, requester: Requester, ethClient: EthClientInterface):
        self.requester = requester
        self.ethClient = ethClient
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetdataUriFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'tokenURI'][0]
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]

    async def retrieve_token_metadata(self,registryAddress: str,tokenId: str) -> RetrievedTokenMetadata:
        try:
            tokenMetadataUriResponse = await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetdataUriFunctionAbi, arguments={'tokenId': int(tokenId)})
        except BadRequestException as exception:
            if 'URI query for nonexistent token' in exception.message:
                raise TokenDoesNotExistException()
            raise exception
        tokenMetadataUri = tokenMetadataUriResponse[0]
        if len(tokenMetadataUri.strip()) == 0:
            tokenMetadataUri = None
        if not tokenMetadataUri:
            raise TokenHasNoMetadataException()
        if tokenMetadataUri.startswith('https://gateway.pinata.cloud/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://gateway.pinata.cloud/ipfs/', 'ipfs://')
        if tokenMetadataUri.startswith('https://ipfs.foundation.app/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://ipfs.foundation.app/ipfs/', 'ipfs://')
        if tokenMetadataUri.startswith('https://niftylabs.mypinata.cloud/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://niftylabs.mypinata.cloud/ipfs/', 'ipfs://')
        if tokenMetadataUri.startswith('https://time.mypinata.cloud/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://time.mypinata.cloud/ipfs/', 'ipfs://')
        if tokenMetadataUri.startswith('https://robotos.mypinata.cloud/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://robotos.mypinata.cloud/ipfs/', 'ipfs://')
        # NOTE(krishan711): save the url here before using ipfs gateways etc
        metadataUrl = tokenMetadataUri
        if tokenMetadataUri.startswith('ipfs://'):
            tokenMetadataUri = tokenMetadataUri.replace('ipfs://', 'https://ipfs.io/ipfs/')
        if not tokenMetadataUri:
            tokenMetadataResponseJson = {}
        elif tokenMetadataUri.startswith('data:'):
            # TODO(krishan711): parse the data here
            tokenMetadataResponseJson = {}
        else:
            try:
                tokenMetadataResponse = await self.requester.get(url=tokenMetadataUri)
                tokenMetadataResponseJson = tokenMetadataResponse.json()
            except Exception as exception:
                logging.info(f'Failed to pull metadata from {metadataUrl}: {exception}')
                tokenMetadataResponseJson = {}
        retrievedTokenMetadata = RetrievedTokenMetadata(
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            imageUrl=tokenMetadataResponseJson.get('image'),
            name=tokenMetadataResponseJson.get('name'),
            description=tokenMetadataResponseJson.get('description'),
            attributes=tokenMetadataResponseJson.get('attributes', []),
        )
        return retrievedTokenMetadata
