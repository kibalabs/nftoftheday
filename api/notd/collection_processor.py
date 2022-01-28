import asyncio
import json
import logging

from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.requester import ResponseException
from core.web3.eth_client import EthClientInterface
from core.s3_manager import S3Manager
from core.util import date_util
from httpx import ReadTimeout

from notd.model import RetrievedCollection

_INTERFACE_ID_ERC721 = '0x5b5e139f'
_INTERFACE_ID_ERC1155 = '0xd9b67a26'

class CollectionDoesNotExist(NotFoundException):
    pass

class CollectionProcessor:

    def __init__(self, requester: Requester, ethClient: EthClientInterface, openseaApiKey: str, s3manager: S3Manager, bucketName: str):
        self.requester = requester
        self.ethClient = ethClient
        self.openseaApiKey = openseaApiKey
        self.s3manager = s3manager
        self.bucketName = bucketName
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]
        self.erc721MetadataSymbolFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'symbol'][0]
        with open('./contracts/IERC1155MetadataURI.json') as contractJsonFile:
            erc1155MetadataContractJson = json.load(contractJsonFile)
        self.erc1155MetadataContractAbi = erc1155MetadataContractJson['abi']
        self.erc1155MetadataUriFunctionAbi = [internalAbi for internalAbi in self.erc1155MetadataContractAbi if internalAbi.get('name') == 'uri'][0]
        with open('./contracts/IERC165.json') as contractJsonFile:
            erc165MetadataContractJson = json.load(contractJsonFile)
        self.erc165MetadataContractAbi = erc165MetadataContractJson['abi']
        self.erc165SupportInterfaceUriFunctionAbi = [internalAbi for internalAbi in self.erc165MetadataContractAbi if internalAbi.get('name') == 'supportsInterface'][0]
        with open('./contracts/ContractMetadata.json') as contractJsonFile:
            contractMetadataJson = json.load(contractJsonFile)
        self.contractAbi = contractMetadataJson['abi']
        self.contractUriFunctionAbi = [internalAbi for internalAbi in self.contractAbi if internalAbi['name'] == 'contractURI'][0]

    async def retrieve_collection(self, address: str) -> RetrievedCollection:
        try:
            doesSupportErc721Response = await self.ethClient.call_function(toAddress=address, contractAbi=self.erc165MetadataContractAbi, functionAbi=self.erc165SupportInterfaceUriFunctionAbi, arguments={'interfaceId': _INTERFACE_ID_ERC721})
            doesSupportErc721 = doesSupportErc721Response[0]
        except BadRequestException as exception:
            doesSupportErc721 = False
        try:
            doesSupportErc1155Response = await self.ethClient.call_function(toAddress=address, contractAbi=self.erc165MetadataContractAbi, functionAbi=self.erc165SupportInterfaceUriFunctionAbi, arguments={'interfaceId': _INTERFACE_ID_ERC1155})
            doesSupportErc1155 = doesSupportErc1155Response[0]
        except BadRequestException as exception:
            doesSupportErc1155 = False
        try:
            tokenMetadataNameResponse = await self.ethClient.call_function(toAddress=address, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetadataNameFunctionAbi)
            collectionName = tokenMetadataNameResponse[0]
        except BadRequestException as exception:
            collectionName = None
        try:
            tokenMetadataSymbolResponse = await self.ethClient.call_function(toAddress=address, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetadataSymbolFunctionAbi)
            collectionSymbol = tokenMetadataSymbolResponse[0]
        except BadRequestException:
            collectionSymbol = None
        try:
            contractUriResponse = await self.ethClient.call_function(toAddress=address, contractAbi=self.contractAbi, functionAbi=self.contractUriFunctionAbi)
            contractMetadataUri = contractUriResponse[0]
        except BadRequestException:
            contractMetadataUri = None
        print(contractMetadataUri)
        if contractMetadataUri is not None and bool(contractMetadataUri):
            if contractMetadataUri.startswith('ipfs://'):
                contractMetadataUri = contractMetadataUri.replace('ipfs://', 'https://ipfs.io/ipfs/')
            if "{address}" in contractMetadataUri:
                contractMetadataUri = contractMetadataUri.replace('{address}', address)
            contractMetadataUriResponse = await self.requester.get(url=contractMetadataUri)
            collectionMetadata = contractMetadataUriResponse.json()
            if isinstance(collectionMetadata, str):
                collectionMetadata = json.loads(collectionMetadata)
            await self.s3manager.write_file(content=str.encode(json.dumps(collectionMetadata)), targetPath=f'{self.bucketName}/collection-metadatas/{address}/{date_util.datetime_from_now()}.json')
        else:
            collectionMetadata = None
        openseaResponse = None
        retryCount = 0
        while not openseaResponse:
            try:
                openseaResponse = await self.requester.get(url=f'https://api.opensea.io/api/v1/asset_contract/{address}', headers={"X-API-KEY": self.openseaApiKey})
            except ResponseException as exception:
                if exception.statusCode == 404:
                    raise CollectionDoesNotExist()
                if retryCount >= 3 or (exception.statusCode < 500 and exception.statusCode != 429):
                    break
                logging.info(f'Retrying due to: {str(exception)}')
                await asyncio.sleep(1.5)
            except ReadTimeout as exception:
                if retryCount >= 3:
                    break
                logging.info(f'Retrying due to: {str(exception)}')
                await asyncio.sleep(1.5)
            retryCount += 1
        openseaCollection = openseaResponse.json().get('collection') if openseaResponse else {}
        if openseaCollection is None:
            logging.info(f'Failed to load collection from opensea: {address}')
            openseaCollection = {}
        name = collectionName
        symbol = collectionSymbol
        description = None
        imageUrl = None
        twitterUsername = None
        instagramUsername = None
        wikiUrl = None
        openseaSlug = None
        url = None
        discordUrl = None
        bannerImageUrl = None
        if collectionMetadata:
            name = name or collectionMetadata.get('name')
            symbol = symbol or collectionMetadata.get('symbol')
            description = collectionMetadata.get('description')
            imageUrl = collectionMetadata.get('image')
            twitterUsername = collectionMetadata.get('twitterUsername')
            instagramUsername = collectionMetadata.get('instagramUsername')
            wikiUrl = collectionMetadata.get('wikiUrl')
            openseaSlug = collectionMetadata.get('openseaSlug')
            url = collectionMetadata.get('external_link')
            discordUrl = collectionMetadata.get('discord_url')
            bannerImageUrl = collectionMetadata.get('bannerImageUrl')
        if openseaCollection:
            name = name or openseaCollection.get('name')
            symbol = symbol or openseaCollection.get('symbol')
            description = description or openseaCollection.get('description')
            imageUrl = imageUrl or openseaCollection.get('image_url')
            twitterUsername = twitterUsername or openseaCollection.get('twitter_username')
            instagramUsername = instagramUsername or openseaCollection.get('instagram_username')
            wikiUrl = wikiUrl or openseaCollection.get('wiki_url')
            openseaSlug = openseaSlug or openseaCollection.get('slug')
            url = url or openseaCollection.get('external_url')
            discordUrl = discordUrl or openseaCollection.get('discord_url')
            bannerImageUrl = bannerImageUrl or openseaCollection.get('banner_image_url')
        retrievedCollection = RetrievedCollection(
            address=address,
            name=name,
            symbol=symbol,
            description=description,
            imageUrl=imageUrl,
            twitterUsername=twitterUsername,
            instagramUsername=instagramUsername,
            wikiUrl=wikiUrl,
            openseaSlug=openseaSlug,
            url=url,
            discordUrl=discordUrl,
            bannerImageUrl=bannerImageUrl,
            doesSupportErc721=doesSupportErc721,
            doesSupportErc1155=doesSupportErc1155,
        )
        return retrievedCollection
