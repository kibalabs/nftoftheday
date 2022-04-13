import base64
import logging
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import datetime

from async_timeout import asyncio
from core.aws_requester import AwsRequester
from core.requester import Requester
from core.s3_manager import S3Manager
from core.web3.eth_client import RestEthClient
from core.store.database import Database

from notd.store.retriever import Retriever
from notd.block_processor import BlockProcessor
from notd.model import Collection
from notd.model import RetrievedCollection
from notd.model import RetrievedTokenMetadata
from notd.token_metadata_processor import TokenMetadataProcessor


async def main():
    s3manager = S3Manager(region='eu-west-1', accessKeyId=os.environ['AWS_KEY'],accessKeySecret=os.environ['AWS_SECRET'])
    requester = Requester()
    ethClient = RestEthClient(url=f'https://mainnet.infura.io/v3/{os.environ["INFURA_PROJECT_ID"]}', requester=requester)
    blockProcessor = BlockProcessor(ethClient=ethClient)
    requester = Requester()
    tokenMetadataProcessor = TokenMetadataProcessor(requester=requester, ethClient=ethClient, s3manager=s3manager, bucketName=os.environ['S3_BUCKET'])

    await s3manager.connect()
    result = tokenMetadataProcessor.get_default_token_metadata(registryAddress='0x57E9a39aE8eC404C08f88740A9e6E306f50c937f',tokenId=165)
    expected = RetrievedTokenMetadata(
        registryAddress='0x57E9a39aE8eC404C08f88740A9e6E306f50c937f', tokenId='165', metadataUrl=None, imageUrl=None,animationUrl=None, youtubeUrl=None, backgroundColor=None, name='#165', description=None, frameImageUrl=None, attributes=[]
    )
    assert (result == expected)

    collection = Collection(
        address='0x495f947276749Ce646f68AC8c248420045cb7b5e', name='OpenSea Shared Storefront', symbol='OPENSTORE', description=None, imageUrl=None, twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug=None, url=None, discordUrl=None, bannerImageUrl=None, doesSupportErc721=False, doesSupportErc1155=True, collectionId=9, createdDate=datetime.datetime(2022, 2, 10, 15, 35, 27, 493515), updatedDate=datetime.datetime(2022, 3, 10, 11, 20, 43, 69095)
    )
    result = await tokenMetadataProcessor.retrieve_token_metadata(
        registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='1027194722486925029699656604254821663009080914619475021175016778814206246913', collection=collection
    )
    expected = RetrievedTokenMetadata(
        registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='1027194722486925029699656604254821663009080914619475021175016778814206246913', metadataUrl='https://api.opensea.io/api/v1/metadata/0x495f947276749Ce646f68AC8c248420045cb7b5e/1027194722486925029699656604254821663009080914619475021175016778814206246913', name='LegacyPunks #117 Richard the Lionheart', description='Richard the Lionheart (1157-1199 AD), actually Richard I of England - but more commonly known as Lionheart due to his reputation as great military leader and warrior, was King of England from 1189 until his death in 1199 AD. Richard spent the majority of his life at war and eventually died in battle. He also ruled as Duke of Normandy, Aquitaine and Gascony, Lord of Cyprus, and Count of Poitiers, Anjou, Maine, and Nantes, and was overlord of Brittany at various times during the same period. Richard was a popular ruler and is perhaps best known for his attempt to retake Jerusalem from Saladin during the Third Crusade. Although, this Crusade did not successfully recapture Jerusalem, it achieved partial success in recapturing Acre, Jaffa, and reversing most of Saladin’s conquests. Regardless, Richard is much considered the winner of the Third Crusade after his famous victory at the Battle of Arsuf.', imageUrl='https://lh3.googleusercontent.com/3u7F2lRRhj9y4dd2-o9R8sfU7dYW6UQN4Vc4BOoH1JyrT5cAHPDF40Q2aPycYn1ZDoin3CnCVRgD2yHe82KYlmVX8Lbbw_YaFp1YyQ', animationUrl=None, youtubeUrl=None, backgroundColor=None, frameImageUrl=None, attributes=[]
    )
    assert (result == expected)

    collection = Collection(
        address='0x93317e87a3a47821803caadc54ae418af80603da', name='Cameo Pass', symbol='CAMEOPASS', description='Cameo Pass is a collection of NFTs granting access to Cameo in the metaverse,...', imageUrl='https://openseauserdata.com/files/7572aef06110b4e365817f60d37eff0d.svg', twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug='cameo-pass', url='http://pass.cameo.com', discordUrl='https://discord.gg/ssZeP6WBYg', bannerImageUrl='https://lh3.googleusercontent.com/HiSZHoavhCSzrmc2Un2y6QzSWk_wAWLz4sBr9G1Wjz6bGH8mDce_8rNlH-vRvM1xwbqS-_pSCsK99rrr8P-Es4FCkjvxETij8lojNw=s2500', doesSupportErc721=False, doesSupportErc1155=True, collectionId=64040, createdDate=datetime.datetime(2022, 4, 2, 21, 37, 1, 727907), updatedDate=datetime.datetime(2022, 4, 2, 21, 37, 1, 727907)
    )
    
    result = await tokenMetadataProcessor.retrieve_token_metadata(
        registryAddress='0x93317e87a3a47821803caadc54ae418af80603da', tokenId='2', collection=collection
    )
    expected = RetrievedTokenMetadata(
        registryAddress='0x93317e87a3a47821803caadc54ae418af80603da', tokenId='2', metadataUrl='ipfs://Qmbitpu7WNj76fhArU2yU2wqQbTnW7ASNJcm8Kf4F4GzL1/0000000000000000000000000000000000000000000000000000000000000002.json', name='gn', description='gn. Art by Vinnie Hager.', imageUrl='ipfs://QmQuqAAahKUw6BHXbEYAvz9N8UTaHPH5X1iK18LaLdUSqo/2.gif', animationUrl=None, youtubeUrl=None, backgroundColor=None, frameImageUrl=None, attributes=[])
    assert (result == expected)

    collection = Collection(
        address='0x97fB6806AcbA833c5Ca80135D7d75BF3794b9df7', name='Lifetime Pass', symbol='LP', description="The Lifetime Pass gives users lifetime access to Astroworld's Virtual Theme Park....", imageUrl='https://gateway.pinata.cloud/ipfs/QmewxBAuXkvkV2YcskXK7GBcspX7MuMvNdMjbiRBNbekdf/', twitterUsername=None, instagramUsername=None, wikiUrl=None, openseaSlug='astroworld-lifetime-pass-v2', url=None, discordUrl=None, bannerImageUrl=None, doesSupportErc721=True, doesSupportErc1155=False, collectionId=65389, createdDate=datetime.datetime(2022, 4, 7, 9, 24, 30, 369275), updatedDate=datetime.datetime(2022, 4, 7, 9, 24, 30, 369275)
    )
    result = await tokenMetadataProcessor.retrieve_token_metadata(
        registryAddress='0x97fB6806AcbA833c5Ca80135D7d75BF3794b9df7', tokenId='2', collection=collection
    )
    expected = RetrievedTokenMetadata(
        registryAddress='0x97fB6806AcbA833c5Ca80135D7d75BF3794b9df7', tokenId='2', metadataUrl='ipfs://QmQNWCbw2SDPt21qs4gENSAhbxMYDrmf8ur6pxKz8Ra1MZ', name='Astroworld Lifetime Pass', description="The Lifetime Pass gives users lifetime access to Astroworld's Virtual Theme Park. This NFT must be in your wallet at the time of each entry. Additionally, Astroworld LP holders will have exclusive access to Astroworld BETA and Astroworld related events that take place in Astroworld or IRL.", imageUrl='https://gateway.pinata.cloud/ipfs/QmewxBAuXkvkV2YcskXK7GBcspX7MuMvNdMjbiRBNbekdf/', animationUrl=None, youtubeUrl=None, backgroundColor=None, frameImageUrl=None, attributes=[]
    )
    assert (result == expected)

    collection = Collection(
        address='0x4581649aF66BCCAeE81eebaE3DDc0511FE4C5312', name='TheAlienBoy', symbol='TABOY', description='Each Alien Boy is unique and algorithmically generated by combining 182 properties ...', imageUrl='https://lh3.googleusercontent.com/mnNWlPXlDTp8N1JP2kiCrTy-w0lGU0S1AX5sMm0ZhWjSTpIh4RTwXERNjz83aKI1uKjyqf8yZJlsId6TeUgvJRhwaWScJPdWZSlISJc=s120', twitterUsername='TheAlienBoyNFT', instagramUsername=None, wikiUrl=None, openseaSlug='thealienboy', url='https://www.thealienboy.com/', discordUrl='https://discord.gg/thealienboy', bannerImageUrl='https://lh3.googleusercontent.com/bWgbzHdOrgOtpDUm0LTIo4eH4JjzeDUsTce4qA3mrBkGw-wXYnWDQVxaKXBG28Y2kQ634cAFBYEfsBMpqggMirS9Vu6GKxAOeKnqJ00=s2500', doesSupportErc721=True, doesSupportErc1155=False, collectionId=40, createdDate=datetime.datetime(2022, 1, 31, 12, 23, 58, 978642), updatedDate=datetime.datetime(2022, 1, 31, 12, 23, 58, 978642)
    )
    result = await tokenMetadataProcessor.retrieve_token_metadata(
        registryAddress='0x4581649aF66BCCAeE81eebaE3DDc0511FE4C5312', tokenId='6574', collection=collection
    )
    expected = RetrievedTokenMetadata(
        registryAddress='0x4581649aF66BCCAeE81eebaE3DDc0511FE4C5312', tokenId='6574', metadataUrl='https://api.thealienboy.com/metadata/6574', imageUrl='https://gateway.pinata.cloud/ipfs/Qmburch4fp76L6oTfDjZF4Ybk3SzpFbbU52xjN8x42rVTS', animationUrl=None, youtubeUrl=None, backgroundColor=None, name='Alien Boy 6574', description='your Alien Boy has a unique DNA. yours is #0804080734090200350000  \nkeep it safe boy, you may need it someday.', frameImageUrl=None, attributes=[{'trait_type': 'background', 'value': 'Tiger Orange'}, {'trait_type': 'skin', 'value': 'Red'}, {'trait_type': 'face', 'value': 'Scratch'}, {'trait_type': 'eyes', 'value': 'Bloodshot'}, {'trait_type': 'body', 'value': 'Miami Suit'}, {'trait_type': 'mouth', 'value': 'Slime'}, {'trait_type': 'accessory', 'value': 'Neon Sunglasses'}, {'trait_type': 'head', 'value': 'Stickers'}, {'trait_type': 'first_encounter', 'value': '1623776953', 'display_type': 'date'}]
    )
    assert (result == expected)

    collection = Collection(
        address='0xC36442b4a4522E871399CD717aBDD847Ab11FE88', name='Uniswap V3 Positions NFT-V1', symbol='UNI-V3-POS', description='', imageUrl='https://lh3.googleusercontent.com/8My7rmWHJCAi35QSp2IMf50NRNIRJelpEdassqIxiL6Q_m2SE2qG7QKIT_1wfXH2afDcACiWVGrt2jkfHqHKlElttUTdL6dmC9G0Mpk=s120', twitterUsername='@Uniswap', instagramUsername=None, wikiUrl=None, openseaSlug='uniswap-v3-positions', url='https://uniswap.org/', discordUrl='https://discord.gg/FCfyBSbCU5', bannerImageUrl='https://lh3.googleusercontent.com/Xq98abLTjlFfzdIxsXNL0sVE2W-3FGcJ2TFUkphz9dh9wEH4rcUesMhE7RzEh_ivPCdL5KxkNVfyE5gb870OgqOLQnBP6sIL54-G0A=s2500', doesSupportErc721=True, doesSupportErc1155=False, collectionId=26, createdDate=datetime.datetime(2022, 1, 31, 0, 24, 59, 737286), updatedDate=datetime.datetime(2022, 1, 31, 0, 24, 59, 737286)
    )
    result = await tokenMetadataProcessor.retrieve_token_metadata(
        registryAddress='0xC36442b4a4522E871399CD717aBDD847Ab11FE88', tokenId='48820', collection=collection
    )
    expected =RetrievedTokenMetadata(
        registryAddress='0xC36442b4a4522E871399CD717aBDD847Ab11FE88', tokenId='48820', metadataUrl='data:application/json;base64,eyJuYW1lIjoiVW5pc3dhcCAtIDAuMyUgLSBVTkkvV0VUSCAtIDc2Ljk5ODw+MTE4LjYwIiwgImRlc2NyaXB0aW9uIjoiVGhpcyBORlQgcmVwcmVzZW50cyBhIGxpcXVpZGl0eSBwb3NpdGlvbiBpbiBhIFVuaXN3YXAgVjMgVU5JLVdFVEggcG9vbC4gVGhlIG93bmVyIG9mIHRoaXMgTkZUIGNhbiBtb2RpZnkgb3IgcmVkZWVtIHRoZSBwb3NpdGlvbi5cblxuUG9vbCBBZGRyZXNzOiAweDFkNDIwNjRmYzRiZWI1ZjhhYWY4NWY0NjE3YWU4YjNiNWI4YmQ4MDFcblVOSSBBZGRyZXNzOiAweDFmOTg0MGE4NWQ1YWY1YmYxZDE3NjJmOTI1YmRhZGRjNDIwMWY5ODRcbldFVEggQWRkcmVzczogMHhjMDJhYWEzOWIyMjNmZThkMGEwZTVjNGYyN2VhZDkwODNjNzU2Y2MyXG5GZWUgVGllcjogMC4zJVxuVG9rZW4gSUQ6IDQ4ODIwXG5cbuKaoO+4jyBESVNDTEFJTUVSOiBEdWUgZGlsaWdlbmNlIGlzIGltcGVyYXRpdmUgd2hlbiBhc3Nlc3NpbmcgdGhpcyBORlQuIE1ha2Ugc3VyZSB0b2tlbiBhZGRyZXNzZXMgbWF0Y2ggdGhlIGV4cGVjdGVkIHRva2VucywgYXMgdG9rZW4gc3ltYm9scyBtYXkgYmUgaW1pdGF0ZWQuIiwgImltYWdlIjogImRhdGE6aW1hZ2Uvc3ZnK3htbDtiYXNlNjQsUEhOMlp5QjNhV1IwYUQwaU1qa3dJaUJvWldsbmFIUTlJalV3TUNJZ2RtbGxkMEp2ZUQwaU1DQXdJREk1TUNBMU1EQWlJSGh0Ykc1elBTSm9kSFJ3T2k4dmQzZDNMbmN6TG05eVp5OHlNREF3TDNOMlp5SWdlRzFzYm5NNmVHeHBibXM5SjJoMGRIQTZMeTkzZDNjdWR6TXViM0puTHpFNU9Ua3ZlR3hwYm1zblBqeGtaV1p6UGp4bWFXeDBaWElnYVdROUltWXhJajQ4Wm1WSmJXRm5aU0J5WlhOMWJIUTlJbkF3SWlCNGJHbHVhenBvY21WbVBTSmtZWFJoT21sdFlXZGxMM04yWnl0NGJXdzdZbUZ6WlRZMExGQklUakphZVVJellWZFNNR0ZFTUc1TmFtdDNTbmxDYjFwWGJHNWhTRkU1U25wVmQwMURZMmRrYld4c1pEQktkbVZFTUc1TlEwRjNTVVJKTlUxRFFURk5SRUZ1U1Vob2RHSkhOWHBRVTJSdlpFaFNkMDlwT0haa00yUXpURzVqZWt4dE9YbGFlVGg1VFVSQmQwd3pUakphZVdNclVFaEtiRmt6VVdka01teHJaRWRuT1VwNlNUVk5TRUkwU25sQ2IxcFhiRzVoU0ZFNVNucFZkMDFJUWpSS2VVSnRZVmQ0YzFCVFkycE5WMWsxVDBSUmQwcDVPQ3RRUXpsNlpHMWpLeUl2UGp4bVpVbHRZV2RsSUhKbGMzVnNkRDBpY0RFaUlIaHNhVzVyT21oeVpXWTlJbVJoZEdFNmFXMWhaMlV2YzNabkszaHRiRHRpWVhObE5qUXNVRWhPTWxwNVFqTmhWMUl3WVVRd2JrMXFhM2RLZVVKdldsZHNibUZJVVRsS2VsVjNUVU5qWjJSdGJHeGtNRXAyWlVRd2JrMURRWGRKUkVrMVRVTkJNVTFFUVc1SlNHaDBZa2MxZWxCVFpHOWtTRkozVDJrNGRtUXpaRE5NYm1ONlRHMDVlVnA1T0hsTlJFRjNURE5PTWxwNVl5dFFSMDV3WTIxT2MxcFRRbXBsUkRCdVRWUk5lVXA1UW1wbFZEQnVUWHByZWtwNVFubFFVMk40VFdwQ2QyVkRZMmRhYld4ellrUXdia2t5VFhkTmJVWm9XVk5qZGxCcWQzWmpNMXB1VUdjOVBTSXZQanhtWlVsdFlXZGxJSEpsYzNWc2REMGljRElpSUhoc2FXNXJPbWh5WldZOUltUmhkR0U2YVcxaFoyVXZjM1puSzNodGJEdGlZWE5sTmpRc1VFaE9NbHA1UWpOaFYxSXdZVVF3YmsxcWEzZEtlVUp2V2xkc2JtRklVVGxLZWxWM1RVTmpaMlJ0Ykd4a01FcDJaVVF3YmsxRFFYZEpSRWsxVFVOQk1VMUVRVzVKU0doMFlrYzFlbEJUWkc5a1NGSjNUMms0ZG1RelpETk1ibU42VEcwNWVWcDVPSGxOUkVGM1RETk9NbHA1WXl0UVIwNXdZMjFPYzFwVFFtcGxSREJ1VG5wRmJrbEhUalZRVTJONlRYcE5ia2xJU1RsS2VrVjVUVWhDTkVwNVFtMWhWM2h6VUZOamFrMUVSbTFQVkdjd1NuazRLMUJET1hwa2JXTXJJaUF2UGp4bVpVbHRZV2RsSUhKbGMzVnNkRDBpY0RNaUlIaHNhVzVyT21oeVpXWTlJbVJoZEdFNmFXMWhaMlV2YzNabkszaHRiRHRpWVhObE5qUXNVRWhPTWxwNVFqTmhWMUl3WVVRd2JrMXFhM2RLZVVKdldsZHNibUZJVVRsS2VsVjNUVU5qWjJSdGJHeGtNRXAyWlVRd2JrMURRWGRKUkVrMVRVTkJNVTFFUVc1SlNHaDBZa2MxZWxCVFpHOWtTRkozVDJrNGRtUXpaRE5NYm1ONlRHMDVlVnA1T0hsTlJFRjNURE5PTWxwNVl5dFFSMDV3WTIxT2MxcFRRbXBsUkRCdVRucFpia2xIVGpWUVUyTjZUVVJOYmtsSVNUbEtla1YzVFVoQ05FcDVRbTFoVjNoelVGTmphazU2VlRKWk1rMTVTbms0SzFCRE9YcGtiV01ySWlBdlBqeG1aVUpzWlc1a0lHMXZaR1U5SW05MlpYSnNZWGtpSUdsdVBTSndNQ0lnYVc0eVBTSndNU0lnTHo0OFptVkNiR1Z1WkNCdGIyUmxQU0psZUdOc2RYTnBiMjRpSUdsdU1qMGljRElpSUM4K1BHWmxRbXhsYm1RZ2JXOWtaVDBpYjNabGNteGhlU0lnYVc0eVBTSndNeUlnY21WemRXeDBQU0ppYkdWdVpFOTFkQ0lnTHo0OFptVkhZWFZ6YzJsaGJrSnNkWElnYVc0OUltSnNaVzVrVDNWMElpQnpkR1JFWlhacFlYUnBiMjQ5SWpReUlpQXZQand2Wm1sc2RHVnlQaUE4WTJ4cGNGQmhkR2dnYVdROUltTnZjbTVsY25NaVBqeHlaV04wSUhkcFpIUm9QU0l5T1RBaUlHaGxhV2RvZEQwaU5UQXdJaUJ5ZUQwaU5ESWlJSEo1UFNJME1pSWdMejQ4TDJOc2FYQlFZWFJvUGp4d1lYUm9JR2xrUFNKMFpYaDBMWEJoZEdndFlTSWdaRDBpVFRRd0lERXlJRWd5TlRBZ1FUSTRJREk0SURBZ01DQXhJREkzT0NBME1DQldORFl3SUVFeU9DQXlPQ0F3SURBZ01TQXlOVEFnTkRnNElFZzBNQ0JCTWpnZ01qZ2dNQ0F3SURFZ01USWdORFl3SUZZME1DQkJNamdnTWpnZ01DQXdJREVnTkRBZ01USWdlaUlnTHo0OGNHRjBhQ0JwWkQwaWJXbHVhVzFoY0NJZ1pEMGlUVEl6TkNBME5EUkRNak0wSURRMU55NDVORGtnTWpReUxqSXhJRFEyTXlBeU5UTWdORFl6SWlBdlBqeG1hV3gwWlhJZ2FXUTlJblJ2Y0MxeVpXZHBiMjR0WW14MWNpSStQR1psUjJGMWMzTnBZVzVDYkhWeUlHbHVQU0pUYjNWeVkyVkhjbUZ3YUdsaklpQnpkR1JFWlhacFlYUnBiMjQ5SWpJMElpQXZQand2Wm1sc2RHVnlQanhzYVc1bFlYSkhjbUZrYVdWdWRDQnBaRDBpWjNKaFpDMTFjQ0lnZURFOUlqRWlJSGd5UFNJd0lpQjVNVDBpTVNJZ2VUSTlJakFpUGp4emRHOXdJRzltWm5ObGREMGlNQzR3SWlCemRHOXdMV052Ykc5eVBTSjNhR2wwWlNJZ2MzUnZjQzF2Y0dGamFYUjVQU0l4SWlBdlBqeHpkRzl3SUc5bVpuTmxkRDBpTGpraUlITjBiM0F0WTI5c2IzSTlJbmRvYVhSbElpQnpkRzl3TFc5d1lXTnBkSGs5SWpBaUlDOCtQQzlzYVc1bFlYSkhjbUZrYVdWdWRENDhiR2x1WldGeVIzSmhaR2xsYm5RZ2FXUTlJbWR5WVdRdFpHOTNiaUlnZURFOUlqQWlJSGd5UFNJeElpQjVNVDBpTUNJZ2VUSTlJakVpUGp4emRHOXdJRzltWm5ObGREMGlNQzR3SWlCemRHOXdMV052Ykc5eVBTSjNhR2wwWlNJZ2MzUnZjQzF2Y0dGamFYUjVQU0l4SWlBdlBqeHpkRzl3SUc5bVpuTmxkRDBpTUM0NUlpQnpkRzl3TFdOdmJHOXlQU0ozYUdsMFpTSWdjM1J2Y0MxdmNHRmphWFI1UFNJd0lpQXZQand2YkdsdVpXRnlSM0poWkdsbGJuUStQRzFoYzJzZ2FXUTlJbVpoWkdVdGRYQWlJRzFoYzJ0RGIyNTBaVzUwVlc1cGRITTlJbTlpYW1WamRFSnZkVzVrYVc1blFtOTRJajQ4Y21WamRDQjNhV1IwYUQwaU1TSWdhR1ZwWjJoMFBTSXhJaUJtYVd4c1BTSjFjbXdvSTJkeVlXUXRkWEFwSWlBdlBqd3ZiV0Z6YXo0OGJXRnpheUJwWkQwaVptRmtaUzFrYjNkdUlpQnRZWE5yUTI5dWRHVnVkRlZ1YVhSelBTSnZZbXBsWTNSQ2IzVnVaR2x1WjBKdmVDSStQSEpsWTNRZ2QybGtkR2c5SWpFaUlHaGxhV2RvZEQwaU1TSWdabWxzYkQwaWRYSnNLQ05uY21Ga0xXUnZkMjRwSWlBdlBqd3ZiV0Z6YXo0OGJXRnpheUJwWkQwaWJtOXVaU0lnYldGemEwTnZiblJsYm5SVmJtbDBjejBpYjJKcVpXTjBRbTkxYm1ScGJtZENiM2dpUGp4eVpXTjBJSGRwWkhSb1BTSXhJaUJvWldsbmFIUTlJakVpSUdacGJHdzlJbmRvYVhSbElpQXZQand2YldGemF6NDhiR2x1WldGeVIzSmhaR2xsYm5RZ2FXUTlJbWR5WVdRdGMzbHRZbTlzSWo0OGMzUnZjQ0J2Wm1aelpYUTlJakF1TnlJZ2MzUnZjQzFqYjJ4dmNqMGlkMmhwZEdVaUlITjBiM0F0YjNCaFkybDBlVDBpTVNJZ0x6NDhjM1J2Y0NCdlptWnpaWFE5SWk0NU5TSWdjM1J2Y0MxamIyeHZjajBpZDJocGRHVWlJSE4wYjNBdGIzQmhZMmwwZVQwaU1DSWdMejQ4TDJ4cGJtVmhja2R5WVdScFpXNTBQanh0WVhOcklHbGtQU0ptWVdSbExYTjViV0p2YkNJZ2JXRnphME52Ym5SbGJuUlZibWwwY3owaWRYTmxjbE53WVdObFQyNVZjMlVpUGp4eVpXTjBJSGRwWkhSb1BTSXlPVEJ3ZUNJZ2FHVnBaMmgwUFNJeU1EQndlQ0lnWm1sc2JEMGlkWEpzS0NObmNtRmtMWE41YldKdmJDa2lJQzgrUEM5dFlYTnJQand2WkdWbWN6NDhaeUJqYkdsd0xYQmhkR2c5SW5WeWJDZ2pZMjl5Ym1WeWN5a2lQanh5WldOMElHWnBiR3c5SWpGbU9UZzBNQ0lnZUQwaU1IQjRJaUI1UFNJd2NIZ2lJSGRwWkhSb1BTSXlPVEJ3ZUNJZ2FHVnBaMmgwUFNJMU1EQndlQ0lnTHo0OGNtVmpkQ0J6ZEhsc1pUMGlabWxzZEdWeU9pQjFjbXdvSTJZeEtTSWdlRDBpTUhCNElpQjVQU0l3Y0hnaUlIZHBaSFJvUFNJeU9UQndlQ0lnYUdWcFoyaDBQU0kxTURCd2VDSWdMejRnUEdjZ2MzUjViR1U5SW1acGJIUmxjanAxY213b0kzUnZjQzF5WldkcGIyNHRZbXgxY2lrN0lIUnlZVzV6Wm05eWJUcHpZMkZzWlNneExqVXBPeUIwY21GdWMyWnZjbTB0YjNKcFoybHVPbU5sYm5SbGNpQjBiM0E3SWo0OGNtVmpkQ0JtYVd4c1BTSnViMjVsSWlCNFBTSXdjSGdpSUhrOUlqQndlQ0lnZDJsa2RHZzlJakk1TUhCNElpQm9aV2xuYUhROUlqVXdNSEI0SWlBdlBqeGxiR3hwY0hObElHTjRQU0kxTUNVaUlHTjVQU0l3Y0hnaUlISjRQU0l4T0RCd2VDSWdjbms5SWpFeU1IQjRJaUJtYVd4c1BTSWpNREF3SWlCdmNHRmphWFI1UFNJd0xqZzFJaUF2UGp3dlp6NDhjbVZqZENCNFBTSXdJaUI1UFNJd0lpQjNhV1IwYUQwaU1qa3dJaUJvWldsbmFIUTlJalV3TUNJZ2NuZzlJalF5SWlCeWVUMGlORElpSUdacGJHdzlJbkpuWW1Fb01Dd3dMREFzTUNraUlITjBjbTlyWlQwaWNtZGlZU2d5TlRVc01qVTFMREkxTlN3d0xqSXBJaUF2UGp3dlp6NDhkR1Y0ZENCMFpYaDBMWEpsYm1SbGNtbHVaejBpYjNCMGFXMXBlbVZUY0dWbFpDSStQSFJsZUhSUVlYUm9JSE4wWVhKMFQyWm1jMlYwUFNJdE1UQXdKU0lnWm1sc2JEMGlkMmhwZEdVaUlHWnZiblF0Wm1GdGFXeDVQU0luUTI5MWNtbGxjaUJPWlhjbkxDQnRiMjV2YzNCaFkyVWlJR1p2Ym5RdGMybDZaVDBpTVRCd2VDSWdlR3hwYm1zNmFISmxaajBpSTNSbGVIUXRjR0YwYUMxaElqNHdlR013TW1GaFlUTTVZakl5TTJabE9HUXdZVEJsTldNMFpqSTNaV0ZrT1RBNE0yTTNOVFpqWXpJZzRvQ2lJRmRGVkVnZ1BHRnVhVzFoZEdVZ1lXUmthWFJwZG1VOUluTjFiU0lnWVhSMGNtbGlkWFJsVG1GdFpUMGljM1JoY25SUFptWnpaWFFpSUdaeWIyMDlJakFsSWlCMGJ6MGlNVEF3SlNJZ1ltVm5hVzQ5SWpCeklpQmtkWEk5SWpNd2N5SWdjbVZ3WldGMFEyOTFiblE5SW1sdVpHVm1hVzVwZEdVaUlDOCtQQzkwWlhoMFVHRjBhRDRnUEhSbGVIUlFZWFJvSUhOMFlYSjBUMlptYzJWMFBTSXdKU0lnWm1sc2JEMGlkMmhwZEdVaUlHWnZiblF0Wm1GdGFXeDVQU0luUTI5MWNtbGxjaUJPWlhjbkxDQnRiMjV2YzNCaFkyVWlJR1p2Ym5RdGMybDZaVDBpTVRCd2VDSWdlR3hwYm1zNmFISmxaajBpSTNSbGVIUXRjR0YwYUMxaElqNHdlR013TW1GaFlUTTVZakl5TTJabE9HUXdZVEJsTldNMFpqSTNaV0ZrT1RBNE0yTTNOVFpqWXpJZzRvQ2lJRmRGVkVnZ1BHRnVhVzFoZEdVZ1lXUmthWFJwZG1VOUluTjFiU0lnWVhSMGNtbGlkWFJsVG1GdFpUMGljM1JoY25SUFptWnpaWFFpSUdaeWIyMDlJakFsSWlCMGJ6MGlNVEF3SlNJZ1ltVm5hVzQ5SWpCeklpQmtkWEk5SWpNd2N5SWdjbVZ3WldGMFEyOTFiblE5SW1sdVpHVm1hVzVwZEdVaUlDOCtJRHd2ZEdWNGRGQmhkR2crUEhSbGVIUlFZWFJvSUhOMFlYSjBUMlptYzJWMFBTSTFNQ1VpSUdacGJHdzlJbmRvYVhSbElpQm1iMjUwTFdaaGJXbHNlVDBpSjBOdmRYSnBaWElnVG1WM0p5d2diVzl1YjNOd1lXTmxJaUJtYjI1MExYTnBlbVU5SWpFd2NIZ2lJSGhzYVc1ck9taHlaV1k5SWlOMFpYaDBMWEJoZEdndFlTSStNSGd4WmprNE5EQmhPRFZrTldGbU5XSm1NV1F4TnpZeVpqa3lOV0prWVdSa1l6UXlNREZtT1RnMElPS0FvaUJWVGtrZ1BHRnVhVzFoZEdVZ1lXUmthWFJwZG1VOUluTjFiU0lnWVhSMGNtbGlkWFJsVG1GdFpUMGljM1JoY25SUFptWnpaWFFpSUdaeWIyMDlJakFsSWlCMGJ6MGlNVEF3SlNJZ1ltVm5hVzQ5SWpCeklpQmtkWEk5SWpNd2N5SWdjbVZ3WldGMFEyOTFiblE5SW1sdVpHVm1hVzVwZEdVaUlDOCtQQzkwWlhoMFVHRjBhRDQ4ZEdWNGRGQmhkR2dnYzNSaGNuUlBabVp6WlhROUlpMDFNQ1VpSUdacGJHdzlJbmRvYVhSbElpQm1iMjUwTFdaaGJXbHNlVDBpSjBOdmRYSnBaWElnVG1WM0p5d2diVzl1YjNOd1lXTmxJaUJtYjI1MExYTnBlbVU5SWpFd2NIZ2lJSGhzYVc1ck9taHlaV1k5SWlOMFpYaDBMWEJoZEdndFlTSStNSGd4WmprNE5EQmhPRFZrTldGbU5XSm1NV1F4TnpZeVpqa3lOV0prWVdSa1l6UXlNREZtT1RnMElPS0FvaUJWVGtrZ1BHRnVhVzFoZEdVZ1lXUmthWFJwZG1VOUluTjFiU0lnWVhSMGNtbGlkWFJsVG1GdFpUMGljM1JoY25SUFptWnpaWFFpSUdaeWIyMDlJakFsSWlCMGJ6MGlNVEF3SlNJZ1ltVm5hVzQ5SWpCeklpQmtkWEk5SWpNd2N5SWdjbVZ3WldGMFEyOTFiblE5SW1sdVpHVm1hVzVwZEdVaUlDOCtQQzkwWlhoMFVHRjBhRDQ4TDNSbGVIUStQR2NnYldGemF6MGlkWEpzS0NObVlXUmxMWE41YldKdmJDa2lQanh5WldOMElHWnBiR3c5SW01dmJtVWlJSGc5SWpCd2VDSWdlVDBpTUhCNElpQjNhV1IwYUQwaU1qa3djSGdpSUdobGFXZG9kRDBpTWpBd2NIZ2lJQzgrSUR4MFpYaDBJSGs5SWpjd2NIZ2lJSGc5SWpNeWNIZ2lJR1pwYkd3OUluZG9hWFJsSWlCbWIyNTBMV1poYldsc2VUMGlKME52ZFhKcFpYSWdUbVYzSnl3Z2JXOXViM053WVdObElpQm1iMjUwTFhkbGFXZG9kRDBpTWpBd0lpQm1iMjUwTFhOcGVtVTlJak0yY0hnaVBsVk9TUzlYUlZSSVBDOTBaWGgwUGp4MFpYaDBJSGs5SWpFeE5YQjRJaUI0UFNJek1uQjRJaUJtYVd4c1BTSjNhR2wwWlNJZ1ptOXVkQzFtWVcxcGJIazlJaWREYjNWeWFXVnlJRTVsZHljc0lHMXZibTl6Y0dGalpTSWdabTl1ZEMxM1pXbG5hSFE5SWpJd01DSWdabTl1ZEMxemFYcGxQU0l6Tm5CNElqNHdMak1sUEM5MFpYaDBQand2Wno0OGNtVmpkQ0I0UFNJeE5pSWdlVDBpTVRZaUlIZHBaSFJvUFNJeU5UZ2lJR2hsYVdkb2REMGlORFk0SWlCeWVEMGlNallpSUhKNVBTSXlOaUlnWm1sc2JEMGljbWRpWVNnd0xEQXNNQ3d3S1NJZ2MzUnliMnRsUFNKeVoySmhLREkxTlN3eU5UVXNNalUxTERBdU1pa2lJQzgrUEdjZ2JXRnphejBpZFhKc0tDTm1ZV1JsTFdSdmQyNHBJaUJ6ZEhsc1pUMGlkSEpoYm5ObWIzSnRPblJ5WVc1emJHRjBaU2czTW5CNExERTRPWEI0S1NJK1BISmxZM1FnZUQwaUxURTJjSGdpSUhrOUlpMHhObkI0SWlCM2FXUjBhRDBpTVRnd2NIZ2lJR2hsYVdkb2REMGlNVGd3Y0hnaUlHWnBiR3c5SW01dmJtVWlJQzgrUEhCaGRHZ2daRDBpVFRFZ01VTTVJRGd4SURZMUlERXpOeUF4TkRVZ01UUTFJaUJ6ZEhKdmEyVTlJbkpuWW1Fb01Dd3dMREFzTUM0ektTSWdjM1J5YjJ0bExYZHBaSFJvUFNJek1uQjRJaUJtYVd4c1BTSnViMjVsSWlCemRISnZhMlV0YkdsdVpXTmhjRDBpY205MWJtUWlJQzgrUEM5blBqeG5JRzFoYzJzOUluVnliQ2dqWm1Ga1pTMWtiM2R1S1NJZ2MzUjViR1U5SW5SeVlXNXpabTl5YlRwMGNtRnVjMnhoZEdVb056SndlQ3d4T0Rsd2VDa2lQanh5WldOMElIZzlJaTB4Tm5CNElpQjVQU0l0TVRad2VDSWdkMmxrZEdnOUlqRTRNSEI0SWlCb1pXbG5hSFE5SWpFNE1IQjRJaUJtYVd4c1BTSnViMjVsSWlBdlBqeHdZWFJvSUdROUlrMHhJREZET1NBNE1TQTJOU0F4TXpjZ01UUTFJREUwTlNJZ2MzUnliMnRsUFNKeVoySmhLREkxTlN3eU5UVXNNalUxTERFcElpQm1hV3hzUFNKdWIyNWxJaUJ6ZEhKdmEyVXRiR2x1WldOaGNEMGljbTkxYm1RaUlDOCtQQzluUGp4amFYSmpiR1VnWTNnOUlqY3pjSGdpSUdONVBTSXhPVEJ3ZUNJZ2NqMGlOSEI0SWlCbWFXeHNQU0ozYUdsMFpTSWdMejQ4WTJseVkyeGxJR040UFNJM00zQjRJaUJqZVQwaU1Ua3djSGdpSUhJOUlqSTBjSGdpSUdacGJHdzlJbTV2Ym1VaUlITjBjbTlyWlQwaWQyaHBkR1VpSUM4K0lEeG5JSE4wZVd4bFBTSjBjbUZ1YzJadmNtMDZkSEpoYm5Oc1lYUmxLREk1Y0hnc0lETTROSEI0S1NJK1BISmxZM1FnZDJsa2RHZzlJamt4Y0hnaUlHaGxhV2RvZEQwaU1qWndlQ0lnY25nOUlqaHdlQ0lnY25rOUlqaHdlQ0lnWm1sc2JEMGljbWRpWVNnd0xEQXNNQ3d3TGpZcElpQXZQangwWlhoMElIZzlJakV5Y0hnaUlIazlJakUzY0hnaUlHWnZiblF0Wm1GdGFXeDVQU0luUTI5MWNtbGxjaUJPWlhjbkxDQnRiMjV2YzNCaFkyVWlJR1p2Ym5RdGMybDZaVDBpTVRKd2VDSWdabWxzYkQwaWQyaHBkR1VpUGp4MGMzQmhiaUJtYVd4c1BTSnlaMkpoS0RJMU5Td3lOVFVzTWpVMUxEQXVOaWtpUGtsRU9pQThMM1J6Y0dGdVBqUTRPREl3UEM5MFpYaDBQand2Wno0Z1BHY2djM1I1YkdVOUluUnlZVzV6Wm05eWJUcDBjbUZ1YzJ4aGRHVW9Namx3ZUN3Z05ERTBjSGdwSWo0OGNtVmpkQ0IzYVdSMGFEMGlNVFF3Y0hnaUlHaGxhV2RvZEQwaU1qWndlQ0lnY25nOUlqaHdlQ0lnY25rOUlqaHdlQ0lnWm1sc2JEMGljbWRpWVNnd0xEQXNNQ3d3TGpZcElpQXZQangwWlhoMElIZzlJakV5Y0hnaUlIazlJakUzY0hnaUlHWnZiblF0Wm1GdGFXeDVQU0luUTI5MWNtbGxjaUJPWlhjbkxDQnRiMjV2YzNCaFkyVWlJR1p2Ym5RdGMybDZaVDBpTVRKd2VDSWdabWxzYkQwaWQyaHBkR1VpUGp4MGMzQmhiaUJtYVd4c1BTSnlaMkpoS0RJMU5Td3lOVFVzTWpVMUxEQXVOaWtpUGsxcGJpQlVhV05yT2lBOEwzUnpjR0Z1UGkwME56YzJNRHd2ZEdWNGRENDhMMmMrSUR4bklITjBlV3hsUFNKMGNtRnVjMlp2Y20wNmRISmhibk5zWVhSbEtESTVjSGdzSURRME5IQjRLU0krUEhKbFkzUWdkMmxrZEdnOUlqRTBNSEI0SWlCb1pXbG5hSFE5SWpJMmNIZ2lJSEo0UFNJNGNIZ2lJSEo1UFNJNGNIZ2lJR1pwYkd3OUluSm5ZbUVvTUN3d0xEQXNNQzQyS1NJZ0x6NDhkR1Y0ZENCNFBTSXhNbkI0SWlCNVBTSXhOM0I0SWlCbWIyNTBMV1poYldsc2VUMGlKME52ZFhKcFpYSWdUbVYzSnl3Z2JXOXViM053WVdObElpQm1iMjUwTFhOcGVtVTlJakV5Y0hnaUlHWnBiR3c5SW5kb2FYUmxJajQ4ZEhOd1lXNGdabWxzYkQwaWNtZGlZU2d5TlRVc01qVTFMREkxTlN3d0xqWXBJajVOWVhnZ1ZHbGphem9nUEM5MGMzQmhiajR0TkRNME5EQThMM1JsZUhRK1BDOW5QanhuSUhOMGVXeGxQU0owY21GdWMyWnZjbTA2ZEhKaGJuTnNZWFJsS0RJeU5uQjRMQ0EwTXpOd2VDa2lQanh5WldOMElIZHBaSFJvUFNJek5uQjRJaUJvWldsbmFIUTlJak0yY0hnaUlISjRQU0k0Y0hnaUlISjVQU0k0Y0hnaUlHWnBiR3c5SW01dmJtVWlJSE4wY205clpUMGljbWRpWVNneU5UVXNNalUxTERJMU5Td3dMaklwSWlBdlBqeHdZWFJvSUhOMGNtOXJaUzFzYVc1bFkyRndQU0p5YjNWdVpDSWdaRDBpVFRnZ09VTTRMakF3TURBMElESXlMamswT1RRZ01UWXVNakE1T1NBeU9DQXlOeUF5T0NJZ1ptbHNiRDBpYm05dVpTSWdjM1J5YjJ0bFBTSjNhR2wwWlNJZ0x6NDhZMmx5WTJ4bElITjBlV3hsUFNKMGNtRnVjMlp2Y20wNmRISmhibk5zWVhSbE0yUW9PSEI0TENBeE5DNHlOWEI0TENBd2NIZ3BJaUJqZUQwaU1IQjRJaUJqZVQwaU1IQjRJaUJ5UFNJMGNIZ2lJR1pwYkd3OUluZG9hWFJsSWk4K1BDOW5Qand2YzNablBnPT0ifQ==', imageUrl='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjkwIiBoZWlnaHQ9IjUwMCIgdmlld0JveD0iMCAwIDI5MCA1MDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9J2h0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsnPjxkZWZzPjxmaWx0ZXIgaWQ9ImYxIj48ZmVJbWFnZSByZXN1bHQ9InAwIiB4bGluazpocmVmPSJkYXRhOmltYWdlL3N2Zyt4bWw7YmFzZTY0LFBITjJaeUIzYVdSMGFEMG5Namt3SnlCb1pXbG5hSFE5SnpVd01DY2dkbWxsZDBKdmVEMG5NQ0F3SURJNU1DQTFNREFuSUhodGJHNXpQU2RvZEhSd09pOHZkM2QzTG5jekxtOXlaeTh5TURBd0wzTjJaeWMrUEhKbFkzUWdkMmxrZEdnOUp6STVNSEI0SnlCb1pXbG5hSFE5SnpVd01IQjRKeUJtYVd4c1BTY2pNV1k1T0RRd0p5OCtQQzl6ZG1jKyIvPjxmZUltYWdlIHJlc3VsdD0icDEiIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2Uvc3ZnK3htbDtiYXNlNjQsUEhOMlp5QjNhV1IwYUQwbk1qa3dKeUJvWldsbmFIUTlKelV3TUNjZ2RtbGxkMEp2ZUQwbk1DQXdJREk1TUNBMU1EQW5JSGh0Ykc1elBTZG9kSFJ3T2k4dmQzZDNMbmN6TG05eVp5OHlNREF3TDNOMlp5YytQR05wY21Oc1pTQmplRDBuTVRNeUp5QmplVDBuTXprekp5QnlQU2N4TWpCd2VDY2dabWxzYkQwbkkyTXdNbUZoWVNjdlBqd3ZjM1puUGc9PSIvPjxmZUltYWdlIHJlc3VsdD0icDIiIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2Uvc3ZnK3htbDtiYXNlNjQsUEhOMlp5QjNhV1IwYUQwbk1qa3dKeUJvWldsbmFIUTlKelV3TUNjZ2RtbGxkMEp2ZUQwbk1DQXdJREk1TUNBMU1EQW5JSGh0Ykc1elBTZG9kSFJ3T2k4dmQzZDNMbmN6TG05eVp5OHlNREF3TDNOMlp5YytQR05wY21Oc1pTQmplRDBuTnpFbklHTjVQU2N6TXpNbklISTlKekV5TUhCNEp5Qm1hV3hzUFNjak1ERm1PVGcwSnk4K1BDOXpkbWMrIiAvPjxmZUltYWdlIHJlc3VsdD0icDMiIHhsaW5rOmhyZWY9ImRhdGE6aW1hZ2Uvc3ZnK3htbDtiYXNlNjQsUEhOMlp5QjNhV1IwYUQwbk1qa3dKeUJvWldsbmFIUTlKelV3TUNjZ2RtbGxkMEp2ZUQwbk1DQXdJREk1TUNBMU1EQW5JSGh0Ykc1elBTZG9kSFJ3T2k4dmQzZDNMbmN6TG05eVp5OHlNREF3TDNOMlp5YytQR05wY21Oc1pTQmplRDBuTnpZbklHTjVQU2N6TURNbklISTlKekV3TUhCNEp5Qm1hV3hzUFNjak56VTJZMk15Snk4K1BDOXpkbWMrIiAvPjxmZUJsZW5kIG1vZGU9Im92ZXJsYXkiIGluPSJwMCIgaW4yPSJwMSIgLz48ZmVCbGVuZCBtb2RlPSJleGNsdXNpb24iIGluMj0icDIiIC8+PGZlQmxlbmQgbW9kZT0ib3ZlcmxheSIgaW4yPSJwMyIgcmVzdWx0PSJibGVuZE91dCIgLz48ZmVHYXVzc2lhbkJsdXIgaW49ImJsZW5kT3V0IiBzdGREZXZpYXRpb249IjQyIiAvPjwvZmlsdGVyPiA8Y2xpcFBhdGggaWQ9ImNvcm5lcnMiPjxyZWN0IHdpZHRoPSIyOTAiIGhlaWdodD0iNTAwIiByeD0iNDIiIHJ5PSI0MiIgLz48L2NsaXBQYXRoPjxwYXRoIGlkPSJ0ZXh0LXBhdGgtYSIgZD0iTTQwIDEyIEgyNTAgQTI4IDI4IDAgMCAxIDI3OCA0MCBWNDYwIEEyOCAyOCAwIDAgMSAyNTAgNDg4IEg0MCBBMjggMjggMCAwIDEgMTIgNDYwIFY0MCBBMjggMjggMCAwIDEgNDAgMTIgeiIgLz48cGF0aCBpZD0ibWluaW1hcCIgZD0iTTIzNCA0NDRDMjM0IDQ1Ny45NDkgMjQyLjIxIDQ2MyAyNTMgNDYzIiAvPjxmaWx0ZXIgaWQ9InRvcC1yZWdpb24tYmx1ciI+PGZlR2F1c3NpYW5CbHVyIGluPSJTb3VyY2VHcmFwaGljIiBzdGREZXZpYXRpb249IjI0IiAvPjwvZmlsdGVyPjxsaW5lYXJHcmFkaWVudCBpZD0iZ3JhZC11cCIgeDE9IjEiIHgyPSIwIiB5MT0iMSIgeTI9IjAiPjxzdG9wIG9mZnNldD0iMC4wIiBzdG9wLWNvbG9yPSJ3aGl0ZSIgc3RvcC1vcGFjaXR5PSIxIiAvPjxzdG9wIG9mZnNldD0iLjkiIHN0b3AtY29sb3I9IndoaXRlIiBzdG9wLW9wYWNpdHk9IjAiIC8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImdyYWQtZG93biIgeDE9IjAiIHgyPSIxIiB5MT0iMCIgeTI9IjEiPjxzdG9wIG9mZnNldD0iMC4wIiBzdG9wLWNvbG9yPSJ3aGl0ZSIgc3RvcC1vcGFjaXR5PSIxIiAvPjxzdG9wIG9mZnNldD0iMC45IiBzdG9wLWNvbG9yPSJ3aGl0ZSIgc3RvcC1vcGFjaXR5PSIwIiAvPjwvbGluZWFyR3JhZGllbnQ+PG1hc2sgaWQ9ImZhZGUtdXAiIG1hc2tDb250ZW50VW5pdHM9Im9iamVjdEJvdW5kaW5nQm94Ij48cmVjdCB3aWR0aD0iMSIgaGVpZ2h0PSIxIiBmaWxsPSJ1cmwoI2dyYWQtdXApIiAvPjwvbWFzaz48bWFzayBpZD0iZmFkZS1kb3duIiBtYXNrQ29udGVudFVuaXRzPSJvYmplY3RCb3VuZGluZ0JveCI+PHJlY3Qgd2lkdGg9IjEiIGhlaWdodD0iMSIgZmlsbD0idXJsKCNncmFkLWRvd24pIiAvPjwvbWFzaz48bWFzayBpZD0ibm9uZSIgbWFza0NvbnRlbnRVbml0cz0ib2JqZWN0Qm91bmRpbmdCb3giPjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IndoaXRlIiAvPjwvbWFzaz48bGluZWFyR3JhZGllbnQgaWQ9ImdyYWQtc3ltYm9sIj48c3RvcCBvZmZzZXQ9IjAuNyIgc3RvcC1jb2xvcj0id2hpdGUiIHN0b3Atb3BhY2l0eT0iMSIgLz48c3RvcCBvZmZzZXQ9Ii45NSIgc3RvcC1jb2xvcj0id2hpdGUiIHN0b3Atb3BhY2l0eT0iMCIgLz48L2xpbmVhckdyYWRpZW50PjxtYXNrIGlkPSJmYWRlLXN5bWJvbCIgbWFza0NvbnRlbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPjxyZWN0IHdpZHRoPSIyOTBweCIgaGVpZ2h0PSIyMDBweCIgZmlsbD0idXJsKCNncmFkLXN5bWJvbCkiIC8+PC9tYXNrPjwvZGVmcz48ZyBjbGlwLXBhdGg9InVybCgjY29ybmVycykiPjxyZWN0IGZpbGw9IjFmOTg0MCIgeD0iMHB4IiB5PSIwcHgiIHdpZHRoPSIyOTBweCIgaGVpZ2h0PSI1MDBweCIgLz48cmVjdCBzdHlsZT0iZmlsdGVyOiB1cmwoI2YxKSIgeD0iMHB4IiB5PSIwcHgiIHdpZHRoPSIyOTBweCIgaGVpZ2h0PSI1MDBweCIgLz4gPGcgc3R5bGU9ImZpbHRlcjp1cmwoI3RvcC1yZWdpb24tYmx1cik7IHRyYW5zZm9ybTpzY2FsZSgxLjUpOyB0cmFuc2Zvcm0tb3JpZ2luOmNlbnRlciB0b3A7Ij48cmVjdCBmaWxsPSJub25lIiB4PSIwcHgiIHk9IjBweCIgd2lkdGg9IjI5MHB4IiBoZWlnaHQ9IjUwMHB4IiAvPjxlbGxpcHNlIGN4PSI1MCUiIGN5PSIwcHgiIHJ4PSIxODBweCIgcnk9IjEyMHB4IiBmaWxsPSIjMDAwIiBvcGFjaXR5PSIwLjg1IiAvPjwvZz48cmVjdCB4PSIwIiB5PSIwIiB3aWR0aD0iMjkwIiBoZWlnaHQ9IjUwMCIgcng9IjQyIiByeT0iNDIiIGZpbGw9InJnYmEoMCwwLDAsMCkiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjIpIiAvPjwvZz48dGV4dCB0ZXh0LXJlbmRlcmluZz0ib3B0aW1pemVTcGVlZCI+PHRleHRQYXRoIHN0YXJ0T2Zmc2V0PSItMTAwJSIgZmlsbD0id2hpdGUiIGZvbnQtZmFtaWx5PSInQ291cmllciBOZXcnLCBtb25vc3BhY2UiIGZvbnQtc2l6ZT0iMTBweCIgeGxpbms6aHJlZj0iI3RleHQtcGF0aC1hIj4weGMwMmFhYTM5YjIyM2ZlOGQwYTBlNWM0ZjI3ZWFkOTA4M2M3NTZjYzIg4oCiIFdFVEggPGFuaW1hdGUgYWRkaXRpdmU9InN1bSIgYXR0cmlidXRlTmFtZT0ic3RhcnRPZmZzZXQiIGZyb209IjAlIiB0bz0iMTAwJSIgYmVnaW49IjBzIiBkdXI9IjMwcyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiIC8+PC90ZXh0UGF0aD4gPHRleHRQYXRoIHN0YXJ0T2Zmc2V0PSIwJSIgZmlsbD0id2hpdGUiIGZvbnQtZmFtaWx5PSInQ291cmllciBOZXcnLCBtb25vc3BhY2UiIGZvbnQtc2l6ZT0iMTBweCIgeGxpbms6aHJlZj0iI3RleHQtcGF0aC1hIj4weGMwMmFhYTM5YjIyM2ZlOGQwYTBlNWM0ZjI3ZWFkOTA4M2M3NTZjYzIg4oCiIFdFVEggPGFuaW1hdGUgYWRkaXRpdmU9InN1bSIgYXR0cmlidXRlTmFtZT0ic3RhcnRPZmZzZXQiIGZyb209IjAlIiB0bz0iMTAwJSIgYmVnaW49IjBzIiBkdXI9IjMwcyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiIC8+IDwvdGV4dFBhdGg+PHRleHRQYXRoIHN0YXJ0T2Zmc2V0PSI1MCUiIGZpbGw9IndoaXRlIiBmb250LWZhbWlseT0iJ0NvdXJpZXIgTmV3JywgbW9ub3NwYWNlIiBmb250LXNpemU9IjEwcHgiIHhsaW5rOmhyZWY9IiN0ZXh0LXBhdGgtYSI+MHgxZjk4NDBhODVkNWFmNWJmMWQxNzYyZjkyNWJkYWRkYzQyMDFmOTg0IOKAoiBVTkkgPGFuaW1hdGUgYWRkaXRpdmU9InN1bSIgYXR0cmlidXRlTmFtZT0ic3RhcnRPZmZzZXQiIGZyb209IjAlIiB0bz0iMTAwJSIgYmVnaW49IjBzIiBkdXI9IjMwcyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiIC8+PC90ZXh0UGF0aD48dGV4dFBhdGggc3RhcnRPZmZzZXQ9Ii01MCUiIGZpbGw9IndoaXRlIiBmb250LWZhbWlseT0iJ0NvdXJpZXIgTmV3JywgbW9ub3NwYWNlIiBmb250LXNpemU9IjEwcHgiIHhsaW5rOmhyZWY9IiN0ZXh0LXBhdGgtYSI+MHgxZjk4NDBhODVkNWFmNWJmMWQxNzYyZjkyNWJkYWRkYzQyMDFmOTg0IOKAoiBVTkkgPGFuaW1hdGUgYWRkaXRpdmU9InN1bSIgYXR0cmlidXRlTmFtZT0ic3RhcnRPZmZzZXQiIGZyb209IjAlIiB0bz0iMTAwJSIgYmVnaW49IjBzIiBkdXI9IjMwcyIgcmVwZWF0Q291bnQ9ImluZGVmaW5pdGUiIC8+PC90ZXh0UGF0aD48L3RleHQ+PGcgbWFzaz0idXJsKCNmYWRlLXN5bWJvbCkiPjxyZWN0IGZpbGw9Im5vbmUiIHg9IjBweCIgeT0iMHB4IiB3aWR0aD0iMjkwcHgiIGhlaWdodD0iMjAwcHgiIC8+IDx0ZXh0IHk9IjcwcHgiIHg9IjMycHgiIGZpbGw9IndoaXRlIiBmb250LWZhbWlseT0iJ0NvdXJpZXIgTmV3JywgbW9ub3NwYWNlIiBmb250LXdlaWdodD0iMjAwIiBmb250LXNpemU9IjM2cHgiPlVOSS9XRVRIPC90ZXh0Pjx0ZXh0IHk9IjExNXB4IiB4PSIzMnB4IiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IidDb3VyaWVyIE5ldycsIG1vbm9zcGFjZSIgZm9udC13ZWlnaHQ9IjIwMCIgZm9udC1zaXplPSIzNnB4Ij4wLjMlPC90ZXh0PjwvZz48cmVjdCB4PSIxNiIgeT0iMTYiIHdpZHRoPSIyNTgiIGhlaWdodD0iNDY4IiByeD0iMjYiIHJ5PSIyNiIgZmlsbD0icmdiYSgwLDAsMCwwKSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMikiIC8+PGcgbWFzaz0idXJsKCNmYWRlLWRvd24pIiBzdHlsZT0idHJhbnNmb3JtOnRyYW5zbGF0ZSg3MnB4LDE4OXB4KSI+PHJlY3QgeD0iLTE2cHgiIHk9Ii0xNnB4IiB3aWR0aD0iMTgwcHgiIGhlaWdodD0iMTgwcHgiIGZpbGw9Im5vbmUiIC8+PHBhdGggZD0iTTEgMUM5IDgxIDY1IDEzNyAxNDUgMTQ1IiBzdHJva2U9InJnYmEoMCwwLDAsMC4zKSIgc3Ryb2tlLXdpZHRoPSIzMnB4IiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiIC8+PC9nPjxnIG1hc2s9InVybCgjZmFkZS1kb3duKSIgc3R5bGU9InRyYW5zZm9ybTp0cmFuc2xhdGUoNzJweCwxODlweCkiPjxyZWN0IHg9Ii0xNnB4IiB5PSItMTZweCIgd2lkdGg9IjE4MHB4IiBoZWlnaHQ9IjE4MHB4IiBmaWxsPSJub25lIiAvPjxwYXRoIGQ9Ik0xIDFDOSA4MSA2NSAxMzcgMTQ1IDE0NSIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDEpIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiIC8+PC9nPjxjaXJjbGUgY3g9IjczcHgiIGN5PSIxOTBweCIgcj0iNHB4IiBmaWxsPSJ3aGl0ZSIgLz48Y2lyY2xlIGN4PSI3M3B4IiBjeT0iMTkwcHgiIHI9IjI0cHgiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIC8+IDxnIHN0eWxlPSJ0cmFuc2Zvcm06dHJhbnNsYXRlKDI5cHgsIDM4NHB4KSI+PHJlY3Qgd2lkdGg9IjkxcHgiIGhlaWdodD0iMjZweCIgcng9IjhweCIgcnk9IjhweCIgZmlsbD0icmdiYSgwLDAsMCwwLjYpIiAvPjx0ZXh0IHg9IjEycHgiIHk9IjE3cHgiIGZvbnQtZmFtaWx5PSInQ291cmllciBOZXcnLCBtb25vc3BhY2UiIGZvbnQtc2l6ZT0iMTJweCIgZmlsbD0id2hpdGUiPjx0c3BhbiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuNikiPklEOiA8L3RzcGFuPjQ4ODIwPC90ZXh0PjwvZz4gPGcgc3R5bGU9InRyYW5zZm9ybTp0cmFuc2xhdGUoMjlweCwgNDE0cHgpIj48cmVjdCB3aWR0aD0iMTQwcHgiIGhlaWdodD0iMjZweCIgcng9IjhweCIgcnk9IjhweCIgZmlsbD0icmdiYSgwLDAsMCwwLjYpIiAvPjx0ZXh0IHg9IjEycHgiIHk9IjE3cHgiIGZvbnQtZmFtaWx5PSInQ291cmllciBOZXcnLCBtb25vc3BhY2UiIGZvbnQtc2l6ZT0iMTJweCIgZmlsbD0id2hpdGUiPjx0c3BhbiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuNikiPk1pbiBUaWNrOiA8L3RzcGFuPi00Nzc2MDwvdGV4dD48L2c+IDxnIHN0eWxlPSJ0cmFuc2Zvcm06dHJhbnNsYXRlKDI5cHgsIDQ0NHB4KSI+PHJlY3Qgd2lkdGg9IjE0MHB4IiBoZWlnaHQ9IjI2cHgiIHJ4PSI4cHgiIHJ5PSI4cHgiIGZpbGw9InJnYmEoMCwwLDAsMC42KSIgLz48dGV4dCB4PSIxMnB4IiB5PSIxN3B4IiBmb250LWZhbWlseT0iJ0NvdXJpZXIgTmV3JywgbW9ub3NwYWNlIiBmb250LXNpemU9IjEycHgiIGZpbGw9IndoaXRlIj48dHNwYW4gZmlsbD0icmdiYSgyNTUsMjU1LDI1NSwwLjYpIj5NYXggVGljazogPC90c3Bhbj4tNDM0NDA8L3RleHQ+PC9nPjxnIHN0eWxlPSJ0cmFuc2Zvcm06dHJhbnNsYXRlKDIyNnB4LCA0MzNweCkiPjxyZWN0IHdpZHRoPSIzNnB4IiBoZWlnaHQ9IjM2cHgiIHJ4PSI4cHgiIHJ5PSI4cHgiIGZpbGw9Im5vbmUiIHN0cm9rZT0icmdiYSgyNTUsMjU1LDI1NSwwLjIpIiAvPjxwYXRoIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgZD0iTTggOUM4LjAwMDA0IDIyLjk0OTQgMTYuMjA5OSAyOCAyNyAyOCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgLz48Y2lyY2xlIHN0eWxlPSJ0cmFuc2Zvcm06dHJhbnNsYXRlM2QoOHB4LCAxNC4yNXB4LCAwcHgpIiBjeD0iMHB4IiBjeT0iMHB4IiByPSI0cHgiIGZpbGw9IndoaXRlIi8+PC9nPjwvc3ZnPg==', animationUrl=None, youtubeUrl=None, backgroundColor=None, name='Uniswap - 0.3% - UNI/WETH - 76.998<>118.60', description='This NFT represents a liquidity position in a Uniswap V3 UNI-WETH pool. The owner of this NFT can modify or redeem the position.\n\nPool Address: 0x1d42064fc4beb5f8aaf85f4617ae8b3b5b8bd801\nUNI Address: 0x1f9840a85d5af5bf1d1762f925bdaddc4201f984\nWETH Address: 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2\nFee Tier: 0.3%\nToken ID: 48820\n\n⚠️ DISCLAIMER: Due diligence is imperative when assessing this NFT. Make sure token addresses match the expected tokens, as token symbols may be imitated.', frameImageUrl=None, attributes=[]
    )
    assert (result == expected)

    collection = Collection(
        address='0xE3f92992BB4F0f0D173623A52b2922d65172601d', name='Knights of Degen', symbol='KNIGHTS', description='8,888 NFT Degens who love sports, betting, alpha and nfts ⚔️', imageUrl='https://lh3.googleusercontent.com/yxdb_995UrIS6W9YIHMfMCRsdYRqcITlBvO5w7OoUx35rkClUeq9rPCvTMXdtw_zION07O_qRZSuNfZu6R6o8bI_KmbrfThhFtA4SBc=s120', twitterUsername='knightsofdegen', instagramUsername=None, wikiUrl=None, openseaSlug='knights-of-degen-official', url='https://www.knightsofdegen.io/', discordUrl='https://discord.gg/knightsofdegen', bannerImageUrl='https://lh3.googleusercontent.com/328JHSQ2nPpzfTxpZjV5xiiBp6R17GgUdjHJ7BF0mU-SH0Ou1LiiYmcET0WeHt26LD4tVXenIvYZD7VC8jV__bqRCiA_CzmWfwg7=s2500', doesSupportErc721=True, doesSupportErc1155=False, collectionId=41, createdDate=datetime.datetime(2022, 1, 31, 12, 27, 18, 712443), updatedDate=datetime.datetime(2022, 1, 31, 12, 27, 18, 712443)
    )
    result = await tokenMetadataProcessor.retrieve_token_metadata(
        registryAddress='0xE3f92992BB4F0f0D173623A52b2922d65172601d', tokenId='4655', collection=collection
    )
    expected = RetrievedTokenMetadata(
        registryAddress='0xE3f92992BB4F0f0D173623A52b2922d65172601d', tokenId='4655', metadataUrl='ipfs://QmZk6BfbKYswziCEdYaMqh7yQqtcmCnHhoNu3zDGKQjKpJ/4655', imageUrl='ipfs://QmdFkX7SkgL9cDYPwt4CNpsQ5CSz74CF3MwswmGLKEgDMp/4655.png', animationUrl=None, youtubeUrl=None, backgroundColor=None, name='Knights of Degen #4655', description='The Knights of Degen are 8,888 NFT degenerate gamblers that live their truest and darkest lives, free from oppression, and spend their days in the Degen Sports Bars watching and wagering on all sporting events.', frameImageUrl=None,  attributes=[{'trait_type': 'Background', 'value': 'Teal'}, {'trait_type': 'Eyes', 'value': 'Blue'}, {'trait_type': 'Helmet', 'value': 'Valkyrie Helmet - Silver'}, {'trait_type': 'Nose', 'value': 'Normal'}, {'trait_type': 'Armor', 'value': 'Chainmail - Silver'}, {'trait_type': 'Mouth', 'value': 'Tongue Out'}, {'trait_type': 'Character', 'value': 'Human'}, {'trait_type': 'Weapon', 'value': 'None'}]
    )
    assert (result == expected)

    await s3manager.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
