import dataclasses
import datetime
import json
import textwrap
from collections import defaultdict
from typing import Dict
from typing import List
from typing import Tuple

from core import logging
from core.util import chain_util
from core.web3.eth_client import EthClientInterface
from web3 import Web3
from web3.types import HexBytes
from web3.types import LogReceipt
from web3.types import TxData
from web3.types import TxReceipt

from notd.model import MARKETPLACE_ADDRESSES
from notd.model import ProcessedBlock
from notd.model import RetrievedTokenTransfer

WRAPPED_ETHER_ADDRESS = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

@dataclasses.dataclass
class RetrievedEvent:
    transactionHash: str
    registryAddress: str
    fromAddress: str
    toAddress: str
    operatorAddress: str
    tokenId: str
    amount: int
    tokenType: str


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
        self.erc721TransferEventSignatureHash = Web3.keccak(text='Transfer(address,address,uint256)').hex()
        self.erc20TransferEventSignatureHash = Web3.keccak(text='Transfer(address,address,uint256)').hex()

        with open('./contracts/IERC1155.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.ierc1155Contract = self.w3.eth.contract(abi=contractJson['abi'])
        self.ierc1155TransferEvent = self.ierc1155Contract.events.TransferSingle()
        # TODO(krishan711): use the contract to get the signature hash instead of doing manually
        # self.contractFilter = self.ierc1155Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
        self.erc1155TransferEventSignatureHash = Web3.keccak(text='TransferSingle(address,address,address,uint256,uint256)').hex()

        with open('./contracts/IERC1155.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.ierc1155Contract = self.w3.eth.contract(abi=contractJson['abi'])
        self.ierc1155TransferEvent = self.ierc1155Contract.events.TransferBatch()
        # TODO(krishan711): use the contract to get the signature hash instead of doing manually
        # self.contractFilter = self.ierc1155Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
        self.erc1155TransferBatchEventSignatureHash = Web3.keccak(text='TransferBatch(address,address,address,uint256[],uint256[])').hex()

    async def get_transaction_receipt(self, transactionHash: str) -> TxReceipt:
        return await self.ethClient.get_transaction_receipt(transactionHash=transactionHash)

    async def get_latest_block_number(self) -> int:
        return await self.ethClient.get_latest_block_number()

    async def _get_retrieved_events(self, blockNumber: int) -> Dict[str, List[RetrievedEvent]]:
        retrievedEvents: List[RetrievedEvent] = []
        erc721events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc721TransferEventSignatureHash])
        for event in erc721events:
            retrievedEvents += await self._process_erc721_single_event(event=dict(event))
        erc1155events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TransferEventSignatureHash])
        erc1155RetrievedEvents: List[RetrievedEvent] = []
        for event in erc1155events:
            erc1155RetrievedEvents += await self._process_erc1155_single_event(event=dict(event))
        erc1155BatchEvents = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TransferBatchEventSignatureHash])
        for event in erc1155BatchEvents:
            erc1155RetrievedEvents += await self._process_erc1155_batch_event(event=dict(event))
        logging.info(f'Found {len(erc721events)} erc721, {len(erc1155events)} erc1155Single, {len(erc1155BatchEvents)} erc1155Batch events in block #{blockNumber}')
        # NOTE(krishan711): these need to be merged because of floor seeps e.g. https://etherscan.io/tx/0x88affc90581254ca2ceb04cefac281c4e704d457999c6a7135072a92a7befc8b
        retrievedEvents += await self._merge_erc1155_retrieved_events(erc1155RetrievedEvents=erc1155RetrievedEvents)
        transactionHashEventMap = defaultdict(list)
        for retrievedEvent in retrievedEvents:
            transactionHashEventMap[retrievedEvent.transactionHash].append(retrievedEvent)
        return transactionHashEventMap

    async def _get_transaction_weth_values(self, blockNumber: int) -> Dict[str, List[tuple]]:
        transactionHashWethValuesMap = defaultdict(list)
        erc20events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc20TransferEventSignatureHash])
        for event in erc20events:
            if len(event['topics']) == 3 and event['address'] == WRAPPED_ETHER_ADDRESS:
                transactionHash = event['transactionHash'].hex()
                fromAddress = chain_util.normalize_address(event['topics'][1].hex())
                wethValue = int(event["data"], 16)
                transactionHashWethValuesMap[transactionHash] += [(fromAddress, wethValue)]
        return transactionHashWethValuesMap

    async def process_block(self, blockNumber: int) -> ProcessedBlock:
        # NOTE(krishan711): some blocks are too large to be retrieved from the AWS hosted node e.g. #14222802
        # for these, we can use infura specifically but if this problem gets too big find a better solution
        blockData = await self.ethClient.get_block(blockNumber=blockNumber, shouldHydrateTransactions=True)
        transactionHashEventMap = await self._get_retrieved_events(blockNumber=blockNumber)
        transactionHashWethValuesMap = await self._get_transaction_weth_values(blockNumber=blockNumber)
        retrievedTokenTransfers: List[RetrievedTokenTransfer] = []
        for transaction in blockData['transactions']:
            retrievedTokenTransfers += await self.process_transaction(transaction=transaction, retrievedEvents=transactionHashEventMap[transaction['hash'].hex()], wethValues=transactionHashWethValuesMap[transaction['hash'].hex()])
        blockHash = blockData['hash'].hex()
        blockDate = datetime.datetime.utcfromtimestamp(blockData['timestamp'])
        return ProcessedBlock(blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate, retrievedTokenTransfers=retrievedTokenTransfers)

    async def _process_erc1155_single_event(self, event: LogReceipt) -> List[RetrievedEvent]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = chain_util.normalize_address(event['address'])
        if len(event['topics']) < 4:
            logging.debug('Ignoring event with less than 4 topics')
            return []
        operatorAddress = chain_util.normalize_address(event['topics'][1].hex())
        fromAddress = chain_util.normalize_address(event['topics'][2].hex())
        toAddress = chain_util.normalize_address(event['topics'][3].hex())
        data = event['data']
        data = textwrap.wrap(data[2:], 64)
        data = [int(f'0x{elem}', 16) for elem in data]
        tokenId = data[0]
        amount = data[1]
        retrievedEvents = [RetrievedEvent(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=tokenId, amount=amount, tokenType='erc1155single')]
        return retrievedEvents

    async def _merge_erc1155_retrieved_events(self, erc1155RetrievedEvents: List[RetrievedEvent]) -> List[RetrievedEvent]:
        firstEvents = {}
        for event in erc1155RetrievedEvents:
            eventKey = (event.transactionHash, event.registryAddress, event.tokenId, event.fromAddress, event.toAddress, event.tokenType)
            firstEvent = firstEvents.get(eventKey)
            if firstEvent:
                firstEvent.amount += event.amount
            else:
                firstEvents[eventKey] = event
        return list(firstEvents.values())

    async def _process_erc1155_batch_event(self, event: LogReceipt,) -> List[RetrievedTokenTransfer]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = chain_util.normalize_address(event['address'])
        if len(event['topics']) < 4:
            logging.debug('Ignoring event with less than 4 topics')
            return []
        operatorAddress = chain_util.normalize_address(event['topics'][1].hex())
        fromAddress = chain_util.normalize_address(event['topics'][2].hex())
        toAddress = chain_util.normalize_address(event['topics'][3].hex())
        data = event['data']
        data = textwrap.wrap(data[2:], 64)
        data = [int(f'0x{elem}',16) for elem in data]
        lengthOfArray = data[2]
        tokenIds = data[3:3+lengthOfArray]
        lengthOfValue = data[3+lengthOfArray]
        amounts = data[4+lengthOfArray:4+lengthOfArray+lengthOfValue]
        dataDict = {tokenIds[i]: amounts[i] for i in range(len(tokenIds))}
        retrievedEvents = [RetrievedEvent(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=id, amount=amount, tokenType='erc1155batch') for (id, amount) in dataDict.items()]
        return retrievedEvents

    async def _process_erc721_single_event(self, event: LogReceipt) -> List[RetrievedTokenTransfer]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = chain_util.normalize_address(event['address'])
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
        fromAddress = chain_util.normalize_address(event['topics'][1].hex())
        toAddress = chain_util.normalize_address(event['topics'][2].hex())
        tokenId = int.from_bytes(bytes(event['topics'][3]), 'big')
        retrievedEvents = [RetrievedEvent(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=None, amount=1, tokenId=tokenId, tokenType='erc721')]
        return retrievedEvents

    async def process_transaction(self, transaction: TxData, retrievedEvents: List[RetrievedEvent], wethValues: List[tuple]) -> List[RetrievedTokenTransfer]:
        contractAddress = transaction['to']
        if not contractAddress:
            # NOTE(krishan711): for contract creations we have to get the contract address from the creation receipt
            ethTransactionReceipt = await self.get_transaction_receipt(transactionHash=transaction['hash'].hex())
            contractAddress = ethTransactionReceipt['contractAddress']
        contractAddress = chain_util.normalize_address(value=contractAddress)
        transactionFromAddress = chain_util.normalize_address(value=transaction['from'])
        tokenKeys = [(retrievedEvent.registryAddress, retrievedEvent.tokenId) for retrievedEvent in retrievedEvents]
        tokenKeyCounts = {tokenKey: tokenKeys.count(tokenKey) for tokenKey in tokenKeys}
        registryAddresses = {retrievedEvent.registryAddress for retrievedEvent in retrievedEvents}
        retrievedTokenTransfers: list[RetrievedTokenTransfer] = []
        # NOTE(krishan711) Set interstitial and multi first, they are independent of other info
        isMultiAddress = len(registryAddresses) > 1
        tokenKeySeenCounts: Dict[Tuple(str, str), int] = defaultdict(int)
        for retrievedEvent in retrievedEvents:
            tokenKey = (retrievedEvent.registryAddress, retrievedEvent.tokenId)
            tokenKeyCount = tokenKeyCounts[tokenKey]
            tokenKeySeenCounts[tokenKey] += 1
            isInterstitial = tokenKeySeenCounts[tokenKey] < tokenKeyCount
            isOutbound = retrievedEvent.fromAddress == transactionFromAddress
            operatorAddress = retrievedEvent.operatorAddress if retrievedEvent.operatorAddress else transactionFromAddress
            retrievedTokenTransfers += [
                RetrievedTokenTransfer(
                    transactionHash=retrievedEvent.transactionHash,
                    registryAddress=retrievedEvent.registryAddress,
                    tokenId=retrievedEvent.tokenId,
                    fromAddress=retrievedEvent.fromAddress,
                    toAddress=retrievedEvent.toAddress,
                    operatorAddress=operatorAddress,
                    contractAddress=contractAddress,
                    amount=retrievedEvent.amount,
                    value=0,
                    gasLimit=transaction['gas'],
                    gasPrice=transaction['gasPrice'],
                    blockNumber=transaction['blockNumber'],
                    tokenType=retrievedEvent.tokenType,
                    isMultiAddress=isMultiAddress,
                    isInterstitial=isInterstitial,
                    isOutbound=isOutbound,
                    isSwap=False,
                    isBatch=False,
                )
            ]
        # Calculate isBatch only if this is not a multi address
        if not isMultiAddress:
            isBatch = len({retrievedTokenTransfer for retrievedTokenTransfer in retrievedTokenTransfers if not retrievedTokenTransfer.isInterstitial}) > 1
            for retrievedTokenTransfer in retrievedTokenTransfers:
                retrievedTokenTransfer.isBatch = isBatch and not retrievedTokenTransfer.isInterstitial
        # Calculate swaps as anywhere the transaction creator receives a token
        # NOTE(krishan711): this is wrong cos it marks accepted offers as swaps but is acceptable for now cos it marks the value as 0
        # example of why this is necessary: https://etherscan.io/tx/0x6332d565f96a1ae47ae403df47acc0d28fe11c409fb2e3cc4d1a96a1c5987ed8
        nonInterstitialFromAddresses = {retrievedTokenTransfer.fromAddress for retrievedTokenTransfer in retrievedTokenTransfers if not retrievedTokenTransfer.isInterstitial}
        nonInterstitialToAddresses = {retrievedTokenTransfer.toAddress for retrievedTokenTransfer in retrievedTokenTransfers if not retrievedTokenTransfer.isInterstitial}
        isSwap = len(nonInterstitialFromAddresses.intersection(nonInterstitialToAddresses)) > 0
        for retrievedTokenTransfer in retrievedTokenTransfers:
            retrievedTokenTransfer.isSwap = isSwap
        # Calculate transaction value for either weth or eth
        transactionValue = 0
        if transaction['value'] > 0:
            transactionValue = transaction['value']
        elif len(wethValues) > 0:
            for address, wethValue in wethValues:
                if address in nonInterstitialToAddresses:
                    transactionValue += wethValue
        # Only calculate value for remaining
        if transactionValue and not isMultiAddress:
            # If contractAddress is a opensea market place isOutbound is still a valued transfer
            if contractAddress in MARKETPLACE_ADDRESSES:
                valuedTransfers = [retrievedTokenTransfer for retrievedTokenTransfer in retrievedTokenTransfers if not retrievedTokenTransfer.isInterstitial and not retrievedTokenTransfer.isSwap]
            else:
                valuedTransfers = [retrievedTokenTransfer for retrievedTokenTransfer in retrievedTokenTransfers if not retrievedTokenTransfer.isInterstitial and not retrievedTokenTransfer.isSwap and not retrievedTokenTransfer.isOutbound]
            for retrievedTokenTransfer in valuedTransfers:
                retrievedTokenTransfer.value = int(transactionValue / len(valuedTransfers))
        return retrievedTokenTransfers
