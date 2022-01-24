import asyncio
import json
import logging

from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.requester import ResponseException
from core.web3.eth_client import EthClientInterface
from httpx import ReadTimeout

from notd.model import RetrievedCollection

_INTERFACE_ID_ERC721 = '0x5b5e139f'
_INTERFACE_ID_ERC1155 = '0xd9b67a26'


class CollectionDoesNotExist(NotFoundException):
    pass

class CollectionProcessor:

    def __init__(self, requester: Requester, ethClient: EthClientInterface, openseaApiKey: str):
        self.requester = requester
        self.ethClient = ethClient
        self.openseaApiKey = openseaApiKey
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]
        self.erc721MetadataSymbolFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'symbol'][0]
        self.erc721MetadataSymbolFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'contractURI'][0]
        with open('./contracts/IERC1155MetadataURI.json') as contractJsonFile:
            erc1155MetadataContractJson = json.load(contractJsonFile)
        self.erc1155MetadataContractAbi = erc1155MetadataContractJson['abi']
        self.erc1155MetadataUriFunctionAbi = [internalAbi for internalAbi in self.erc1155MetadataContractAbi if internalAbi.get('name') == 'uri'][0]
        with open('./contracts/IERC165.json') as contractJsonFile:
            erc165MetadataContractJson = json.load(contractJsonFile)
        self.erc165MetadataContractAbi = erc165MetadataContractJson['abi']
        self.erc165SupportInterfaceUriFunctionAbi = [internalAbi for internalAbi in self.erc165MetadataContractAbi if internalAbi.get('name') == 'supportsInterface'][0]

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
            contractUriResponse = await self.ethClient.call_function(toAddress=address, contractAbi=self.erc721MetdataContractAbi, functionAbi=self.erc721MetdataContractURI)
            contractMetadataUri = contractUriResponse[0]
        except BadRequestException:
            contractMetadataUri = None
        if contractMetadataUri is not None:
            contractMetadataUriResponse = await self.requester.get(url=contractMetadataUri)
            openseaCollection = contractMetadataUriResponse.json()
            if isinstance(openseaCollection, str):
                    openseaCollection = json.loads(openseaCollection)
        else:
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
        retrievedCollection = RetrievedCollection(
            address=address,
            name=collectionName or openseaCollection.get('name'),
            symbol=collectionSymbol or openseaCollection.get('symbol'),
            description=openseaCollection.get('description'),
            imageUrl=openseaCollection.get('image_url'),
            twitterUsername=openseaCollection.get('twitter_username'),
            instagramUsername=openseaCollection.get('instagram_username'),
            wikiUrl=openseaCollection.get('wiki_url'),
            openseaSlug=openseaCollection.get('slug'),
            url=openseaCollection.get('external_url') or contractMetadataUri,
            discordUrl=openseaCollection.get('discord_url'),
            bannerImageUrl=openseaCollection.get('banner_image_url'),
            doesSupportErc721=doesSupportErc721,
            doesSupportErc1155=doesSupportErc1155,
        )
        return retrievedCollection
