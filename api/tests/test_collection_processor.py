import base64
import logging
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from async_timeout import asyncio
import boto3

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
    expected = RetrievedCollection(address='0x3E3bF91740a8363D9433c8d3535B9b3C9E55f669', name='Civit Illustrations', symbol='CIV20', description=None, imageUrl='QmXKBRxpTFdRsqLDRUxXNoTJRChwcEQAqQVF8LXKaXmMTf', twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug=None, url='https://app.rarible.com/collection/0x3e3bf91740a8363d9433c8d3535b9b3c9e55f669', discordUrl=None, bannerImageUrl=None, doesSupportErc721=True, doesSupportErc1155=False)
    assert (result == expected)
    
    result = await collectionProcessor.retrieve_collection('0xDb68Df0e86Bc7C6176E6a2255a5365f51113BCe8')
    expected = RetrievedCollection(address='0xDb68Df0e86Bc7C6176E6a2255a5365f51113BCe8', name='Rope Makers United', symbol='RMU', description='Rope Makers United Storefront', imageUrl='https://rope.lol/images/RopeLogo3D.gif', twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug=None, url='https://rope.lol', discordUrl=None, bannerImageUrl=None, doesSupportErc721=False, doesSupportErc1155=True)
    assert (result == expected)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
