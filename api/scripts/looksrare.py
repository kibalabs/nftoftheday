import asyncio
import logging
import os
import sys


from core.requester import Requester

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.token_listing_processor import TokenListingProcessor


async def test():
    requester = Requester()
    tokenListingProcessor = TokenListingProcessor(requester=requester, openseaRequester=None)
    looksrareListing = await tokenListingProcessor.get_looks_rare_listings_for_collection(registryAddress='0xbce3781ae7ca1a5e050bd9c4c77369867ebc307e')
    print(looksrareListing, len(looksrareListing))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
