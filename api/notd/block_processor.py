import asyncio
import datetime
import json
import logging
from typing import List
from typing import Optional
from ast import literal_eval
import textwrap

import async_lru
from core.util import list_util
from core.util.chain_util import normalize_address
from core.web3.eth_client import EthClientInterface
from web3 import Web3
from web3.types import HexBytes
from web3.types import LogReceipt
from web3.types import TxData
from web3.types import TxReceipt

from notd.model import ERC1155TokenTransfer
from notd.model import RetrievedTokenTransfer

class BlockProcessor:

    def __init__(self, ethClient: EthClientInterface):
        self.w3 = Web3()
        self.ethClient = ethClient

        with open('./contracts/CryptoKitties.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.cryptoKittiesContract = self.w3.eth.contract(address='0x06012c8cf97BEaD5deAe237070F9587f8E7A266d', abi=contractJson['abi'])
        self.cryptoKittiesTransferEvent = self.cryptoKittiesContract.events.Transfer()

        with open('./contracts/CryptoPunksMarket.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.cryptoPunksContract = self.w3.eth.contract(address='0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB', abi=contractJson['abi'])
        self.cryptoPunksTransferEvent = self.cryptoPunksContract.events.PunkTransfer()
        self.cryptoPunksBoughtEvent = self.cryptoPunksContract.events.PunkBought()

        with open('./contracts/IERC721.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.ierc721Contract = self.w3.eth.contract(abi=contractJson['abi'])
        self.ierc721TransferEvent = self.ierc721Contract.events.Transfer()
        # TODO(krishan711): use the contract to get the signature hash instead of doing manually
        # self.contractFilter = self.ierc721Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
        self.erc721TansferEventSignatureHash = Web3.keccak(text='Transfer(address,address,uint256)').hex()

        with open('./contracts/IERC1155.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.ierc1155Contract = self.w3.eth.contract(abi=contractJson['abi'])
        self.ierc1155TransferEvent = self.ierc1155Contract.events.TransferSingle()
        # TODO(krishan711): use the contract to get the signature hash instead of doing manually
        # self.contractFilter = self.ierc1155Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
        self.erc1155TansferEventSignatureHash = Web3.keccak(text='TransferSingle(address,address,address,uint256,uint256)').hex()

        with open('./contracts/IERC1155.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.ierc1155Contract = self.w3.eth.contract(abi=contractJson['abi'])
        self.ierc1155TransferEvent = self.ierc1155Contract.events.TransferBatch()
        # TODO(krishan711): use the contract to get the signature hash instead of doing manually
        # self.contractFilter = self.ierc1155Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
        self.erc1155TansferBatchEventSignatureHash = Web3.keccak(text='TransferBatch(address,address,address,uint256[],uint256[])').hex()

    @async_lru.alru_cache(maxsize=100000)
    async def _get_transaction(self, transactionHash: str) -> TxData:
        return await self.ethClient.get_transaction(transactionHash=transactionHash)

    @async_lru.alru_cache(maxsize=100000)
    async def _get_transaction_receipt(self, transactionHash: str) -> TxReceipt:
        return await self.ethClient.get_transaction_receipt(transactionHash=transactionHash)

    async def get_latest_block_number(self) -> int:
        return await self.ethClient.get_latest_block_number()

    @async_lru.alru_cache(maxsize=100000)
    async def get_transfers_in_block(self, blockNumber: int) -> List[RetrievedTokenTransfer]:
        block = await self.ethClient.get_block(blockNumber)
        blockHash = block['hash'].hex()
        blockDate = datetime.datetime.fromtimestamp(block['timestamp'])
        erc721TokenTransfers = []
        #erc721events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc721TansferEventSignatureHash])
        #logging.info(f'Found {len(erc721events)} events in block #{blockNumber}')
        #for erc721EventsChunk in list_util.generate_chunks(erc721events, 5):
        #    erc721TokenTransfers += await asyncio.gather(*[self._process_event(event=dict(event), blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate) for event in erc721EventsChunk])

        erc1155TokenTransfers = []
        #erc1155events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferEventSignatureHash])
        #logging.info(f'Found {len(erc1155events)} erc1155events in block #{blockNumber}')
        #for erc1155EventsChunk in list_util.generate_chunks(erc1155events, 5):
        #    erc1155TokenTransfers += await asyncio.gather(*[self._process_erc1155_event(event=dict(event), blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate) for event in erc1155EventsChunk])

        erc1155BatchTokenTransfers = []
        erc1155Batchevents = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferBatchEventSignatureHash])
        logging.info(f'Found {len(erc1155Batchevents)} erc1155Batchevents in block #{blockNumber}')
        for erc1155BatchEventsChunk in list_util.generate_chunks(erc1155Batchevents, 5):
            erc1155BatchTokenTransfers += await asyncio.gather(*[self._process_erc1155_event(event=dict(event), blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate) for event in erc1155BatchEventsChunk])

        tokenTransferList = [tokenTransfer for tokenTransfer in erc1155BatchTokenTransfers if tokenTransfer] + [tokenTransfer for tokenTransfer in erc1155TokenTransfers if tokenTransfer] + [tokenTransfer for tokenTransfer in erc721TokenTransfers if tokenTransfer]
        return  tokenTransferList

    @staticmethod
    def decode_transaction_data(data):
        tokenIds = []
        amount = []
        test = textwrap.wrap(data[2:],64)
        test = [literal_eval(f'0x{elem}') for elem in test]
        if len(test) >2:
            lengthOfArray = test[2]
            tokenIds = test[3:3+lengthOfArray]
            lengthOfValue = test[3+lengthOfArray]
            amount = test[4+lengthOfArray:4+lengthOfArray+lengthOfValue]
        else:
            tokenIds = test[:1]
            amount = test[1:]
        dataDict = {tokenIds[i]: amount[i] for i in range(len(tokenIds))}
        return dataDict

    async def _process_erc1155_event(self, event: LogReceipt, blockNumber: int, blockHash: str, blockDate: datetime.datetime) -> Optional[RetrievedTokenTransfer]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = event['address']
        logging.debug(f'------------- {transactionHash} ------------')
        if len(event['topics']) < 4:
            logging.debug('Ignoring event with less than 4 topics')
            return None
        operatorAddress = normalize_address(event['topics'][1].hex())
        fromAddress = normalize_address(event['topics'][2].hex())
        toAddress = normalize_address(event['topics'][3].hex())
        data = self.decode_transaction_data(event['data'])
        ethTransaction = await self._get_transaction(transactionHash=transactionHash)
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        ethTransactionReceipt = await self._get_transaction_receipt(transactionHash=transactionHash)
        gasUsed = ethTransactionReceipt['gasUsed']
        transaction = [ERC1155TokenTransfer(transactionHash=transactionHash, operatorAddress=operatorAddress, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, tokenId=id, amount=amount ,value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=gasUsed, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate) for (id, amount) in data.items()]
        return transaction

    async def _process_event(self, event: LogReceipt, blockNumber: int, blockHash: str, blockDate: datetime.datetime) -> Optional[RetrievedTokenTransfer]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = event['address']
        logging.debug(f'------------- {transactionHash} ------------')
        if registryAddress == self.cryptoKittiesContract.address:
            # NOTE(krishan711): for CryptoKitties the tokenId isn't indexed in the Transfer event
            decodedEventData = self.cryptoKittiesTransferEvent.processLog(event)
            event['topics'] = [event['topics'][0], HexBytes(decodedEventData['args']['from']), HexBytes(decodedEventData['args']['to']), HexBytes(decodedEventData['args']['tokenId'])]
        if registryAddress == self.cryptoPunksContract.address:
            # NOTE(krishan711): for CryptoPunks there is a separate PunkBought (and PunkTransfer if its free) event with the punkId
            ethTransactionReceipt = await self.ethClient.get_transaction_receipt(transactionHash=transactionHash)
            decodedEventData = self.cryptoPunksBoughtEvent.processReceipt(ethTransactionReceipt)
            if len(decodedEventData) == 1:
                event['topics'] = [event['topics'][0], HexBytes(decodedEventData[0]['args']['fromAddress']), HexBytes(decodedEventData[0]['args']['toAddress']), HexBytes(decodedEventData[0]['args']['punkIndex'])]
            else:
                decodedEventData = self.cryptoPunksTransferEvent.processReceipt(ethTransactionReceipt)
                if len(decodedEventData) == 1:
                    event['topics'] = [event['topics'][0], HexBytes(decodedEventData[0]['args']['from']), HexBytes(decodedEventData[0]['args']['to']), HexBytes(decodedEventData[0]['args']['punkIndex'])]
        if len(event['topics']) < 4:
            logging.debug('Ignoring event with less than 4 topics')
            return None
        fromAddress = normalize_address(event['topics'][1].hex())
        toAddress = normalize_address(event['topics'][2].hex())
        tokenId = int.from_bytes(bytes(event['topics'][3]), 'big')
        ethTransaction = await self._get_transaction(transactionHash=transactionHash)
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        ethTransactionReceipt = await self._get_transaction_receipt(transactionHash=transactionHash)
        gasUsed = ethTransactionReceipt['gasUsed']
        transaction = [RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, tokenId=tokenId, value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=gasUsed, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate)]
        return transaction
