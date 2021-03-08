import json

import web3
from web3 import Web3
from web3.contract import Contract
from eth_utils import event_abi_to_log_topic


w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/rdYIr6T2nBgJvtKlYQxmVH3bvjW2DLxi'))


# Block 6517190
block = w3.eth.get_block('0x118a3cd8b55d4026a7a0f9710f5328ff7d7e78a5e160bdcdd15698cc74f8417f')
# print('block', block)

with open('./contracts/IERC721.json') as contractJsonFile:
    ierc721ContractJson = json.load(contractJsonFile)
ierc721ContractAbi = ierc721ContractJson["abi"]

ierc721Contract = w3.eth.contract(abi=ierc721ContractAbi)

# contractFilter = ierc721Contract.events.Transfer.createFilter(fromBlock=6517190, toBlock=6517190, topics=[None, None, None, None])
# TODO(krishan711): use the contract to get the signature hash instead of doing manually
eventSignatureHash = Web3.keccak(text="Transfer(address,address,uint256)").hex()
contractFilter = w3.eth.filter({
    'fromBlock': 6517190,
    'toBlock': 6517190,
    "topics": [eventSignatureHash],
})

entries = contractFilter.get_all_entries()
for entry in entries:
    transactionHash = entry["transactionHash"].hex()
    if len(entry['topics']) < 4:
        # print(f'Ignoring event with less than 4 topics: {transactionHash}')
        continue

    print(f'------------- {transactionHash} ------------')
    registryAddress = entry['address']
    fromAddress = entry['topics'][1].hex()
    toAddress = entry['topics'][2].hex()
    tokenId = int.from_bytes(bytes(entry['topics'][3]), 'big')
    print(f'Transferred {tokenId} from {fromAddress} to {toAddress}')

    transaction = w3.eth.get_transaction(transactionHash)
    gasLimit = transaction['gas']
    gasPrice = transaction['gasPrice']
    value = transaction['value']

    transactionReceipt = w3.eth.getTransactionReceipt(transactionHash)
    gasUsed = transactionReceipt['gasUsed']
    print(f'Paid {value / 100000000000000000.0}Ξ ({gasUsed * gasPrice / 100000000000000000.0}Ξ) to {registryAddress}')

    print(f'OpenSea url: https://opensea.io/assets/{registryAddress}/{tokenId}')
    print(f'OpenSea api url: https://api.opensea.io/api/v1/asset/{registryAddress}/{tokenId}')
