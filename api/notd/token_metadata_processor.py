import base64
import json
import math
import typing
import urllib.parse
from json.decoder import JSONDecodeError
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional

from core import logging
from core.exceptions import BadRequestException
from core.exceptions import InternalServerErrorException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.requester import ResponseException
from core.util.typing_util import JSON
from core.util.typing_util import JSON1
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


class TokenMetadataUnprocessableException(NotFoundException):
    pass


class TokenMetadataProcessor():

    def __init__(self, requester: Requester, ethClient: EthClientInterface, pabloClient: PabloClient):
        self.requester = requester
        self.ethClient = ethClient
        self.pabloClient = pabloClient
        self.w3 = Web3()
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetadataContractJson = json.load(contractJsonFile)
        self.erc721MetadataContractAbi = erc721MetadataContractJson['abi']
        self.erc721MetadataUriFunctionAbi = [internalAbi for internalAbi in self.erc721MetadataContractAbi if internalAbi.get('name') == 'tokenURI'][0]
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetadataContractAbi if internalAbi.get('name') == 'name'][0]
        with open('./contracts/CryptoPunksMetadata.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.cryptoPunksContract = self.w3.eth.contract(address='0x16F5A35647D6F03D5D3da7b35409D65ba03aF3B2', abi=contractJson['abi'])  # type: ignore[call-overload]
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
    def get_default_token_metadata(registryAddress: str, tokenId: str) -> RetrievedTokenMetadata:
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
    def _resolve_data(dataString: str, registryAddress: str, tokenId: str) -> JSON:
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
    def _clean_potential_ipfs_url(ipfsUrl: Optional[str]) -> Optional[str]:
        return ipfsUrl.replace('ipfs://ipfs/', 'ipfs://').rstrip('/') if ipfsUrl else None

    def _clean_potential_url(self, url: Optional[JSON1]) -> Optional[str]:
        if not url:
            return None
        if not isinstance(url, str):
            if isinstance(url, list) and len(url) > 0:
                url = url[0]  # type: ignore[assignment]
            elif isinstance(url, dict):
                imageDict = url
                url = imageDict.get('src')
                if not url:
                    logging.error(f'Failed to extract url from dict: {imageDict}')
            else:
                url = str(url)
        return self._clean_potential_ipfs_url(ipfsUrl=url)  # type: ignore[arg-type]

    @staticmethod
    def _clean_attribute(attribute: Dict[str, JSON1]) -> Dict[str, JSON1]:
        for key, value in attribute.items():
            if isinstance(value, float) and math.isnan(value):
                attribute[key] = 'NaN'
        return attribute

    def _clean_attributes(self, attributes: List[Dict[str, JSON1]]) -> List[Dict[str, JSON1]]:
        cleanedAttributes: List[Dict[str, JSON1]] = []
        for attribute in attributes:
            if not attribute:
                continue
            if isinstance(attribute, list):  # type: ignore[unreachable]
                cleanedAttributes += self._clean_attributes(attribute)  # type: ignore[unreachable]
            elif isinstance(attribute, dict):
                cleanedAttributes.append(self._clean_attribute(attribute))
            else:
                logging.info(f'Unknown attribute instance type: {attribute}')  # type: ignore[unreachable]
        return cleanedAttributes

    def _get_token_metadata_from_data(self, registryAddress: str, tokenId: str, metadataUrl: str, tokenMetadataDict: Mapping[str, JSON1]) -> RetrievedTokenMetadata:
        name = tokenMetadataDict.get('name') or tokenMetadataDict.get('title') or f'#{tokenId}'
        description: Optional[str] = tokenMetadataDict.get('description')  # type: ignore[assignment]
        if isinstance(description, list) and len(description) > 0:  # type: ignore[unreachable]
            description = description[0]  # type: ignore[unreachable]
        imageUrl: Optional[str] = tokenMetadataDict.get('image') or tokenMetadataDict.get('image_url') or tokenMetadataDict.get('imageUrl') or tokenMetadataDict.get('image_data')  # type: ignore[assignment]
        animationUrl: Optional[str] = tokenMetadataDict.get('animation_url') or tokenMetadataDict.get('animation')  # type: ignore[assignment]
        youtubeUrl: Optional[str] = tokenMetadataDict.get('youtube_url')  # type: ignore[assignment]
        frameImageUrl: Optional[str] = tokenMetadataDict.get('frame_image') or tokenMetadataDict.get('frame_image_url') or tokenMetadataDict.get('frameImage')  # type: ignore[assignment]
        attributes: JSON = tokenMetadataDict.get('attributes') or []  # type: ignore[assignment]
        if isinstance(attributes, list):
            attributes = self._clean_attributes(attributes)  # type: ignore[assignment, arg-type]
        retrievedTokenMetadata = RetrievedTokenMetadata(
            registryAddress=registryAddress,
            tokenId=tokenId,
            metadataUrl=metadataUrl,
            name=str(name).replace('\u0000', '').encode('utf-8', 'namereplace').decode(),
            description=str(description).replace('\u0000', '').encode('utf-8', 'namereplace').decode() if description else None,
            imageUrl=self._clean_potential_url(url=imageUrl),
            resizableImageUrl=None,
            animationUrl=self._clean_potential_url(url=animationUrl),
            youtubeUrl=self._clean_potential_url(url=youtubeUrl),
            frameImageUrl=self._clean_potential_url(url=frameImageUrl),
            backgroundColor=str(tokenMetadataDict['background_color']) if tokenMetadataDict.get('background_color') else None,
            attributes=attributes,
        )
        return retrievedTokenMetadata

    async def retrieve_token_metadata(self, registryAddress: str, tokenId: str, collection: Collection) -> RetrievedTokenMetadata:
        if registryAddress == '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB':
            # NOTE(krishan711): special case for CryptoPunks
            attributesResponse = await self.ethClient.call_function(toAddress=self.cryptoPunksContract.address, contractAbi=self.cryptoPunksContract.abi, functionAbi=self.cryptoPunksAttributesFunctionAbi, arguments={'index': int(tokenId)})
            attributes: JSON = [{'trait_type': 'Accessory', 'value': attribute.strip()} for attribute in attributesResponse[0].split(',')]
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
            raise TokenMetadataUnprocessableException()
        if registryAddress == '0xAA6612F03443517ceD2Bdcf27958c22353ceeAb9':
            # TODO(krishan711): Implement special case for Bamboozlers
            raise TokenMetadataUnprocessableException()
        if registryAddress == '0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85':
            # TODO(krishan711): Implement special case for ENS
            raise TokenMetadataUnprocessableException()
        if registryAddress == '0x06012c8cf97BEaD5deAe237070F9587f8E7A266d':
            # TODO(krishan711): Implement special case for cryptokitties
            raise TokenMetadataUnprocessableException()
        if registryAddress in ('0x57E9a39aE8eC404C08f88740A9e6E306f50c937f', '0xFFF7F797213d7aE5f654f2bC91c071745843b5B9'):
            # TODO(krishan711): Implement special case for polkacity and Elephants for Africa (their contract seems broken)
            raise TokenMetadataUnprocessableException()
        if registryAddress in ('0x772Da237fc93ded712E5823b497Db5991CC6951e', '0xE072AA2B0d39587A08813391e84495971A098084'):
            # TODO(krishan711): Implement special case for Everdragons, DISTXR (their contract is unverified)
            raise TokenMetadataUnprocessableException()
        if registryAddress == '0xdF5d68D54433661b1e5e90a547237fFB0AdF6EC2':
            # TODO(krishan711): Implement special case for Arcona Digital Land (it's a really old contract)
            raise TokenMetadataUnprocessableException()
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
            if badRequestException.message:
                if 'URI query for nonexistent token' in badRequestException.message:
                    raise TokenDoesNotExistException(message='URI query for nonexistent token')
                if 'execution reverted' in badRequestException.message:
                    raise TokenMetadataUnprocessableException(message='execution reverted')
                if 'out of gas' in badRequestException.message:
                    raise TokenMetadataUnprocessableException(message='out of gas')
                if 'stack limit reached' in badRequestException.message:
                    raise TokenMetadataUnprocessableException(message='stack limit reached')
                if 'Maybe the method does not exist on this contract' in badRequestException.message:
                    raise TokenMetadataUnprocessableException(message='Maybe the method does not exist on this contract')
                if 'value could not be decoded as valid UTF8' in badRequestException.message:
                    raise TokenMetadataUnprocessableException(message='value could not be decoded as valid UTF8')
            raise badRequestException
        tokenMetadataUri: Optional[str] = None
        if tokenMetadataUriResponse:
            if tokenMetadataUriResponse.startswith('https://api.opensea.io/api/v1/metadata/'):
                tokenMetadataUri = f'https://api.opensea.io/api/v1/metadata/{registryAddress}/{tokenId}'
            else:
                hexId = hex(int(tokenId)).replace('0x', '').rjust(64, '0')
                tokenMetadataUri = typing.cast(str, tokenMetadataUriResponse).replace('0x{id}', hexId).replace('{id}', hexId).replace('\x00', '')
        if tokenMetadataUri and len(tokenMetadataUri.strip()) == 0:
            tokenMetadataUri = None
        if not tokenMetadataUri:
            raise TokenMetadataUnprocessableException()
        for ipfsProviderPrefix in IPFS_PROVIDER_PREFIXES:
            if tokenMetadataUri.startswith(ipfsProviderPrefix):
                tokenMetadataUri = tokenMetadataUri.replace(ipfsProviderPrefix, 'ipfs://')
        tokenMetadataUri = self._clean_potential_ipfs_url(tokenMetadataUri)
        # NOTE(krishan711): save the url here before using ipfs gateways etc
        metadataUrl = typing.cast(str, tokenMetadataUri)
        if tokenMetadataUri and tokenMetadataUri.startswith('ipfs://'):
            tokenMetadataUri = tokenMetadataUri.replace('ipfs://', 'https://pablo-images.kibalabs.com/v1/ipfs/')
        tokenMetadataDict: JSON = {}
        if not tokenMetadataUri:
            tokenMetadataDict = {}
        elif tokenMetadataUri.startswith('data:'):
            tokenMetadataDict = self._resolve_data(dataString=tokenMetadataUri, registryAddress=registryAddress, tokenId=tokenId)
        else:
            try:
                tokenMetadataResponse = await self.requester.get(url=tokenMetadataUri, timeout=10)
                tokenMetadataDict = tokenMetadataResponse.json()
                if tokenMetadataDict is None:
                    raise InternalServerErrorException('Empty response')
                if isinstance(tokenMetadataDict, (bool, int, float)):
                    raise InternalServerErrorException(f'Invalid response: {tokenMetadataDict}')
                if isinstance(tokenMetadataDict, str):
                    tokenMetadataDict = json.loads(tokenMetadataDict)
            except ResponseException as exception:
                errorMessage = '' if exception.message and (exception.message.strip().startswith('<!DOCTYPE html') or exception.message.strip().startswith('<html')) else exception.message
                logging.info(f'Response error while pulling metadata from {metadataUrl}: {exception.statusCode} {errorMessage}')
                tokenMetadataDict = {}
            except Exception as exception:  # pylint: disable=broad-except
                logging.info(f'Failed to process metadata from {metadataUrl}: {type(exception)} {str(exception)}')
                tokenMetadataDict = {}
        if isinstance(tokenMetadataDict, list):
            tokenMetadataDict = tokenMetadataDict[0] if len(tokenMetadataDict) > 0 else {}  # type: ignore[assignment]
        if not isinstance(tokenMetadataDict, dict):
            return self.get_default_token_metadata(registryAddress=registryAddress, tokenId=tokenId)
        retrievedTokenMetadata = self._get_token_metadata_from_data(registryAddress=registryAddress, tokenId=tokenId, metadataUrl=metadataUrl, tokenMetadataDict=tokenMetadataDict)
        if registryAddress in GALLERY_COLLECTIONS and retrievedTokenMetadata.imageUrl:
            try:
                image = await self.pabloClient.upload_image_url(url=retrievedTokenMetadata.imageUrl)
                retrievedTokenMetadata.resizableImageUrl = image.resizableUrl
            except BadRequestException as exception:
                # TODO(krishan711): this is ignoring "unsupported image format", find nicer way to ignore only this error
                logging.info(f'Skipping resizing image due to: {exception}')
        return retrievedTokenMetadata
