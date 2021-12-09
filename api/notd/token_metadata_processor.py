import base64
import json
import logging
from typing import Dict
from json.decoder import JSONDecodeError
import urllib.parse

from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.s3_manager import S3Manager
from core.util import date_util
from core.web3.eth_client import EthClientInterface

from notd.model import RetrievedTokenMetadata

IPFS_PROVIDER_PREFIXES = [
    'https://gateway.pinata.cloud/ipfs/',
    'https://ipfs.foundation.app/ipfs/',
    'https://ipfs.io/ipfs/',
    'https://ipfs.infura.io/ipfs/',
    'https://niftylabs.mypinata.cloud/ipfs/',
    'https://time.mypinata.cloud/ipfs/',
    'https://robotos.mypinata.cloud/ipfs/',
]


class TokenDoesNotExistException(NotFoundException):
    pass


class TokenHasNoMetadataException(NotFoundException):
    pass

class TokenMetadataProcessor():

    def __init__(self, requester: Requester, ethClient: EthClientInterface, s3manager: S3Manager, bucketName: str):
        self.requester = requester
        self.ethClient = ethClient
        self.s3manager = s3manager
        self.bucketName = bucketName
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetdataUriFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'tokenURI'][0]
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]

    @staticmethod
    def _resolve_data(dataString: str, registryAddress: str, tokenId: str) -> Dict:
        tokenMetadataJson = None
        if dataString.startswith('data:application/json;base64,'):
            bse64String = dataString.replace('data:application/json;base64,', '', 1)
            tokenMetadataJson = base64.b64decode(bse64String.encode('utf-8')).decode('utf-8')
        elif dataString.startswith('data:application/json;utf8,'):
            tokenMetadataJson = dataString.replace('data:application/json;utf8,', '', 1)
        elif dataString.startswith('data:application/json;charset=utf-8,'):
            tokenMetadataJson = dataString.replace('data:application/json;charset=utf-8,', '', 1)
        elif dataString.startswith('data:application/json,'):
            tokenMetadataJson = dataString.replace('data:application/json,', '', 1)
        elif dataString.startswith('data:text/plain,'):
            tokenMetadataJson = dataString.replace('data:text/plain,', '', 1)
        else:
            logging.info(f'Failed to process data string: {dataString}')
            tokenMetadataDict = {}
        if tokenMetadataJson:
            # NOTE(krishan711): it's safe to decode something that'd either encoded or not encoded
            tokenMetadataJson = urllib.parse.unquote(tokenMetadataJson)
            try:
                tokenMetadataDict = json.loads(tokenMetadataJson)
            except JSONDecodeError as exception:
                logging.info(f'Failed to parse JSON for {registryAddress}/{tokenId}: {exception}')
                tokenMetadataDict = {}
        return tokenMetadataDict

    async def retrieve_token_metadata(self, registryAddress: str, tokenId: str) -> RetrievedTokenMetadata:
        if registryAddress == '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85':
            # TODO(krishan711): Implement special case for ENS
            raise TokenDoesNotExistException()
        if registryAddress == '0x06012c8cf97BEaD5deAe237070F9587f8E7A266d':
            # TODO(krishan711): Implement special case for cryptokitties
            raise TokenDoesNotExistException()
        if registryAddress == '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB':
            # TODO(krishan711): Implement special case for cryptopunks
            raise TokenDoesNotExistException()
        if registryAddress == '0x66018A2AC8F28f4d68d1F018680957F2F22528Da':
            # TODO(krishan711): Implement special case for etherland
            raise TokenDoesNotExistException()
        if registryAddress == '0xE22e1e620dffb03065CD77dB0162249c0c91bf01':
            # TODO(krishan711): Implement special case for bearxlabs
            raise TokenDoesNotExistException()
        if registryAddress in ('0x57E9a39aE8eC404C08f88740A9e6E306f50c937f', '0xFFF7F797213d7aE5f654f2bC91c071745843b5B9'):
            # TODO(krishan711): Implement special case for polkacity and Elephants for Africa (their contract seems broken)
            raise TokenDoesNotExistException()
        if registryAddress == '0x772Da237fc93ded712E5823b497Db5991CC6951e':
            # TODO(krishan711): Implement special case for Everdragons(their contract is unverified)
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
            defaultTokenMetadata = TokenHasNoMetadataException()
            return defaultTokenMetadata
        for ipfsProviderPrefix in IPFS_PROVIDER_PREFIXES:
            if tokenMetadataUri.startswith(ipfsProviderPrefix):
                tokenMetadataUri = tokenMetadataUri.replace(ipfsProviderPrefix, 'ipfs://')
        # NOTE(krishan711): save the url here before using ipfs gateways etc
        metadataUrl = tokenMetadataUri
        if tokenMetadataUri.startswith('ipfs://'):
            tokenMetadataUri = tokenMetadataUri.replace('ipfs://', 'https://ipfs.io/ipfs/')
        if not tokenMetadataUri:
            tokenMetadataDict = {}
        elif tokenMetadataUri.startswith('data:'):
            tokenMetadataDict = self._resolve_data(dataString=tokenMetadataUri, registryAddress=registryAddress, tokenId=tokenId)
        else:
            try:
                tokenMetadataResponse = await self.requester.get(url=tokenMetadataUri)
                tokenMetadataDict = tokenMetadataResponse.json()
                if isinstance(tokenMetadataDict, str):
                    tokenMetadataDict = json.loads(tokenMetadataDict)
            except Exception as exception:  # pylint: disable=broad-except
                logging.info(f'Failed to pull metadata from {metadataUrl}: {exception}')
                tokenMetadataDict = {}
        await self.s3manager.write_file(content=str.encode(json.dumps(tokenMetadataDict)), targetPath=f'{self.bucketName}/token-metadatas/{registryAddress}/{tokenId}/{date_util.datetime_from_now()}.json')
        description = tokenMetadataDict.get('description')
        if isinstance(description, list):
            if len(description) != 1:
                raise BadRequestException(f'description is an array with len != 1: {description}')
            description = description[0]
        retrievedTokenMetadata = RetrievedTokenMetadata(
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            imageUrl=tokenMetadataDict.get('image'),
            name=tokenMetadataDict.get('name'),
            description=description,
            attributes=tokenMetadataDict.get('attributes', []),
        )
        return retrievedTokenMetadata
