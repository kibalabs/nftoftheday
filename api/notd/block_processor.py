import datetime
import json
import logging
import textwrap
from typing import List

from core.util.chain_util import normalize_address
from core.web3.eth_client import EthClientInterface
from web3 import Web3
from web3.types import BlockData
from web3.types import HexBytes
from web3.types import LogReceipt
from web3.types import TxData
from web3.types import TxReceipt

from notd.model import ProcessedBlock
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

    async def _get_transaction(self, transactionHash: str, blockData: BlockData) -> TxData:
        return next((transaction for transaction in blockData['transactions'] if transaction['hash'].hex() == transactionHash), None)

    async def get_transaction_receipt(self, transactionHash: str) -> TxReceipt:
        return await self.ethClient.get_transaction_receipt(transactionHash=transactionHash)

    async def get_latest_block_number(self) -> int:
        return await self.ethClient.get_latest_block_number()

    async def process_block(self, blockNumber: int) -> List[RetrievedTokenTransfer]:
        blockData = await self.ethClient.get_block(blockNumber=blockNumber, shouldHydrateTransactions=True)
        retrievedTokenTransfers = []
        erc721events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc721TansferEventSignatureHash])
        logging.info(f'Found {len(erc721events)} erc721 events in block #{blockNumber}')
        for event in erc721events:
            retrievedTokenTransfers += await self._process_erc721_single_event(event=dict(event), blockData=blockData)
        erc1155events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferEventSignatureHash])
        logging.info(f'Found {len(erc1155events)} erc1155Single events in block #{blockNumber}')
        for event in erc1155events:
            retrievedTokenTransfers += await self._process_erc1155_single_event(event=dict(event), blockData=blockData)
        erc1155Batchevents = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferBatchEventSignatureHash])
        logging.info(f'Found {len(erc1155Batchevents)} erc1155Batch events in block #{blockNumber}')
        for event in erc1155Batchevents:
            retrievedTokenTransfers += await self._process_erc1155_batch_event(event=dict(event), blockData=blockData)
        blockNumber = blockData['number']
        blockHash = blockData['hash'].hex()
        blockDate = datetime.datetime.fromtimestamp(blockData['timestamp'])
        return ProcessedBlock(blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate, retrievedTokenTransfers=retrievedTokenTransfers)

    async def _process_erc1155_single_event(self, event: LogReceipt, blockData: BlockData) -> List[RetrievedTokenTransfer]:
        blockNumber = blockData['number']
        blockHash = blockData['hash'].hex()
        blockDate = datetime.datetime.fromtimestamp(blockData['timestamp'])
        transactionHash = event['transactionHash'].hex()
        registryAddress = normalize_address(event['address'])
        logging.debug(f'------------- {transactionHash} ------------')
        if len(event['topics']) < 4:
            logging.debug('Ignoring event with less than 4 topics')
            return []
        operatorAddress = normalize_address(event['topics'][1].hex())
        fromAddress = normalize_address(event['topics'][2].hex())
        toAddress = normalize_address(event['topics'][3].hex())
        data = event['data']
        data = textwrap.wrap(data[2:], 64)
        data = [int(f'0x{elem}',16) for elem in data]
        tokenId = data[0]
        amount = data[1]
        ethTransaction = await self._get_transaction(transactionHash=transactionHash, blockData=blockData)
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        transactions = [RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=tokenId, amount=amount, value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=0, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate, tokenType='erc1155single')]
        return transactions

    async def _process_erc1155_batch_event(self, event: LogReceipt, blockData: BlockData) -> List[RetrievedTokenTransfer]:
        blockNumber = blockData['number']
        blockHash = blockData['hash'].hex()
        blockDate = datetime.datetime.fromtimestamp(blockData['timestamp'])
        transactionHash = event['transactionHash'].hex()
        registryAddress = normalize_address(event['address'])
        logging.debug(f'------------- {transactionHash} ------------')
        if len(event['topics']) < 4:
            logging.debug('Ignoring event with less than 4 topics')
            return []
        operatorAddress = normalize_address(event['topics'][1].hex())
        fromAddress = normalize_address(event['topics'][2].hex())
        toAddress = normalize_address(event['topics'][3].hex())
        data = event['data']
        data = textwrap.wrap(data[2:], 64)
        data = [int(f'0x{elem}',16) for elem in data]
        lengthOfArray = data[2]
        tokenIds = data[3:3+lengthOfArray]
        lengthOfValue = data[3+lengthOfArray]
        amounts = data[4+lengthOfArray:4+lengthOfArray+lengthOfValue]
        dataDict = {tokenIds[i]: amounts[i] for i in range(len(tokenIds))}
        ethTransaction = await self._get_transaction(transactionHash=transactionHash, blockData=blockData)
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        transactions = [RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=id, amount=amount ,value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=0, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate, tokenType='erc1155batch') for (id, amount) in dataDict.items()]
        return transactions

    async def _process_erc721_single_event(self, event: LogReceipt, blockData: BlockData) -> List[RetrievedTokenTransfer]:
        blockNumber = blockData['number']
        blockHash = blockData['hash'].hex()
        blockDate = datetime.datetime.fromtimestamp(blockData['timestamp'])
        transactionHash = event['transactionHash'].hex()
        registryAddress = normalize_address(event['address'])
        logging.debug(f'------------- {transactionHash} ------------')
        if registryAddress == self.cryptoKittiesContract.address:
            # NOTE(krishan711): for CryptoKitties the tokenId isn't indexed in the Transfer event
            decodedEventData = self.cryptoKittiesTransferEvent.processLog(event)
            event['topics'] = [event['topics'][0], HexBytes(decodedEventData['args']['from']), HexBytes(decodedEventData['args']['to']), HexBytes(decodedEventData['args']['tokenId'])]
        if registryAddress == self.cryptoPunksContract.address:
            # NOTE(krishan711): for CryptoPunks there is a separate PunkBought (and PunkTransfer if its free) event with the punkId
            ethTransactionReceipt = await self.get_transaction_receipt(transactionHash=transactionHash)
            decodedEventData = self.cryptoPunksBoughtEvent.processReceipt(ethTransactionReceipt)
            if len(decodedEventData) == 1:
                event['topics'] = [event['topics'][0], HexBytes(decodedEventData[0]['args']['fromAddress']), HexBytes(decodedEventData[0]['args']['toAddress']), HexBytes(decodedEventData[0]['args']['punkIndex'])]
            else:
                decodedEventData = self.cryptoPunksTransferEvent.processReceipt(ethTransactionReceipt)
                if len(decodedEventData) == 1:
                    event['topics'] = [event['topics'][0], HexBytes(decodedEventData[0]['args']['from']), HexBytes(decodedEventData[0]['args']['to']), HexBytes(decodedEventData[0]['args']['punkIndex'])]
        if len(event['topics']) < 4:
            logging.debug('Ignoring event with less than 4 topics')
            return []
        fromAddress = normalize_address(event['topics'][1].hex())
        toAddress = normalize_address(event['topics'][2].hex())
        tokenId = int.from_bytes(bytes(event['topics'][3]), 'big')
        ethTransaction = await self._get_transaction(transactionHash=transactionHash, blockData=blockData)
        operatorAddress = ethTransaction['from']
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        transactions = [RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=tokenId, value=value, amount=1, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=0, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate, tokenType='erc721')]
        return transactions
