from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/8a99199d9b7b4a8f8908a7c7a0614df9'))

w3.eth.getBlock('latest')

# Get the ETH balance of an address 
w3.eth.getBalance('YOUR_ADDRESS_HERE')
