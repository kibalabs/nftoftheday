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

from nftoftheday.model import TokenTransfer

class NftOfTheDay:

    def __init__(self, web3Connection: Web3):
        self.w3 = web3Connection
        # with open('./contracts/IERC721.json') as contractJsonFile:
        #     ierc721ContractJson = json.load(contractJsonFile)
        # ierc721Contract = w3.eth.contract(abi=ierc721ContractJson["abi"])
        # contractFilter = ierc721Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
        # TODO(krishan711): use the contract to get the signature hash instead of doing manually
        self.erc721TansferEventSignatureHash = Web3.keccak(text="Transfer(address,address,uint256)").hex()

    def get_transfers_in_block(self, blockNumber: int) -> List[TokenTransfer]:
        block = self.w3.eth.getBlock(blockNumber)
        blockDate = datetime.datetime.fromtimestamp(block['timestamp'])
        contractFilter = self.w3.eth.filter({
            'fromBlock': blockNumber,
            'toBlock': blockNumber,
            'topics': [self.erc721TansferEventSignatureHash],
        })
        tokenTransfers = []
        for event in contractFilter.get_all_entries():
            tokenTransfer = self.process_event(event=event, blockDate=blockDate)
            if tokenTransfer:
                tokenTransfers.append(tokenTransfer)
        return tokenTransfers

    def process_event(self, event: LogReceipt, blockDate: datetime.datetime) -> Optional[TokenTransfer]:
        transactionHash = event["transactionHash"].hex()
        logging.debug(f'------------- {transactionHash} ------------')
        if len(event['topics']) < 4:
            logging.debug(f'Ignoring event with less than 4 topics')
            return None
        registryAddress = event['address']
        fromAddress = event['topics'][1].hex()
        toAddress = event['topics'][2].hex()
        tokenId = int.from_bytes(bytes(event['topics'][3]), 'big')
        ethTransaction = self.w3.eth.get_transaction(transactionHash)
        gasLimit = ethTransaction['gas']
        gasPrice = ethTransaction['gasPrice']
        value = ethTransaction['value']
        ethTransactionReceipt = self.w3.eth.getTransactionReceipt(transactionHash)
        gasUsed = ethTransactionReceipt['gasUsed']
        transaction = TokenTransfer(transactionHash=transactionHash, registryAddress=registryAddress, fromAddress=fromAddress, toAddress=toAddress, tokenId=tokenId, value=value, gasLimit=gasLimit, gasPrice=gasPrice, gasUsed=gasUsed, blockDate=blockDate)
        return transaction
