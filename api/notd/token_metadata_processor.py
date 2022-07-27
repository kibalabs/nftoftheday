import base64
import json
import urllib.parse
from json.decoder import JSONDecodeError
from typing import Any
from typing import Dict

from core import logging
from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.requester import ResponseException
from core.s3_manager import S3Manager
from core.util import date_util
from core.web3.eth_client import EthClientInterface
from pablo import PabloClient
from web3.main import Web3

from notd.model import GALLERY_COLLECTIONS
from notd.model import Collection
from notd.model import RetrievedTokenMetadata

IPFS_PROVIDER_PREFIXES = [
    'https://gateway.pinata.cloud/ipfs/',
    'https://ipfs.foundation.app/ipfs/',
    'https://ipfs.io/ipfs/',
    'https://ipfs.infura.io/ipfs/',
    'https://niftylabs.mypinata.cloud/ipfs/',
    'https://time.mypinata.cloud/ipfs/',
    'https://robotos.mypinata.cloud/ipfs/',
    'https://cloudflare-ipfs.com/ipfs/',
    'https://spriteclub.infura-ipfs.io/ipfs/',
]


class TokenDoesNotExistException(NotFoundException):
    pass


class TokenHasNoMetadataException(NotFoundException):
    pass

class TokenMetadataProcessor():

    def __init__(self, requester: Requester, ethClient: EthClientInterface, s3Manager: S3Manager, bucketName: str, pabloClient: PabloClient):
        self.requester = requester
        self.ethClient = ethClient
        self.s3Manager = s3Manager
        self.bucketName = bucketName
        self.pabloClient = pabloClient
        self.w3 = Web3()
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetadataContractJson = json.load(contractJsonFile)
        self.erc721MetadataContractAbi = erc721MetadataContractJson['abi']
        self.erc721MetadataUriFunctionAbi = [internalAbi for internalAbi in self.erc721MetadataContractAbi if internalAbi.get('name') == 'tokenURI'][0]
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetadataContractAbi if internalAbi.get('name') == 'name'][0]
        with open('./contracts/CryptoPunksMetadata.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.cryptoPunksContract = self.w3.eth.contract(address='0x16F5A35647D6F03D5D3da7b35409D65ba03aF3B2', abi=contractJson['abi'])
        self.cryptoPunksAttributesFunctionAbi = [internalAbi for internalAbi in self.cryptoPunksContract.abi if internalAbi.get('name') == 'punkAttributes'][0]
        self.cryptoPunksImageSvgFunctionAbi = [internalAbi for internalAbi in self.cryptoPunksContract.abi if internalAbi.get('name') == 'punkImageSvg'][0]
        with open('./contracts/IERC1155MetadataURI.json') as contractJsonFile:
            erc1155MetadataContractJson = json.load(contractJsonFile)
        self.erc1155MetadataContractAbi = erc1155MetadataContractJson['abi']
        self.erc1155MetadataUriFunctionAbi = [internalAbi for internalAbi in self.erc1155MetadataContractAbi if internalAbi.get('name') == 'uri'][0]
        #self.erc1155MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc1155MetadataContractAbi if internalAbi.get('name') == 'name'][0]
        with open('./contracts/IERC165.json') as contractJsonFile:
            erc165MetadataContractJson = json.load(contractJsonFile)
        self.erc165MetadataContractAbi = erc165MetadataContractJson['abi']
        self.erc165SupportInterfaceUriFunctionAbi = [internalAbi for internalAbi in self.erc165MetadataContractAbi if internalAbi.get('name') == 'supportsInterface'][0]

    @staticmethod
    def get_default_token_metadata(registryAddress: str, tokenId: str):
        return RetrievedTokenMetadata(
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=None,
            name=f'#{tokenId}',
            description=None,
            imageUrl=None,
            resizableImageUrl=None,
            animationUrl=None,
            youtubeUrl=None,
            backgroundColor=None,
            frameImageUrl=None,
            attributes=[],
        )

    @staticmethod
    def _resolve_data(dataString: str, registryAddress: str, tokenId: str) -> Dict:
        tokenMetadataJson = None
        if dataString.startswith('data:application/json;base64,'):
            bse64String = dataString.replace('data:application/json;base64,', '', 1)
            tokenMetadataJson = base64.b64decode(bse64String.encode('utf-8') + b'==').decode('utf-8', errors='ignore')
        elif dataString.startswith('data:application/json;utf8,'):
            tokenMetadataJson = dataString.replace('data:application/json;utf8,', '', 1)
        elif dataString.startswith('data:application/json;ascii,'):
            tokenMetadataJson = dataString.replace('data:application/json;ascii,', '', 1)
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
            # NOTE(krishan711): it's safe to decode something that's either encoded or not encoded
            tokenMetadataJson = urllib.parse.unquote(tokenMetadataJson)
            try:
                tokenMetadataDict = json.loads(tokenMetadataJson)
            except JSONDecodeError as exception:
                logging.info(f'Failed to parse JSON for {registryAddress}/{tokenId}: {exception}')
                tokenMetadataDict = {}
        return tokenMetadataDict

    @staticmethod
    async def _get_token_metadata_from_data(registryAddress: str, tokenId: str, metadataUrl: str, tokenMetadataDict: Dict[str, Any]) -> RetrievedTokenMetadata:
        name = tokenMetadataDict.get('name') or tokenMetadataDict.get('title') or f'#{tokenId}'
        description = tokenMetadataDict.get('description')
        if isinstance(description, list):
            description = description[0]
        imageUrl = tokenMetadataDict.get('image') or tokenMetadataDict.get('image_url') or tokenMetadataDict.get('imageUrl') or tokenMetadataDict.get('image_data')
        if isinstance(imageUrl, dict):
            imageDict = imageUrl
            imageUrl = imageDict.get('src')
            if not imageUrl:
                logging.error(f'Failed to extract imageUrl from {imageDict}')
        retrievedTokenMetadata = RetrievedTokenMetadata(
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            name=str(name).replace('\u0000', ''),
            description=str(description).replace('\u0000', '') if description else None,
            imageUrl=imageUrl,
            resizableImageUrl=None,
            animationUrl=tokenMetadataDict.get('animation_url') or tokenMetadataDict.get('animation'),
            youtubeUrl=tokenMetadataDict.get('youtube_url'),
            backgroundColor=tokenMetadataDict.get('background_color'),
            frameImageUrl=tokenMetadataDict.get('frame_image') or tokenMetadataDict.get('frame_image_url') or tokenMetadataDict.get('frameImage'),
            attributes=tokenMetadataDict.get('attributes', []),
        )
        return retrievedTokenMetadata

    async def retrieve_token_metadata(self, registryAddress: str, tokenId: str, collection: Collection) -> RetrievedTokenMetadata:
        if registryAddress == '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB':
            # NOTE(krishan711): special case for CryptoPunks
            attributesResponse = await self.ethClient.call_function(toAddress=self.cryptoPunksContract.address, contractAbi=self.cryptoPunksContract.abi, functionAbi=self.cryptoPunksAttributesFunctionAbi, arguments={'index': int(tokenId)})
            attributes = [{'trait_type': 'Accessory', 'value': attribute.strip()} for attribute in attributesResponse[0].split(',')]
            imageSvgResponse = await self.ethClient.call_function(toAddress=self.cryptoPunksContract.address, contractAbi=self.cryptoPunksContract.abi, functionAbi=self.cryptoPunksImageSvgFunctionAbi, arguments={'index': int(tokenId)})
            return RetrievedTokenMetadata(
                registryAddress=registryAddress,
                tokenId=tokenId,
                metadataUrl=None,
                name=f'#{tokenId}',
                description=None,
                imageUrl=imageSvgResponse[0],
                resizableImageUrl=None,
                animationUrl=None,
                youtubeUrl=None,
                backgroundColor=None,
                frameImageUrl=None,
                attributes=attributes,
            )
        if registryAddress == '0xd65c5D035A35F41f31570887E3ddF8c3289EB920':
            # TODO(krishan711): Implement special case for ETHTerrestrials
            raise TokenDoesNotExistException()
        if registryAddress == '0xAA6612F03443517ceD2Bdcf27958c22353ceeAb9':
            # TODO(krishan711): Implement special case for Bamboozlers
            raise TokenDoesNotExistException()
        if registryAddress == '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85':
            # TODO(krishan711): Implement special case for ENS
            raise TokenDoesNotExistException()
        if registryAddress == '0x06012c8cf97BEaD5deAe237070F9587f8E7A266d':
            # TODO(krishan711): Implement special case for cryptokitties
            raise TokenDoesNotExistException()
        if registryAddress in ('0x57E9a39aE8eC404C08f88740A9e6E306f50c937f', '0xFFF7F797213d7aE5f654f2bC91c071745843b5B9'):
            # TODO(krishan711): Implement special case for polkacity and Elephants for Africa (their contract seems broken)
            raise TokenDoesNotExistException()
        if registryAddress in ('0x772Da237fc93ded712E5823b497Db5991CC6951e', '0xE072AA2B0d39587A08813391e84495971A098084'):
            # TODO(krishan711): Implement special case for Everdragons, DISTXR (their contract is unverified)
            raise TokenDoesNotExistException()
        if registryAddress == '0xdF5d68D54433661b1e5e90a547237fFB0AdF6EC2':
            # TODO(krishan711): Implement special case for Arcona Digital Land (it's a really old contract)
            raise TokenDoesNotExistException()
        if not collection.doesSupportErc721 and not collection.doesSupportErc1155:
            logging.info(f'Contract does not support ERC721 or ERC1155: {registryAddress}')
            raise TokenDoesNotExistException()
        tokenMetadataUriResponse = None
        badRequestException = None
        if collection.doesSupportErc721:
            try:
                tokenMetadataUriResponse = (await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc721MetadataContractAbi, functionAbi=self.erc721MetadataUriFunctionAbi, arguments={'tokenId': int(tokenId)}))[0]
            except BadRequestException as exception:
                badRequestException = exception
        if collection.doesSupportErc1155:
            try:
                tokenMetadataUriResponse = (await self.ethClient.call_function(toAddress=registryAddress, contractAbi=self.erc1155MetadataContractAbi, functionAbi=self.erc1155MetadataUriFunctionAbi, arguments={'id': int(tokenId)}))[0]
            except BadRequestException as exception:
                badRequestException = exception
        if badRequestException is not None:
            if 'URI query for nonexistent token' in badRequestException.message:
                raise TokenDoesNotExistException()
            if 'execution reverted' in badRequestException.message:
                raise TokenDoesNotExistException()
            if 'out of gas' in badRequestException.message:
                raise TokenDoesNotExistException()
            if 'stack limit reached' in badRequestException.message:
                raise TokenDoesNotExistException()
            if 'Maybe the method does not exist on this contract' in badRequestException.message:
                raise TokenDoesNotExistException()
            if 'value could not be decoded as valid UTF8' in badRequestException.message:
                raise TokenDoesNotExistException()
            raise badRequestException
        if tokenMetadataUriResponse.startswith('https://api.opensea.io/api/v1/metadata/'):
            tokenMetadataUri = f'https://api.opensea.io/api/v1/metadata/{registryAddress}/{tokenId}'
        else:
            hexId = hex(int(tokenId)).replace('0x', '').rjust(64, '0')
            tokenMetadataUri = tokenMetadataUriResponse.replace('0x{id}', hexId).replace('{id}', hexId).replace('\x00', '')
        if len(tokenMetadataUri.strip()) == 0:
            tokenMetadataUri = None
        if not tokenMetadataUri:
            raise TokenHasNoMetadataException()
        for ipfsProviderPrefix in IPFS_PROVIDER_PREFIXES:
            if tokenMetadataUri.startswith(ipfsProviderPrefix):
                tokenMetadataUri = tokenMetadataUri.replace(ipfsProviderPrefix, 'ipfs://')
        # NOTE(krishan711): save the url here before using ipfs gateways etc
        metadataUrl = tokenMetadataUri
        if tokenMetadataUri.startswith('ipfs://'):
            tokenMetadataUri = tokenMetadataUri.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/')
        if not tokenMetadataUri:
            tokenMetadataDict = {}
        elif tokenMetadataUri.startswith('data:'):
            tokenMetadataDict = self._resolve_data(dataString=tokenMetadataUri, registryAddress=registryAddress, tokenId=tokenId)
        else:
            try:
                tokenMetadataResponse = await self.requester.get(url=tokenMetadataUri, timeout=10)
                tokenMetadataDict = tokenMetadataResponse.json()
                if registryAddress == '0x8Cef7873425D94E2588f10A08428280a2e6338e3':
                    tokenMetadataDict = tokenMetadataDict[0]
                if tokenMetadataDict is None:
                    raise Exception('Empty response')
                if isinstance(tokenMetadataDict, (bool, int, float)):
                    raise Exception(f'Invalid response: {tokenMetadataDict}')
                if isinstance(tokenMetadataDict, str):
                    tokenMetadataDict = json.loads(tokenMetadataDict)
            except ResponseException as exception:
                errorMessage = '' if exception.message.strip().startswith('<!DOCTYPE html') or exception.message.strip().startswith('<html') else exception.message
                logging.info(f'Response error while pulling metadata from {metadataUrl}: {exception.statusCode} {errorMessage}')
                tokenMetadataDict = {}
            except Exception as exception:  # pylint: disable=broad-except
                logging.info(f'Failed to process metadata from {metadataUrl}: {type(exception)} {str(exception)}')
                tokenMetadataDict = {}
        await self.s3Manager.write_file(content=str.encode(json.dumps(tokenMetadataDict)), targetPath=f'{self.bucketName}/token-metadatas/{registryAddress}/{tokenId}/{date_util.datetime_from_now()}.json')
        retrievedTokenMetadata = await self._get_token_metadata_from_data(registryAddress=registryAddress, tokenId=tokenId, metadataUrl=metadataUrl, tokenMetadataDict=tokenMetadataDict)
        if registryAddress in GALLERY_COLLECTIONS and retrievedTokenMetadata.imageUrl:
            image = await self.pabloClient.upload_image_url(url=retrievedTokenMetadata.imageUrl)
            retrievedTokenMetadata.resizableImageUrl = image.resizableUrl
        return retrievedTokenMetadata
