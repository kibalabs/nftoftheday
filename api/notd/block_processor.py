import asyncio
import datetime
import json
import textwrap
from typing import Counter, Dict
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

class RetrievedEvents():
    pass


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
        transactionMap = {transaction['hash'].hex(): transaction for transaction in blockData['transactions']}
        retrievedTokenTransfers = []
        erc721events = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc721TansferEventSignatureHash])
        logging.info(f'Found {len(erc721events)} erc721 events in block #{blockNumber}')
        erc1155SingleEvents = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferEventSignatureHash])
        logging.info(f'Found {len(erc1155SingleEvents)} erc1155Single events in block #{blockNumber}')
        erc1155BatchEvents = await self.ethClient.get_log_entries(startBlockNumber=blockNumber, endBlockNumber=blockNumber, topics=[self.erc1155TansferBatchEventSignatureHash])
        logging.info(f'Found {len(erc1155BatchEvents)} erc1155Batch events in block #{blockNumber}')
        retrievedTokenTransfers += await asyncio.gather(*[self.process_transaction(erc721events=erc721events, erc1155SingleEvents=erc1155SingleEvents, erc1155BatchEvents=erc1155BatchEvents, transaction=transaction) for transaction in blockData['transactions']])
        retrievedTokenTransfers =  [tokenTransfer for tokenTransfers in retrievedTokenTransfers if tokenTransfers is not None for tokenTransfer in tokenTransfers if tokenTransfer is not None]

    #     # NOTE(krishan711): these need to be merged because of floor seeps e.g. https://etherscan.io/tx/0x88affc90581254ca2ceb04cefac281c4e704d457999c6a7135072a92a7befc8b
    #     retrievedTokenTransfers += await self._merge_erc1155_transfers(erc1155Transfers=erc1155Transfers)
        blockHash = blockData['hash'].hex()
        blockDate = datetime.datetime.utcfromtimestamp(blockData['timestamp'])
        return ProcessedBlock(blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate, retrievedTokenTransfers=retrievedTokenTransfers)

    async def _process_erc1155_single_event(self, event: LogReceipt, blockNumber: int, transaction: TxData, ) -> List[RetrievedTokenTransfer]:
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
        gasLimit = transaction['gas']
        gasPrice = transaction['gasPrice']
        isMultiAddress =  False
        isInterstitialTransfer =  False
        value = transaction['value']
        transactions = [RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=tokenId, amount=amount, value=value, gasLimit=gasLimit, gasPrice=gasPrice, blockNumber=blockNumber, tokenType='erc1155single', isMultiAddress=isMultiAddress, isInterstitialTransfer=isInterstitialTransfer)]
        return transactions

    async def _merge_erc1155_transfers(self, erc1155Transfers: List[RetrievedTokenTransfer]) -> List[RetrievedTokenTransfer]:
        firstTransfers = dict()
        for transfer in erc1155Transfers:
            transferKer = (transfer.transactionHash, transfer.registryAddress, transfer.tokenId, transfer.fromAddress, transfer.toAddress, transfer.tokenType)
            firstTransfer = firstTransfers.get(transferKer)
            if firstTransfer:
                firstTransfer.amount += transfer.amount
                firstTransfer.value += transfer.value
            else:
                firstTransfers[transferKer] = transfer
        return list(firstTransfers.values())

    async def _process_erc1155_batch_event(self, event: LogReceipt, blockNumber: int, transaction: TxData) -> List[RetrievedTokenTransfer]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = chain_util.normalize_address(event['address'])
        logging.debug(f'------------- {transactionHash} ------------')
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
        gasLimit = transaction['gas']
        gasPrice = transaction['gasPrice']
        isMultiAddress =  False
        isInterstitialTransfer =  False
        value = transaction['value']
        transactions = [RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=id, amount=amount ,value=value*amount, gasLimit=gasLimit, gasPrice=gasPrice, blockNumber=blockNumber, tokenType='erc1155batch', isMultiAddress=isMultiAddress, isInterstitialTransfer=isInterstitialTransfer) for (id, amount) in dataDict.items()]
        return transactions

    async def _process_erc721_single_event(self, event: LogReceipt, blockNumber: int, transaction: TxData) -> List[RetrievedTokenTransfer]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = chain_util.normalize_address(event['address'])
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
        fromAddress = chain_util.normalize_address(event['topics'][1].hex())
        toAddress = chain_util.normalize_address(event['topics'][2].hex())
        tokenId = int.from_bytes(bytes(event['topics'][3]), 'big')
        operatorAddress = transaction['from']
        gasLimit = transaction['gas']
        gasPrice = transaction['gasPrice']
        isMultiAddress = False 
        isInterstitialTransfer =  False
        value = transaction['value']
        transactions = [RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, operatorAddress=operatorAddress, tokenId=tokenId, value=value, amount=1, gasLimit=gasLimit, gasPrice=gasPrice, blockNumber=blockNumber, tokenType='erc721', isMultiAddress=isMultiAddress, isInterstitialTransfer=isInterstitialTransfer)]
        return transactions

    async def process_transaction(self, erc721events: List[LogReceipt], erc1155SingleEvents: List[LogReceipt], erc1155BatchEvents: List[LogReceipt],transaction: TxData):
        #EXtract events here
        #NO LOGIC IN PROCESS BLOCK
        #print([transaction if transaction['hash'].hex()=='0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef' else []])
        sol = []
        retrievedTokenTransfers = {}
        for event in erc721events:
            if event['transactionHash'].hex() == transaction['hash'].hex() and len(event['topics']) > 3:
                retrievedTokenTransfers[event['transactionHash'].hex()] = retrievedTokenTransfers.get(event['transactionHash'].hex()) + await self._process_erc721_single_event(event=event, blockNumber=transaction['blockNumber'], transaction=transaction,) if retrievedTokenTransfers.get(event['transactionHash'].hex()) else await self._process_erc721_single_event(event=event, blockNumber=transaction['blockNumber'], transaction=transaction,)
                #retrievedTokenTransfer += await asyncio.gather(*[self._process_erc721_single_event(event=event, blockNumber=transaction['blockNumber'], transaction=transaction,)])
        for event in erc1155SingleEvents:
            if event['transactionHash'].hex() == transaction['hash'].hex() and len(event['topics']) > 3:
                retrievedTokenTransfers[event['transactionHash'].hex()] = retrievedTokenTransfers.get(event['transactionHash'].hex()) + await self._process_erc1155_single_event(event=event, blockNumber=transaction['blockNumber'], transaction=transaction,) if retrievedTokenTransfers.get(event['transactionHash'].hex()) else await self._process_erc1155_single_event(event=event, blockNumber=transaction['blockNumber'], transaction=transaction,)
        for event in erc1155BatchEvents:
            if event['transactionHash'].hex() == transaction['hash'].hex() and len(event['topics']) > 3:
                retrievedTokenTransfers[event['transactionHash'].hex()] = retrievedTokenTransfers.get(event['transactionHash'].hex()) + await self._process_erc1155_batch_event(event=event, blockNumber=transaction['blockNumber'], transaction=transaction,) if retrievedTokenTransfers.get(event['transactionHash'].hex()) else await self._process_erc1155_batch_event(event=event, blockNumber=transaction['blockNumber'], transaction=transaction,)

        for tokenTransfers in retrievedTokenTransfers.values():
            if len({tokenTransfer.registryAddress for tokenTransfer in tokenTransfers}) > 1:
                for tokenTransfer in tokenTransfers:
                    tokenTransfer.isMultiAddress = True
                    tokenTransfer.value = 0
            tokens =[(tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId) for tokenTransfer in tokenTransfers]
            tokensCount = {(tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId):tokens.count((tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId)) for tokenTransfer in tokenTransfers}
            count = len(tokenTransfers)
            for  tokenTransfer in tokenTransfers:
                if tokensCount[(tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId)] > 1:
                    tokenTransfer.isInterstitialTransfer = True
                    tokenTransfer.value = 0
                    tokensCount[(tokenTransfer.transactionHash,tokenTransfer.registryAddress,tokenTransfer.tokenId)] -= 1
                    count -= 1
            for tokenTransfer in tokenTransfers:
                if not tokenTransfer.isInterstitialTransfer and not tokenTransfer.isMultiAddress and tokenTransfer.value != 0:
                    tokenTransfer.value = tokenTransfer.value//count

            return tokenTransfers


            #move logic from proces block and process event to process transaction
            #process events returns retrieved events