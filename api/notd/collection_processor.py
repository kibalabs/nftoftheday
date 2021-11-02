import asyncio
import json
import logging

from core.exceptions import BadRequestException
from core.exceptions import NotFoundException
from core.requester import Requester
from core.requester import ResponseException
from core.web3.eth_client import EthClientInterface

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
        response = None
        retryCount = 0
        while not response:
            try:
                response = await self.requester.get(url=f'https://api.opensea.io/api/v1/asset_contract/{address}')
            except ResponseException as exception:
                if exception.statusCode == 404:
                    raise NotFoundException()
                if exception.statusCode != 429 or retryCount >= 3:
                    raise
                logging.info(f'Retrying due to: {str(exception)}')
                await asyncio.sleep(1.5)
                retryCount += 1
        responseJson = response.json()
        collection = responseJson.get('collection')
        if collection is None:
            raise CollectionDoesNotExist()
        retrievedCollection = RetrievedCollection(
            address=address,
            name= collectionName or collection.get('name'),
            symbol=collectionSymbol or collection.get('symbol'),
            description=collection.get('description'),
            imageUrl=collection.get('image_url'),
            twitterUsername=collection.get('twitter_username'),
            instagramUsername=collection.get('instagram_username'),
            wikiUrl=collection.get('wiki_url'),
            openseaSlug=collection.get('slug'),
            url=collection.get('external_url'),
            discordUrl=collection.get('discord_url'),
            bannerImageUrl=collection.get('banner_image_url'),
        )
        return retrievedCollection
