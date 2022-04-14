import base64
from core import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import boto3
from async_timeout import asyncio
from core.requester import Requester
from core.s3_manager import S3Manager
from core.web3.eth_client import RestEthClient

from notd.collection_processor import CollectionProcessor
from notd.model import RetrievedCollection


async def main():
    s3Client = boto3.client(service_name='s3', region_name='eu-west-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    s3manager = S3Manager(s3Client=s3Client)
    requester = Requester()
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    requester = Requester()
    openseaApiKey = os.environ['OPENSEA_API_KEY']
    collectionProcessor = CollectionProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, openseaApiKey=openseaApiKey, bucketName=os.environ['S3_BUCKET'])

    #HAs No contractURI
    result = await collectionProcessor.retrieve_collection('0xE3f92992BB4F0f0D173623A52b2922d65172601d')
    expected = RetrievedCollection(address='0xE3f92992BB4F0f0D173623A52b2922d65172601d', name='Knights of Degen', symbol='KNIGHTS', description='8,888 NFT Degens who love sports, betting, alpha and nfts ⚔️', imageUrl='https://lh3.googleusercontent.com/yxdb_995UrIS6W9YIHMfMCRsdYRqcITlBvO5w7OoUx35rkClUeq9rPCvTMXdtw_zION07O_qRZSuNfZu6R6o8bI_KmbrfThhFtA4SBc=s120', twitterUsername='knightsofdegen', instagramUsername=None, wikiUrl=None, openseaSlug='knights-of-degen-official', url='https://www.knightsofdegen.io/', discordUrl='https://discord.gg/knightsofdegen', bannerImageUrl='https://lh3.googleusercontent.com/328JHSQ2nPpzfTxpZjV5xiiBp6R17GgUdjHJ7BF0mU-SH0Ou1LiiYmcET0WeHt26LD4tVXenIvYZD7VC8jV__bqRCiA_CzmWfwg7=s2500', doesSupportErc721=True, doesSupportErc1155=False)
    assert (result == expected)

    result = await collectionProcessor.retrieve_collection('0xd153f0014db6d1F339c6340d2C9F59214355D9d7')
    expected = RetrievedCollection(address='0xd153f0014db6d1F339c6340d2C9F59214355D9d7', name='Crypto Hobos', symbol='CryptoHobos', description='Crypto Hobos Pet Partners: https://opensea.io/collection/crypto-hobos-pet-partners\n\nThe first generative NFT project to be painted by hand, Crypto Hobos fuses the fine art and profile picture genres of the NFT space.\nArtist Valiahmed Popov has destroyed the source paintings of the over 200 traits that comprise the project, and so the 8000 original Crypto Hobos now exist solely on the Ethereum blockchain in the form of ERC-721 tokens.', imageUrl='https://lh3.googleusercontent.com/VLkOkaJ9QuVwHahQqHUrI5ZDVEqNBLCK_xEnMv4rBZ7kciwtlj_klhcwmvi5mM77hn5uSS10uVZH_9uNjkwpshppFhmNFc3a-r3YMuI=s120', twitterUsername='CryptoHobos', instagramUsername='cryptohobos', wikiUrl=None, openseaSlug='crypto-hobos', url='https://cryptohobos.io/', discordUrl='https://discord.gg/uFpbRYxMeA', bannerImageUrl='https://lh3.googleusercontent.com/kiqCwFkf5RWIl_jiJJ5hiElKTV4UYXlcATldxYZ4zr0E2XHiaDOwixPGLs-Led2DFBgQx26dd3AmhON914jllitPE0zZu2dYWF4w=s2500', doesSupportErc721=True, doesSupportErc1155=False)
    assert (result == expected)

    #Has ContractURI
    result = await collectionProcessor.retrieve_collection('0x3E3bF91740a8363D9433c8d3535B9b3C9E55f669')
    expected = RetrievedCollection(address='0x3E3bF91740a8363D9433c8d3535B9b3C9E55f669', name='Civit Illustrations', symbol='CIV20', description='Series of digital illustrations and animations', imageUrl='QmXKBRxpTFdRsqLDRUxXNoTJRChwcEQAqQVF8LXKaXmMTf', twitterUsername='ascii_bit', instagramUsername=None, wikiUrl=None, openseaSlug='civit-illustrations', url='https://app.rarible.com/collection/0x3e3bf91740a8363d9433c8d3535b9b3c9e55f669', discordUrl='https://discord.gg/CIVIT', bannerImageUrl='https://lh3.googleusercontent.com/zJOeUEKzl2Rs2JiGOxlZQR5WUru-6I-a8n_sp22USaBVxt0LxeYTe-xSfQhjIK8N6u1SyRaEfRWnyp9j-nDpPfeJWxNgSeDwziAI6Q=s2500', doesSupportErc721=True, doesSupportErc1155=False)
    assert (result == expected)

    result = await collectionProcessor.retrieve_collection('0xDb68Df0e86Bc7C6176E6a2255a5365f51113BCe8')
    expected = RetrievedCollection(address='0xDb68Df0e86Bc7C6176E6a2255a5365f51113BCe8', name='Rope Makers United', symbol='RMU', description='Rope Makers United Storefront', imageUrl='https://rope.lol/images/RopeLogo3D.gif', twitterUsername='dontbuyrope', instagramUsername=None, wikiUrl=None, openseaSlug='rope-makers-united', url='https://rope.lol', discordUrl='https://discord.gg/kWE5G2', bannerImageUrl=None, doesSupportErc721=False, doesSupportErc1155=True)
    assert (result == expected)

    # Has no Name or Symbol
    result = await collectionProcessor.retrieve_collection('0x12F01AF7FBEAFB088E1d3384BFf67390f41E8404')
    expected = RetrievedCollection(address='0x12F01AF7FBEAFB088E1d3384BFf67390f41E8404', name='FVCK_BAEIGE//', symbol=None, description='Collaborative contract between Baeige and Fvckrender', imageUrl='https://lh3.googleusercontent.com/BJECOBeDJqpaVLWgxza8DYaP9SQGq6h7kLFsOUAlTk3G7naycl4GsjjALsnCPayhHTlctEkvChvpxhGWfDh0hiH2-xd9eUU_yBqmYQ=s120', twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug='unidentified-contract-b46angemew', url=None, discordUrl=None, bannerImageUrl='https://lh3.googleusercontent.com/BJECOBeDJqpaVLWgxza8DYaP9SQGq6h7kLFsOUAlTk3G7naycl4GsjjALsnCPayhHTlctEkvChvpxhGWfDh0hiH2-xd9eUU_yBqmYQ=s2500', doesSupportErc721=False, doesSupportErc1155=True)
    assert (result == expected)

    result = await collectionProcessor.retrieve_collection('0x236E7Af5FcAb94770E621c97a1E58b4d0143E95B')
    expected = RetrievedCollection(address='0x236E7Af5FcAb94770E621c97a1E58b4d0143E95B', name="Ethernity's Master Collection", symbol=None, description="Ethernity's Master Collection of Exclusive NFTs on Opensea.", imageUrl='https://lh3.googleusercontent.com/GId53RudYB4l7e6Irj3_5JGyC3bwybdotwXAEgGaq4KCqjtfQChbolTQSJRYzb1bYrHM_G9xH4Il9vh_CM3ZPtMTwSgtkU5Wu7RVVQ=s120', twitterUsername='ethernitychain', instagramUsername=None, wikiUrl=None, openseaSlug='ethernity-master', url='http://ethernity.io', discordUrl='https://discord.gg/EthernityChain', bannerImageUrl='https://lh3.googleusercontent.com/xWwplVCKh2mIkbsHObxlVWPkW-kT0vlptGihpjaqyU4zTvAD90BwkcnTe25sPQuNlreb3cfT_LgRlYiuqLVJD0YYYWipq1s42A0T=s2500', doesSupportErc721=False, doesSupportErc1155=True)
    assert (result == expected)

    #dynamic contractURI
    result = await collectionProcessor.retrieve_collection('0x700CE4AB68aD109224Be3aC85f5A99213bf04f67')
    expected = RetrievedCollection(address='0x700CE4AB68aD109224Be3aC85f5A99213bf04f67', name='Microdoses', symbol='DOSES', description='Smaller graphics and topical comics from Killer Acid, in small editions. ', imageUrl='ipfs://ipfs/QmQ52XALRGEfRKCjDryeqXkq5nnSnDuRaiGaLwhs3R77Dz', twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug='microdoses', url='https://app.rarible.com/collection/0x700ce4ab68ad109224be3ac85f5a99213bf04f67', discordUrl=None, bannerImageUrl=None, doesSupportErc721=False, doesSupportErc1155=True)

    result = await collectionProcessor.retrieve_collection('0x48531836e57bc28d6fee33840f43826b889aa2fc')
    expected = RetrievedCollection(address='0x48531836e57bc28d6fee33840f43826b889aa2fc', name='Super Crypto Man', symbol='PIPPI', description='New generation of Japanese sticker culture × NFT.Making 3D Collective NFT with Cryptoworld as a theme. ', imageUrl='ipfs://ipfs/QmUvzee6ZvY41S5W842fm8wiFr8ueqQSDimfLQhHyp76Tk', twitterUsername='@Pippi_NFTart', instagramUsername=None, wikiUrl=None, openseaSlug='super-crypto-man', url='https://app.rarible.com/collection/0x48531836e57bc28d6fee33840f43826b889aa2fc', discordUrl=None, bannerImageUrl='https://lh3.googleusercontent.com/TvePJaCzrlt4m-kNSiD0HUkryq5wTYlU0vkugYC9F0CBhThEO2PGCN0m6BRawoNDF2RWNn3E0AixFsSefikyr-5tmWIZkLHoPmxQ-w=s2500', doesSupportErc721=False, doesSupportErc1155=True)

    result =     await collectionProcessor.retrieve_collection('0xDD97c0b7ED3DC93d09A681dE0E7228b5dfEAE463')
    expected = RetrievedCollection(address='0xDD97c0b7ED3DC93d09A681dE0E7228b5dfEAE463', name='Beanterra', symbol='BEANEL', description='Beanels of Beanterra - Diverse and lovable creatures that roam the realm filled with lush landscapes, snow-capped mountains, and deep blue oceans.', imageUrl='https://lh3.googleusercontent.com/ZT-Zq2CWSG0mBzzeeTCsAdMFVyu3au6sPyN_v3CVYXguuI19EL0JrB9QVgg-3tFMJxvg2FJbtpjM8iz5n77tC_gg4t37y-9UP7dQmmA=s120', twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug='beanterra', url='https://beanterra.io/', discordUrl='https://discord.gg/beanterra', bannerImageUrl='https://lh3.googleusercontent.com/tBVqF5do5ZpKVqqM6qgcyU44u_Utin0JAH_ygwaqVXMDq3KtsfxG10xXtYliGz6rhjEfngx4eb8LA8IcHn7U2oH_5WlRt9JIUZea7Oc=s2500', doesSupportErc721=True, doesSupportErc1155=False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
