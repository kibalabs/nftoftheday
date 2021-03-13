import json
import datetime
from typing import List
from typing import Optional
import logging

import web3
from web3 import Web3
from web3.contract import Contract
from web3.types import LogReceipt
from web3.types import BlockData
from web3.types import TxData
from web3.types import TxReceipt
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes

from notd.model import RetrievedTokenTransfer
from notd.core.requester import Requester

class EthClientInterface:

    async def get_latest_block_number(self) -> int:
        raise NotImplementedError()

    async def get_block(self, blockNumber: int) -> BlockData:
        raise NotImplementedError()

    async def get_transaction(self, transactionHash: str) -> TxData:
        raise NotImplementedError()

    async def get_transaction_receipt(self, transactionHash: str) -> TxReceipt:
        raise NotImplementedError()

class Web3EthClient(EthClientInterface):

    def __init__(self, web3Connection: Web3):
        self.w3 = web3Connection

    async def get_latest_block_number(self) -> int:
        return self.w3.eth.block_number

    async def get_block(self, blockNumber: int) -> BlockData:
        return self.w3.eth.get_block(blockNumber)

    async def get_transaction(self, transactionHash: str) -> TxData:
        return self.w3.eth.get_transaction(transactionHash)

    async def get_transaction_receipt(self, transactionHash: str) -> TxReceipt:
        return self.w3.eth.getTransactionReceipt(transactionHash)

# class EtherscanEthClient(EthClientInterface):

#     def __init__(self, apiKey: str, requester: Requester):
#         self.apiKey = apiKey
#         self.requester = requester
#         self.apiUrl = 'https://api.etherscan.io/api'

#     async def get_latest_block_number(self) -> int:
#         return self.w3.eth.block_number

#     async def get_block(self, blockNumber: int) -> BlockData:
#         response = await self.requester.get(url=self.apiUrl, data={'module': 'block', }, headers={'Authorization': f'Bearer {self.apiKey}'})
#         jsonResponse = json.loads(response.content)
#         print('jsonResponse', json.dumps(jsonResponse))

#     async def get_transaction(self, transactionHash: str) -> TxData:
#         return self.w3.eth.get_transaction(transactionHash)

#     async def get_transaction_receipt(self, transactionHash: str) -> TxReceipt:
#         return self.w3.eth.getTransactionReceipt(transactionHash)

class BlockProcessor:

    def __init__(self, web3Connection: Web3, ethClient: EthClientInterface):
        self.w3 = web3Connection
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

    async def get_latest_block_number(self) -> int:
        return await self.ethClient.get_latest_block_number()

    async def get_transfers_in_block(self, blockNumber: int) -> List[RetrievedTokenTransfer]:
        block = await self.ethClient.get_block(blockNumber)
        blockHash = block['hash'].hex()
        blockDate = datetime.datetime.fromtimestamp(block['timestamp'])
        contractFilter = self.w3.eth.filter({
            'fromBlock': blockNumber,
            'toBlock': blockNumber,
            'topics': [self.erc721TansferEventSignatureHash],
        })
        tokenTransfers = []
        for event in contractFilter.get_all_entries():
            tokenTransfer = await self._process_event(event=dict(event), blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate)
            if tokenTransfer:
                tokenTransfers.append(tokenTransfer)
        return tokenTransfers

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
            logging.debug(f'Ignoring event with less than 4 topics')
            return None
        fromAddress = event['topics'][1].hex()
        toAddress = event['topics'][2].hex()
        tokenId = int.from_bytes(bytes(event['topics'][3]), 'big')
        ethTransaction = await self.ethClient.get_transaction(transactionHash=transactionHash)
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        ethTransactionReceipt = await self.ethClient.get_transaction_receipt(transactionHash=transactionHash)
        gasUsed = ethTransactionReceipt['gasUsed']
        transaction = RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, tokenId=tokenId, value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=gasUsed, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate)
        return transaction
