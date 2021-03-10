import json
import datetime
from typing import List
from typing import Optional
import logging

import web3
from web3 import Web3
from web3.contract import Contract
from web3.types import LogReceipt
from eth_utils import event_abi_to_log_topic
from hexbytes import HexBytes

from notd.model import RetrievedTokenTransfer

class BlockProcessor:

    def __init__(self, web3Connection: Web3):
        self.w3 = web3Connection
        with open('./contracts/CryptoKitties.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.cryptoKittiesContract = self.w3.eth.contract(address='0x06012c8cf97BEaD5deAe237070F9587f8E7A266d', abi=contractJson['abi'])
        self.cryptoKittiesTransferEvent = self.cryptoKittiesContract.events.Transfer()
        with open('./contracts/IERC721.json') as contractJsonFile:
            contractJson = json.load(contractJsonFile)
        self.ierc721Contract = self.w3.eth.contract(abi=contractJson['abi'])
        self.ierc721TransferEvent = self.ierc721Contract.events.Transfer()
        # TODO(krishan711): use the contract to get the signature hash instead of doing manually
        # self.contractFilter = self.ierc721Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
        self.erc721TansferEventSignatureHash = Web3.keccak(text='Transfer(address,address,uint256)').hex()

    async def get_transfers_in_block(self, blockNumber: int) -> List[RetrievedTokenTransfer]:
        block = self.w3.eth.getBlock(blockNumber)
        blockHash = block['hash'].hex()
        blockDate = datetime.datetime.fromtimestamp(block['timestamp'])
        contractFilter = self.w3.eth.filter({
            'fromBlock': blockNumber,
            'toBlock': blockNumber,
            'topics': [self.erc721TansferEventSignatureHash],
        })
        tokenTransfers = []
        for event in contractFilter.get_all_entries():
            tokenTransfer = await self.process_event(event=dict(event), blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate)
            if tokenTransfer:
                tokenTransfers.append(tokenTransfer)
        return tokenTransfers

    async def process_event(self, event: LogReceipt, blockNumber: int, blockHash: str, blockDate: datetime.datetime) -> Optional[RetrievedTokenTransfer]:
        transactionHash = event['transactionHash'].hex()
        registryAddress = event['address']
        logging.debug(f'------------- {transactionHash} ------------')
        if registryAddress == self.cryptoKittiesContract.address:
            decodedEventData = self.cryptoKittiesTransferEvent.processLog(event)
            event['topics'] = [event['topics'][0], HexBytes(decodedEventData['args']['from']), HexBytes(decodedEventData['args']['to']), HexBytes(decodedEventData['args']['tokenId'])]
        # NOTE(krishan711): for CryptoPunks we need more work!
        # if registryAddress == '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB':
        #     print('event', event)
        #     raise Exception()
        if len(event['topics']) < 4:
            logging.debug(f'Ignoring event with less than 4 topics')
            return None
        fromAddress = event['topics'][1].hex()
        toAddress = event['topics'][2].hex()
        tokenId = int.from_bytes(bytes(event['topics'][3]), 'big')
        ethTransaction = self.w3.eth.get_transaction(transactionHash)
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        ethTransactionReceipt = self.w3.eth.getTransactionReceipt(transactionHash)
        gasUsed = ethTransactionReceipt['gasUsed']
        transaction = RetrievedTokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, tokenId=tokenId, value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=gasUsed, blockNumber=blockNumber, blockHash=blockHash, blockDate=blockDate)
        return transaction
