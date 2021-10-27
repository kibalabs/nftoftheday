import json
import logging
from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.web3.eth_client import EthClientInterface

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

    async def retrieve_token_metadata(self, registryAddress: str,tokenId: str) -> RetrievedTokenMetadata:
        if registryAddress == '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85':
            # TODO(krishan711): Implement special case for ENS
            raise TokenDoesNotExistException()
        if registryAddress == '0x06012c8cf97BEaD5deAe237070F9587f8E7A266d':
            # TODO(krishan711): Implement special case for cryptokitties
            raise TokenDoesNotExistException()
        if registryAddress == '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB':
            # TODO(krishan711): Implement special case for cryptopunks
            raise TokenDoesNotExistException()
        try:
            tokenMetadataUriResponse = await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetdataUriFunctionAbi, arguments={'tokenId': int(tokenId)})
        except BadRequestException as exception:
            if 'URI query for nonexistent token' in exception.message:
                raise TokenDoesNotExistException()
            if 'execution reverted' in exception.message:
                raise TokenDoesNotExistException()
            if 'out of gas' in exception.message:
                raise TokenDoesNotExistException()
            raise exception
        tokenMetadataUri = tokenMetadataUriResponse[0].replace('\x00', '')
        if len(tokenMetadataUri.strip()) == 0:
            tokenMetadataUri = None
        if not tokenMetadataUri:
            raise TokenHasNoMetadataException()
        if tokenMetadataUri.startswith('https://gateway.pinata.cloud/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://gateway.pinata.cloud/ipfs/', 'ipfs://')
        if tokenMetadataUri.startswith('https://ipfs.foundation.app/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://ipfs.foundation.app/ipfs/', 'ipfs://')
        if tokenMetadataUri.startswith('https://ipfs.io/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://ipfs.io/ipfs/', 'ipfs://')
        if tokenMetadataUri.startswith('https://ipfs.infura.io/ipfs/'):
            tokenMetadataUri = tokenMetadataUri.replace('https://ipfs.infura.io/ipfs/', 'ipfs://')
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
                if isinstance(tokenMetadataResponseJson, str):
                    tokenMetadataResponseJson = json.loads(tokenMetadataResponseJson)
            except Exception as exception:  # pylint: disable=broad-except
                logging.info(f'Failed to pull metadata from {metadataUrl}: {exception}')
                tokenMetadataResponseJson = {}
        description = tokenMetadataResponseJson.get('description')
        if isinstance(description, list):
            if len(description) != 1:
                raise BadRequestException(f'description is an array with len != 1: {description}')
            description = description[0]
        retrievedTokenMetadata = RetrievedTokenMetadata(
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            imageUrl=tokenMetadataResponseJson.get('image'),
            name=tokenMetadataResponseJson.get('name'),
            description=description,
            attributes=tokenMetadataResponseJson.get('attributes', []),
        )
        return retrievedTokenMetadata
