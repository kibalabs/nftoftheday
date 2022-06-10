from collections import defaultdict
import dataclasses
import datetime
import json
import textwrap
from typing import List

from core import logging
from core.util import chain_util
from core.web3.eth_client import EthClientInterface
from web3 import Web3
from web3.types import HexBytes
from web3.types import LogReceipt
from web3.types import TxData
from web3.types import TxReceipt

from notd.model import ProcessedBlock
from notd.model import RetrievedTokenTransfer

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

    async def get_transaction_receipt(self, transactionHash: str) -> TxReceipt:
        return await self.ethClient.get_transaction_receipt(transactionHash=transactionHash)

    async def get_latest_block_number(self) -> int:
        return await self.ethClient.get_latest_block_number()

    async def process_block(self, blockNumber: int) -> List[RetrievedTokenTransfer]:
        # NOTE(krishan711): some blocks are too large to be retrieved from the AWS hosted node e.g. #14222802
        # for these, we can use infura specifically but if this problem gets too big find a better solution
        blockData = await self.ethClient.get_block(blockNumber=blockNumber, shouldHydrateTransactions=True)
        retrievedEvents = []
        erc721events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc721TansferEventSignatureHash])
        logging.info(f'Found {len(erc721events)} erc721 events in block #{blockNumber}')
        for event in erc721events:
            retrievedEvents += await self._process_erc721_single_event(event=dict(event))
        erc1155events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferEventSignatureHash])
        logging.info(f'Found {len(erc1155events)} erc1155Single events in block #{blockNumber}')
        erc1155RetrievedEvents = []
        for event in erc1155events:
            erc1155RetrievedEvents += await self._process_erc1155_single_event(event=dict(event))
        erc1155Batchevents = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferBatchEventSignatureHash])
        logging.info(f'Found {len(erc1155Batchevents)} erc1155Batch events in block #{blockNumber}')
        for event in erc1155Batchevents:
            erc1155RetrievedEvents += await self._process_erc1155_batch_event(event=dict(event))
        # NOTE(krishan711): these need to be merged because of floor seeps e.g. https://etherscan.io/tx/0x88affc90581254ca2ceb04cefac281c4e704d457999c6a7135072a92a7befc8b
        retrievedEvents += await self._merge_erc1155_retrieved_events(erc1155RetrievedEvents=erc1155RetrievedEvents)
        transactionHashEventMap = defaultdict(list)
        for retrievedEvent in retrievedEvents:
            transactionHashEventMap[retrievedEvent.transactionHash].append(retrievedEvent)
        retrievedTokenTransfers = []
        for transaction in blockData['transactions']:
            retrievedTokenTransfers += await self.process_transaction(transaction=transaction, retrievedEvents=transactionHashEventMap[transaction['hash'].hex()])
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
        retrievedEvent = [RetrievedEvent(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=tokenId, amount=amount, tokenType='erc1155single')]
        return retrievedEvent

    # NOTE(krishan711): these need to be merged because of floor sweeps e.g. https://etherscan.io/tx/0x88affc90581254ca2ceb04cefac281c4e704d457999c6a7135072a92a7befc8b
    async def _merge_erc1155_retrieved_events(self, erc1155RetrievedEvents: List[RetrievedEvent]) -> List[RetrievedEvent]:
        firstEvents =  dict()
        for event in erc1155RetrievedEvents:
            eventKer = (event.transactionHash, event.registryAddress, event.tokenId, event.fromAddress, event.toAddress, event.tokenType)
            firstEvent = firstEvents.get(eventKer)
            if firstEvent:
                firstEvent.amount += event.amount
            else:
                firstEvents[eventKer] = event
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
        retrievedEvent = [RetrievedEvent(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=id, amount=amount, tokenType = 'erc1155batch') for (id, amount) in dataDict.items()]
        return retrievedEvent

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
        retrievedEvent = [RetrievedEvent(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=None, amount=1, tokenId=tokenId, tokenType='erc721')]
        return retrievedEvent

    async def process_transaction(self, transaction: TxData, retrievedEvents: dict) -> List[RetrievedTokenTransfer]:
        retrievedTokenTransfers = []
        tokens =[(retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId) for retrievedEvent in retrievedEvents]
        tokensCount = {(retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId):tokens.count((retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId)) for retrievedEvent in retrievedEvents}
        count = len(tokensCount)
        setOfAddresses = {retrievedEvent.registryAddress for retrievedEvent in retrievedEvents}
        for retrievedEvent in retrievedEvents:
            isMultiAddress = (bool(len(setOfAddresses) > 1))
            if tokensCount[(retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId)] > 1:
                isInterstitialTransfer = True
                tokensCount[(retrievedEvent.transactionHash,retrievedEvent.registryAddress,retrievedEvent.tokenId)] -= 1
            else:
                isInterstitialTransfer = False
            retrievedTokenTransfers += [
                RetrievedTokenTransfer(
                    transactionHash=retrievedEvent.transactionHash,
                    registryAddress=retrievedEvent.registryAddress,
                    tokenId=retrievedEvent.tokenId,
                    fromAddress=retrievedEvent.fromAddress,
                    toAddress=retrievedEvent.toAddress,
                    operatorAddress=retrievedEvent.operatorAddress if retrievedEvent.operatorAddress else transaction['from'],
                    amount=retrievedEvent.amount,
                    value=transaction['value']/count if transaction['value']>0 and not (isInterstitialTransfer or isMultiAddress)  else 0,
                    gasLimit=transaction['gas'],
                    gasPrice=transaction['gasPrice'],
                    blockNumber=transaction['blockNumber'],
                    tokenType=retrievedEvent.tokenType,
                    isMultiAddress=False or isMultiAddress,
                    isInterstitialTransfer=False or isInterstitialTransfer,
                )
            ]
        return retrievedTokenTransfers
