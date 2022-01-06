import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
import logging
from core.requester import Requester
from core.web3.eth_client import RestEthClient
import datetime


from notd.block_processor import BlockProcessor
from notd.model import  RetrievedTokenTransfer



async def main():
    requester = Requester()
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    blockProcessor = BlockProcessor(ethClient=ethClient)

    result = await blockProcessor.get_transfers_in_block(13281280)
    expected = [
        RetrievedTokenTransfer(transactionHash='0x3a59e929b3dcdfd412ee35cb0d88a9b13693e38869d976bef92569e249b89dee', registryAddress='0x33825285eB66c11237Cc68CC182c1e9BF01bA00B', fromAddress='0x857784eA852149c21aD6025E94b715E753Cc2124', toAddress='0xF8ca0a9aAdfBD7470B77DB6D2498CDE243ba8420', tokenId='4973', value=164900000000000000, gasLimit=236924, gasPrice=58300000000, gasUsed=172508, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)),
        RetrievedTokenTransfer(transactionHash='0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef', registryAddress='0x2216d47494E516d8206B70FCa8585820eD3C4946', fromAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', toAddress='0x0000000000000000000000000000000000080085', tokenId='14364', value=0, gasLimit=449751, gasPrice=48786337690, gasUsed=271034, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)),
        RetrievedTokenTransfer(transactionHash='0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef', registryAddress='0x2216d47494E516d8206B70FCa8585820eD3C4946', fromAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', toAddress='0x0000000000000000000000000000000000080085', tokenId='10626', value=0, gasLimit=449751, gasPrice=48786337690, gasUsed=271034, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)),
        RetrievedTokenTransfer(transactionHash='0xf1f0758d54474efb810e470592349703adc758c5037e56ae1bd6a789e9a079ef', registryAddress='0x2216d47494E516d8206B70FCa8585820eD3C4946', fromAddress='0xffF8f66e26ac1A75F2b5Da49c247f3Ec0D0EA5ba', toAddress='0x0000000000000000000000000000000000080085', tokenId='10627', value=0, gasLimit=449751, gasPrice=48786337690, gasUsed=271034, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)),
        RetrievedTokenTransfer(transactionHash='0xfb9e13d47dc451e8c080245488771a5589bc1e461a2911c8dcfd713267df5dbc', registryAddress='0xF8C08433DD41eAeE2e424C9E91467aB27772d9ec', fromAddress='0x44F360a7771888B5Ad92677D795aA10EA88203CA', toAddress='0x62F56981d431e68B5CAb37ae3A242a72824D3ac7', tokenId='97', value=0, gasLimit=60316, gasPrice=46000000000, gasUsed=41597, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)),
        RetrievedTokenTransfer(transactionHash='0x786dedd3df009705c246629c864e839b78b897319d346540f10bb84dabbacbb4', registryAddress='0xC00d444eeD049ad0d858a4A8D6Cac5417054405D', fromAddress='0x089660619d26b6CA62EaCD74e2DdD6089024fcCc', toAddress='0xa1F39F1a900A44DDFC702f9071808a07B841f377', tokenId='1681', value=9000000000000000, gasLimit=331269, gasPrice=45871801906, gasUsed=235481, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)),
        RetrievedTokenTransfer(transactionHash='0x35bf97445892e633811b0251cba7056f0f6d00d127b38e3414f9b219839a0d5a', registryAddress='0x06012c8cf97BEaD5deAe237070F9587f8E7A266d', fromAddress='0xb1690C08E213a35Ed9bAb7B318DE14420FB57d8C', toAddress='0x52b2A1cc5BF5701408A0aAB889fB5ab2Cf65275b', tokenId='938228', value=19857666997354498, gasLimit=168463, gasPrice=45721801906, gasUsed=96944, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)), 
        RetrievedTokenTransfer(transactionHash='0x5f240c53fafdf13e16ea02c3e94b8daec4c0d36272ea5cc639a211e344afd6c8', registryAddress='0xa64C5EC80784675bf289A4722a2eca180212f9dB', fromAddress='0x57B386815E928BBF43aB16cfD7f268E7f861c0AA', toAddress='0xf3E09Fa1754c77aECe0808197b2cAAE896b1C3eD', tokenId='1718', value=50000000000000000, gasLimit=312990, gasPrice=45721801906, gasUsed=226220, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9)),
        RetrievedTokenTransfer(transactionHash='0xd913164a0166140027e68fad832d1942cde756709c778697844f9ab10eb35e4c', registryAddress='0xC36442b4a4522E871399CD717aBDD847Ab11FE88', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x6B33a55786b2412c5283bfFc0383Ca35D702B388', tokenId='130999', value=479676176628488569, gasLimit=626642, gasPrice=45681801906, gasUsed=493984, blockNumber=13281280, blockHash='0x79da1d97baead833e2b4e597a24d08a0e5efddd2c7f0983f776836a8ffb03d4c', blockDate=datetime.datetime(2021, 9, 23, 10, 50, 9))
    ]
    assert result == expected

    result = await blockProcessor.get_transfers_in_block(12839305)
    expected = [
        RetrievedTokenTransfer(transactionHash='0xfc8ffb7652d77c1b880a80134bdce050c9bf712610fa9dc0d3d3fa83c10d3a1b', registryAddress='0xFBB6684EbD6093989740e8ef3e7D57cf3813E5a4', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x18090cDA49B21dEAffC21b4F886aed3eB787d032', tokenId='9991', value=0, gasLimit=184165, gasPrice=40000000000, gasUsed=184165, blockNumber=12839305, blockHash='0x7e36a9f127f3413595ef0f1c4165e4547d20ab566b66fc51a3cbe9eb048f3154', blockDate=datetime.datetime(2021, 7, 16, 18, 41, 41)),
        RetrievedTokenTransfer(transactionHash='0x3093bb2c8cbf1d229594d2cb8b172558fb6730721d9ef561b6400543a59f3734', registryAddress='0x049aba7510f45BA5b64ea9E658E342F904DB358D', fromAddress='0x0000000000000000000000000000000000000000', toAddress='0x54A5A62D34d3C55Cb35Bb8B4d4C958c820c5f322', tokenId='111875105896522767201998009571114989808106447240989160672650322275489228602620', value=0, gasLimit=147908, gasPrice=40000000000, gasUsed=115697, blockNumber=12839305, blockHash='0x7e36a9f127f3413595ef0f1c4165e4547d20ab566b66fc51a3cbe9eb048f3154', blockDate=datetime.datetime(2021, 7, 16, 18, 41, 41)),
        RetrievedTokenTransfer(transactionHash='0x7d15427902a0ae5cb45b20cb38ab4ef0aab204ba1e4ae120f2b3b4d1c40cb688', registryAddress='0x395E5461693e0bB5EC78302605030050f69e628d', fromAddress='0x913C7fa57e6690f96B4AEB65553f0ED3664CAF8b', toAddress='0xA8E3582964ffA96621a767468b1D66207211df00', tokenId='1861', value=0, gasLimit=97681, gasPrice=40000000000, gasUsed=82681, blockNumber=12839305, blockHash='0x7e36a9f127f3413595ef0f1c4165e4547d20ab566b66fc51a3cbe9eb048f3154', blockDate=datetime.datetime(2021, 7, 16, 18, 41, 41))
    ]
    assert result == expected

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
