import asyncio
import datetime
import os
import sys

from core import logging
from core.aws_requester import AwsRequester
from core.requester import Requester
from core.web3.eth_client import RestEthClient
from sqlalchemy import values

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.block_processor import BlockProcessor
from notd.model import ProcessedBlock, RetrievedTokenTransfer

#################################################################################################################################################################
#Test process_transactions
#################################################################################################################################################################
async def get_block_data(ethClient,blockNumber):
    return await ethClient.get_block(blockNumber=blockNumber, shouldHydrateTransactions=True)

async def main():
    requester = Requester()
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    blockProcessor = BlockProcessor(ethClient=ethClient)

    # Burning NFTs
    # https://etherscan.io/tx/0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef started by 0xfff8
    # 3 transfers with 0 value with 0x000 as the receiver and 0xfff as the sender
    blockData = await get_block_data(ethClient=ethClient,blockNumber=13281280)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef', registryAddress='0x2216d47494E516d8206B70FCa8585820eD3C4946', tokenId='14364', fromAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', toAddress='0x0000000000000000000000000000000000080085', operatorAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', amount=1, value=0, gasLimit=449751, gasPrice=48786337690, blockNumber=13281280, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef', registryAddress='0x2216d47494E516d8206B70FCa8585820eD3C4946', tokenId='10626', fromAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', toAddress='0x0000000000000000000000000000000000080085', operatorAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', amount=1, value=0, gasLimit=449751, gasPrice=48786337690, blockNumber=13281280, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef', registryAddress='0x2216d47494E516d8206B70FCa8585820eD3C4946', tokenId='10627', fromAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', toAddress='0x0000000000000000000000000000000000080085', operatorAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', amount=1, value=0, gasLimit=449751, gasPrice=48786337690, blockNumber=13281280, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)
    ]
    assert result == expected


    # Account buys multiple NFTs (of the same collection) from another account
    # https://etherscan.io/tx/0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954  started by 027a
    # 5 transfers each with (0.684/5)eth value with 0x27a as the receiver for each and multiple senders  
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14471751)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='3729', fromAddress='0xB8b6aF171335Ce2E327Afd2ebEf1a2c46cd67B01', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='3698', fromAddress='0x9c8BF4D407cff32eC725eb7D43E106163d182269', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='3534', fromAddress='0x30d82b3cB565Da738383356fd17E9306692Bd5b2', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='2539', fromAddress='0x1a63efB8E8b52e63F700038e17909Cf76AEf5415', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='130', fromAddress='0x40Fa37128A7d54DAB2392ACBC4f43827bc67bBE4', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)
    ]
    assert result == expected

    # Account buys multiple NFTs (of the same collection) from multiple accounts in one transaction started by 0x4ea
    # https://etherscan.io/tx/0x8b52d281485f735dbe910f76d92dd317549790f39778e9461c81f489ebd3763c
    # 5 transfers each with (1.338/5)eth value with 0x4ea as the receiver for each and multiple senders   
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14850684)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0x8b52d281485f735dbe910f76d92dd317549790f39778e9461c81f489ebd3763c':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0x8b52d281485f735dbe910f76d92dd317549790f39778e9461c81f489ebd3763c', registryAddress='0x64b6b4142d4D78E49D53430C1d3939F2317f9085', tokenId='4774', fromAddress='0xc955Ce75796eF64eB1F09e9eff4481c8968C9346', toAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', operatorAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', amount=1, value=446000000000000000, gasLimit=579311, gasPrice=53578026373, blockNumber=14850684, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x8b52d281485f735dbe910f76d92dd317549790f39778e9461c81f489ebd3763c', registryAddress='0x64b6b4142d4D78E49D53430C1d3939F2317f9085', tokenId='5660', fromAddress='0x38a48DDF98D3d6AF7fD46a692265D72515534525', toAddress='0xF97E9727d8E7DB7AA8f006D1742d107cF9411412', operatorAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', amount=1, value=0, gasLimit=579311, gasPrice=53578026373, blockNumber=14850684, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=True),
        RetrievedTokenTransfer(transactionHash='0x8b52d281485f735dbe910f76d92dd317549790f39778e9461c81f489ebd3763c', registryAddress='0x64b6b4142d4D78E49D53430C1d3939F2317f9085', tokenId='5660', fromAddress='0xF97E9727d8E7DB7AA8f006D1742d107cF9411412', toAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', operatorAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', amount=1, value=446000000000000000, gasLimit=579311, gasPrice=53578026373, blockNumber=14850684, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x8b52d281485f735dbe910f76d92dd317549790f39778e9461c81f489ebd3763c', registryAddress='0x64b6b4142d4D78E49D53430C1d3939F2317f9085', tokenId='5729', fromAddress='0x172458fF1b115ba5C2076465977Baf6152C5Ac72', toAddress='0xF97E9727d8E7DB7AA8f006D1742d107cF9411412', operatorAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', amount=1, value=0, gasLimit=579311, gasPrice=53578026373, blockNumber=14850684, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=True),
        RetrievedTokenTransfer(transactionHash='0x8b52d281485f735dbe910f76d92dd317549790f39778e9461c81f489ebd3763c', registryAddress='0x64b6b4142d4D78E49D53430C1d3939F2317f9085', tokenId='5729', fromAddress='0xF97E9727d8E7DB7AA8f006D1742d107cF9411412', toAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', operatorAddress='0x4eA1577b6c155A588A6c18767E6FAaEF51091aC2', amount=1, value=446000000000000000, gasLimit=579311, gasPrice=53578026373, blockNumber=14850684, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)
    ]
    assert result == expected

    # Account buys multiple NFTs (of the different collections) from another account
    # https://etherscan.io/tx/0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170 started by 0x9e56
    # Transfer of 2 SANDBOX tokens: value=0 from 0xf91 to 0x9e5 isMultiAddressTransfer=true
    # Transfer of 5 SANDBOX ASSET tokens: value=0 from 0xf91 to 0x9e5 isMultiAddressTransfer=true
    blockData = await get_block_data(ethClient=ethClient,blockNumber=11003194)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170', registryAddress='0x50f5474724e0Ee42D9a4e711ccFB275809Fd6d4a', tokenId='100834', fromAddress='0xF91B20739309040c93eCD70ae8a7dAC4728d2Fbc', toAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', operatorAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', amount=1, value=0, gasLimit=743176, gasPrice=121000000000, blockNumber=11003194, tokenType='erc721', isMultiAddress=True, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170', registryAddress='0x50f5474724e0Ee42D9a4e711ccFB275809Fd6d4a', tokenId='91489', fromAddress='0xF91B20739309040c93eCD70ae8a7dAC4728d2Fbc', toAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', operatorAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', amount=1, value=0, gasLimit=743176, gasPrice=121000000000, blockNumber=11003194, tokenType='erc721', isMultiAddress=True, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170', registryAddress='0x067a1Eb5E383eD24b66D72aAf80d8D7dB3d299A8', tokenId='55464657044963196816950587289035428064568320970692304673817341489687446964224', fromAddress='0xF91B20739309040c93eCD70ae8a7dAC4728d2Fbc', toAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', operatorAddress='0x9E2d8A4847547e02624F34A309cC5BD4E56C2b31', amount=1, value=0, gasLimit=743176, gasPrice=121000000000, blockNumber=11003194, tokenType='erc1155single', isMultiAddress=True, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170', registryAddress='0x067a1Eb5E383eD24b66D72aAf80d8D7dB3d299A8', tokenId='55464657044963196816950587289035428064568320970692304673817341489687446964225', fromAddress='0xF91B20739309040c93eCD70ae8a7dAC4728d2Fbc', toAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', operatorAddress='0x9E2d8A4847547e02624F34A309cC5BD4E56C2b31', amount=1, value=0, gasLimit=743176, gasPrice=121000000000, blockNumber=11003194, tokenType='erc1155single', isMultiAddress=True, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170', registryAddress='0x067a1Eb5E383eD24b66D72aAf80d8D7dB3d299A8', tokenId='55464657044963196816950587289035428064568320970692304673817341489687446964226', fromAddress='0xF91B20739309040c93eCD70ae8a7dAC4728d2Fbc', toAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', operatorAddress='0x9E2d8A4847547e02624F34A309cC5BD4E56C2b31', amount=1, value=0, gasLimit=743176, gasPrice=121000000000, blockNumber=11003194, tokenType='erc1155single', isMultiAddress=True, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170', registryAddress='0x067a1Eb5E383eD24b66D72aAf80d8D7dB3d299A8', tokenId='55464657044963196816950587289035428064568320970692304673817341489687446964227', fromAddress='0xF91B20739309040c93eCD70ae8a7dAC4728d2Fbc', toAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', operatorAddress='0x9E2d8A4847547e02624F34A309cC5BD4E56C2b31', amount=1, value=0, gasLimit=743176, gasPrice=121000000000, blockNumber=11003194, tokenType='erc1155single', isMultiAddress=True, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd40859bfc1ce80da0e81b8f82b15db1222f6937d108daca7f259e3dd162c5170', registryAddress='0x067a1Eb5E383eD24b66D72aAf80d8D7dB3d299A8', tokenId='55464657044963196816950587289035428064568320970692304673817341489687446964230', fromAddress='0xF91B20739309040c93eCD70ae8a7dAC4728d2Fbc', toAddress='0x9e56C62aa6185A8b7F30DAf5be0EA05718DB6997', operatorAddress='0x9E2d8A4847547e02624F34A309cC5BD4E56C2b31', amount=1, value=0, gasLimit=743176, gasPrice=121000000000, blockNumber=11003194, tokenType='erc1155single', isMultiAddress=True, isInterstitialTransfer=False)
    ]
    assert result == expected


    # Account buys an NFT but there are interstitial transfers in the same transaction
    # https://etherscan.io/tx/0x6bb37dcb9a60ed49da56ccfb21dfcae886e81debd3ab94d73497d62744e758d2 started by 0x04c
    # Transfer of token 5309..: value=0 from 0x000 to 0x283 isInterstitial=true
    # Transfer of token 5309..: value=0.0014 from 0x283 to 0x04c
    blockData = await get_block_data(ethClient=ethClient,blockNumber=13898509)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0x6bb37dcb9a60ed49da56ccfb21dfcae886e81debd3ab94d73497d62744e758d2':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0x6bb37dcb9a60ed49da56ccfb21dfcae886e81debd3ab94d73497d62744e758d2', registryAddress='0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85', tokenId='53091478429947851570161017064535674537231673781900674689421707367586767084753', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x283Af0B28c62C092C9727F1Ee09c02CA627EB7F5', operatorAddress='0x04c1f61baF8DE8DA75DB52f09D9d92a1592f46eA', amount=1, value=0, gasLimit=295604, gasPrice=79444034756, blockNumber=13898509, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=True), 
        RetrievedTokenTransfer(transactionHash='0x6bb37dcb9a60ed49da56ccfb21dfcae886e81debd3ab94d73497d62744e758d2', registryAddress='0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85', tokenId='53091478429947851570161017064535674537231673781900674689421707367586767084753', fromAddress='0x283Af0B28c62C092C9727F1Ee09c02CA627EB7F5', toAddress='0x04c1f61baF8DE8DA75DB52f09D9d92a1592f46eA', operatorAddress='0x04c1f61baF8DE8DA75DB52f09D9d92a1592f46eA', amount=1, value=1446765707746493, gasLimit=295604, gasPrice=79444034756, blockNumber=13898509, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)
    ]
    assert result == expected

    # https://etherscan.io/tx/0xafd0535c4fe269b57cdcd4489eb11f05ff42dce04190b3e65f659ab9f05b71ee started by 0x92a
    # Transfer of token 5309..: value=0 from 0x393 to 0x000 isInterstitial=true
    # Transfer of token 5309..: value=0 from 0x000 to 0x283 isInterstitial=true
    # Transfer of token 5309..: value=0.005 from 0x283 to 0x04c
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14471751)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0xafd0535c4fe269b57cdcd4489eb11f05ff42dce04190b3e65f659ab9f05b71ee':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0xafd0535c4fe269b57cdcd4489eb11f05ff42dce04190b3e65f659ab9f05b71ee', registryAddress='0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85', tokenId='78102327257348450385369200690909064778782768687076101371929764792747181439823', fromAddress='0x393E7176be67D8FaBA18B2c1C52eb827AA90a824', toAddress='0x0000000000000000000000000000000000000000', operatorAddress='0x92a2eAc2d5d442e489597cdBFEf75514fB97b4c0', amount=1, value=0, gasLimit=245377, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=True),
        RetrievedTokenTransfer(transactionHash='0xafd0535c4fe269b57cdcd4489eb11f05ff42dce04190b3e65f659ab9f05b71ee', registryAddress='0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85', tokenId='78102327257348450385369200690909064778782768687076101371929764792747181439823', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x283Af0B28c62C092C9727F1Ee09c02CA627EB7F5', operatorAddress='0x92a2eAc2d5d442e489597cdBFEf75514fB97b4c0', amount=1, value=0, gasLimit=245377, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=True),
        RetrievedTokenTransfer(transactionHash='0xafd0535c4fe269b57cdcd4489eb11f05ff42dce04190b3e65f659ab9f05b71ee', registryAddress='0x57f1887a8BF19b14fC0dF6Fd9B2acc9Af147eA85', tokenId='78102327257348450385369200690909064778782768687076101371929764792747181439823', fromAddress='0x283Af0B28c62C092C9727F1Ee09c02CA627EB7F5', toAddress='0x92a2eAc2d5d442e489597cdBFEf75514fB97b4c0', operatorAddress='0x92a2eAc2d5d442e489597cdBFEf75514fB97b4c0', amount=1, value=5020756571078947, gasLimit=245377, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)]
    assert result == expected

    # Account buys multiple NFTs (of the same collection) from multiple accounts, but there are some interstitial transfers in the same transaction
    # https://etherscan.io/tx/0xd7721e7d21313f791ad279d806d9b506fe4acfc6bfbd0dec3436ce640ebc299d started by 0xdfd
    # Transfer of token 7723: value=0 from 0x505 to 0x83c isInterstitial=true
    # Transfer of token 7723: value=(5.73/3) from 0x83c to 0xdfd 
    # Transfer of token 3624: value=0 from 0xfa8 to 0x83c isInterstitial=true
    # Transfer of token 3624: value=(5.73/3) from 0x83c to 0xdfd 
    # Transfer of token 220: value=(5.73/3) from 0x9dc to 0xdfd 
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14806164)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0xd7721e7d21313f791ad279d806d9b506fe4acfc6bfbd0dec3436ce640ebc299d':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0xd7721e7d21313f791ad279d806d9b506fe4acfc6bfbd0dec3436ce640ebc299d', registryAddress='0x160C404B2b49CBC3240055CEaEE026df1e8497A0', tokenId='220', fromAddress='0x9dC874b1194b144e7C90C9ABA0b6A510353FD130', toAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', operatorAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', amount=1, value=1910000000000000000, gasLimit=754081, gasPrice=21536358794, blockNumber=14806164, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd7721e7d21313f791ad279d806d9b506fe4acfc6bfbd0dec3436ce640ebc299d', registryAddress='0x160C404B2b49CBC3240055CEaEE026df1e8497A0', tokenId='7723', fromAddress='0x5054A3283e57Cc1bd1109F596a0a5a31887D56FB', toAddress='0x83C8F28c26bF6aaca652Df1DbBE0e1b56F8baBa2', operatorAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', amount=1, value=0, gasLimit=754081, gasPrice=21536358794, blockNumber=14806164, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=True),
        RetrievedTokenTransfer(transactionHash='0xd7721e7d21313f791ad279d806d9b506fe4acfc6bfbd0dec3436ce640ebc299d', registryAddress='0x160C404B2b49CBC3240055CEaEE026df1e8497A0', tokenId='7723', fromAddress='0x83C8F28c26bF6aaca652Df1DbBE0e1b56F8baBa2', toAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', operatorAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', amount=1, value=1910000000000000000, gasLimit=754081, gasPrice=21536358794, blockNumber=14806164, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0xd7721e7d21313f791ad279d806d9b506fe4acfc6bfbd0dec3436ce640ebc299d', registryAddress='0x160C404B2b49CBC3240055CEaEE026df1e8497A0', tokenId='3624', fromAddress='0xfa880465C4C1bd5bDf77C06F71bC0d5F77D383AD', toAddress='0x83C8F28c26bF6aaca652Df1DbBE0e1b56F8baBa2', operatorAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', amount=1, value=0, gasLimit=754081, gasPrice=21536358794, blockNumber=14806164, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=True),
        RetrievedTokenTransfer(transactionHash='0xd7721e7d21313f791ad279d806d9b506fe4acfc6bfbd0dec3436ce640ebc299d', registryAddress='0x160C404B2b49CBC3240055CEaEE026df1e8497A0', tokenId='3624', fromAddress='0x83C8F28c26bF6aaca652Df1DbBE0e1b56F8baBa2', toAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', operatorAddress='0xDFD521971212e789b5FF05EF8D9F324fE290e238', amount=1, value=1910000000000000000, gasLimit=754081, gasPrice=21536358794, blockNumber=14806164, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)]
    assert result == expected

   
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14471751)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='3729', fromAddress='0xB8b6aF171335Ce2E327Afd2ebEf1a2c46cd67B01', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='3698', fromAddress='0x9c8BF4D407cff32eC725eb7D43E106163d182269', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='3534', fromAddress='0x30d82b3cB565Da738383356fd17E9306692Bd5b2', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='2539', fromAddress='0x1a63efB8E8b52e63F700038e17909Cf76AEf5415', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x7e2d9da491c020a15ed394899a1344560649ce9b07b7a195c425d7b218551954', registryAddress='0xAcfA101ECE167F1894150e090d9471aeE2dD3041', tokenId='130', fromAddress='0x40Fa37128A7d54DAB2392ACBC4f43827bc67bBE4', toAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', operatorAddress='0x27a45e97c01f30D3E3F7f76734BB8d8b9AF03Eb0', amount=1, value=137880000000000000, gasLimit=963497, gasPrice=24985808182, blockNumber=14471751, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)]
    assert result == expected

    # Account buying an NFT with ERC-20 not eth
    # https://etherscan.io/tx/0xdfc7fa60b02bb76f021e1ddd7ce61ba654f0fa5df6214fcc412935fd95fa8705 started by 0x400
    # Transfer of 219281: value=0.015 from 0x000 to 0x400
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14550945)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0xdfc7fa60b02bb76f021e1ddd7ce61ba654f0fa5df6214fcc412935fd95fa8705':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [RetrievedTokenTransfer(transactionHash='0xdfc7fa60b02bb76f021e1ddd7ce61ba654f0fa5df6214fcc412935fd95fa8705', registryAddress='0xC36442b4a4522E871399CD717aBDD847Ab11FE88', tokenId='219281', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x400815b954C964C3BC356E5541301D957D417EC9', operatorAddress='0x400815b954C964C3BC356E5541301D957D417EC9', amount=1, value=15677481882371820, gasLimit=495462, gasPrice=32756055350, blockNumber=14550945, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)]
    assert result == expected

    # Account accepts and offer for purchase in ERC-20 not eth
    # https://etherscan.io/tx/0x09890dfbd47c251f16088ce6f995228d5f864f43ce620b70edd6fd852be9d4e1 started by 0x283
    # Transfer of 9571: value=0 (goal:1.15) from 0x283 to 0x28a
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14851881)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0x09890dfbd47c251f16088ce6f995228d5f864f43ce620b70edd6fd852be9d4e1':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [RetrievedTokenTransfer(transactionHash='0x09890dfbd47c251f16088ce6f995228d5f864f43ce620b70edd6fd852be9d4e1', registryAddress='0xfE8C6d19365453D26af321D0e8c910428c23873F', tokenId='9571', fromAddress='0x283929Fa5fcFaf27D9898FD867A78Fb5a8B44b5F', toAddress='0x28ad7d7838E693d05B64d516171ea0D3Bd67b70b', operatorAddress='0x283929Fa5fcFaf27D9898FD867A78Fb5a8B44b5F', amount=1, value=0, gasLimit=293512, gasPrice=74122712424, blockNumber=14851881, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)]
    assert result == expected

    # Account buys NFTs for another account
    # https://etherscan.io/tx/0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b started by 0xbd9
    # 7 Transfers: value=(0.4816/7) from 0x000 0x126
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14853186)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b', registryAddress='0x5b42A31DcB0718a1EEf25Ed2600475A97bF1fE65', tokenId='201', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x126449dE757B50714C04D01434492B3c7090f8cb', operatorAddress='0xbd9FF6eb3E115E8EB19aaAdfB71807E76274990B', amount=1, value=68800000000000000, gasLimit=1043788, gasPrice=24437785018, blockNumber=14853186, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b', registryAddress='0x5b42A31DcB0718a1EEf25Ed2600475A97bF1fE65', tokenId='202', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x126449dE757B50714C04D01434492B3c7090f8cb', operatorAddress='0xbd9FF6eb3E115E8EB19aaAdfB71807E76274990B', amount=1, value=68800000000000000, gasLimit=1043788, gasPrice=24437785018, blockNumber=14853186, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b', registryAddress='0x5b42A31DcB0718a1EEf25Ed2600475A97bF1fE65', tokenId='203', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x126449dE757B50714C04D01434492B3c7090f8cb', operatorAddress='0xbd9FF6eb3E115E8EB19aaAdfB71807E76274990B', amount=1, value=68800000000000000, gasLimit=1043788, gasPrice=24437785018, blockNumber=14853186, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b', registryAddress='0x5b42A31DcB0718a1EEf25Ed2600475A97bF1fE65', tokenId='204', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x126449dE757B50714C04D01434492B3c7090f8cb', operatorAddress='0xbd9FF6eb3E115E8EB19aaAdfB71807E76274990B', amount=1, value=68800000000000000, gasLimit=1043788, gasPrice=24437785018, blockNumber=14853186, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b', registryAddress='0x5b42A31DcB0718a1EEf25Ed2600475A97bF1fE65', tokenId='205', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x126449dE757B50714C04D01434492B3c7090f8cb', operatorAddress='0xbd9FF6eb3E115E8EB19aaAdfB71807E76274990B', amount=1, value=68800000000000000, gasLimit=1043788, gasPrice=24437785018, blockNumber=14853186, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b', registryAddress='0x5b42A31DcB0718a1EEf25Ed2600475A97bF1fE65', tokenId='206', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x126449dE757B50714C04D01434492B3c7090f8cb', operatorAddress='0xbd9FF6eb3E115E8EB19aaAdfB71807E76274990B', amount=1, value=68800000000000000, gasLimit=1043788, gasPrice=24437785018, blockNumber=14853186, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x1a466fa7f3815776d272bdb70a2f0a306d8aa1d10953f98d9531e81c7bb7d36b', registryAddress='0x5b42A31DcB0718a1EEf25Ed2600475A97bF1fE65', tokenId='207', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x126449dE757B50714C04D01434492B3c7090f8cb', operatorAddress='0xbd9FF6eb3E115E8EB19aaAdfB71807E76274990B', amount=1, value=68800000000000000, gasLimit=1043788, gasPrice=24437785018, blockNumber=14853186, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)]
    assert result == expected

    # Account buys NFT from another account with ERC-721 token plus eth
    # https://etherscan.io/tx/0x466e880275ee3f815d0c0bd787009632a437eefe1e7e7dab753d21ea16c0bd8b started by 0xaf6
    # Transfer of token 7963 value=(0) from 0x13d to 0xaf6 isSwapTransfer=true
    # Transfer of token 7139 value=7eth from 0xaf6 to 0x023 isSwapTransfer=true
    blockData = await get_block_data(ethClient=ethClient,blockNumber=14806164)
    for transaction in blockData['transactions']:
        if transaction['hash'].hex() == '0x466e880275ee3f815d0c0bd787009632a437eefe1e7e7dab753d21ea16c0bd8b':
            result = (await blockProcessor.process_transaction(transaction=transaction))
            
    expected = [
        RetrievedTokenTransfer(transactionHash='0x466e880275ee3f815d0c0bd787009632a437eefe1e7e7dab753d21ea16c0bd8b', registryAddress='0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D', tokenId='7963', fromAddress='0x13d8faF4A690f5AE52E2D2C52938d1167057B9af', toAddress='0xAf6209795446f33492133dF966042BC2B568d866', operatorAddress='0xAf6209795446f33492133dF966042BC2B568d866', amount=1, value=3502500000000000000, gasLimit=515008, gasPrice=21442773112, blockNumber=14806164, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False),
        RetrievedTokenTransfer(transactionHash='0x466e880275ee3f815d0c0bd787009632a437eefe1e7e7dab753d21ea16c0bd8b', registryAddress='0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D', tokenId='7139', fromAddress='0xAf6209795446f33492133dF966042BC2B568d866', toAddress='0x0232d1083E970F0c78f56202b9A666B526FA379F', operatorAddress='0xAf6209795446f33492133dF966042BC2B568d866', amount=1, value=3502500000000000000, gasLimit=515008, gasPrice=21442773112, blockNumber=14806164, tokenType='erc721', isMultiAddress=False, isInterstitialTransfer=False)
        ]
    assert result == expected


    await requester.close_connections()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())