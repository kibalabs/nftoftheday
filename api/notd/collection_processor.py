import asyncio
import json
import logging
import os

from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.requester import ResponseException
from core.web3.eth_client import EthClientInterface
from httpx import ReadTimeout

from notd.model import RetrievedCollection


class CollectionDoesNotExist(NotFoundException):
    pass

class CollectionProcessor:

    def __init__(self, requester: Requester, ethClient: EthClientInterface):
        self.requester = requester
        self.ethClient = ethClient
        with open('./contracts/IERC721Metadata.json') as contractJsonFile:
            erc721MetdataContractJson = json.load(contractJsonFile)
        self.erc721MetdataContractAbi = erc721MetdataContractJson['abi']
        self.erc721MetadataNameFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'name'][0]
        self.erc721MetadataSymbolFunctionAbi = [internalAbi for internalAbi in self.erc721MetdataContractAbi if internalAbi['name'] == 'symbol'][0]

    async def retrieve_collection(self, address: str) -> RetrievedCollection:
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
        openseaResponse = None
        retryCount = 0
        while not openseaResponse:
            try:
                openseaResponse = await self.requester.get(url=f'https://api.opensea.io/api/v1/asset_contract/{address}',headers={"X-API-KEY": f"{os.environ['OPENSEA_API_KEY']}"})
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
            url=openseaCollection.get('external_url'),
            discordUrl=openseaCollection.get('discord_url'),
            bannerImageUrl=openseaCollection.get('banner_image_url'),
        )
        print(retrievedCollection)
        return retrievedCollection
