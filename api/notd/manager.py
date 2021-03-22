import asyncio
import datetime
import logging
from typing import Sequence

from notd.block_processor import BlockProcessor
from notd.store.saver import Saver
from notd.store.retriever import NotdRetriever
from notd.core.store.retriever import Direction
from notd.core.store.retriever import Order
from notd.core.store.retriever import RandomOrder
from notd.core.store.retriever import DateFieldFilter
from notd.core.store.retriever import StringFieldFilter
from notd.core.requester import Requester
from notd.core.exceptions import NotFoundException
from notd.store.schema import TokenTransfersTable
from notd.model import UiData
from notd.model import Token
from notd.model import RegistryToken
from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.core.exceptions import DuplicateValueException
from notd.core.sqs_message_queue import SqsMessageQueue
from notd.core.util import date_util
from notd.opensea_client import OpenseaClient
from notd.token_client import TokenClient

SPONSORED_TOKENS = [{
    'date': datetime.datetime(2021, 1, 1),
    'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='64159879865138287087882027887075729047962830622590748212892263500451722297345'),
}, {
    'date': datetime.datetime(2021, 3, 17),
    'token': Token(registryAddress='0xeb30e885ad86882e6d7d357977fd6398526b08f6', tokenId='12600020004'),
}, {
    'date': datetime.datetime(2021, 3, 18),
    'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='46336616857044335826783636020397951689168313340333593985461699001474655191041'),
}, {
    'date': datetime.datetime(2021, 3, 19),
    'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='55250154536998404625027252047976608984451896300108729590900307027953738317825'),
}, {
    'date': datetime.datetime(2021, 3, 21),
    'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='25717709526662043702667024073050036494419818265012940397736896226900968472577'),
}, {
    'date': datetime.datetime(2021, 3, 23),
    'token': Token(registryAddres='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='43801378208677021703013652720955131791329532695635720832601938054892750897153'),
}, {
    'date': datetime.datetime(2021, 3, 24),
    'token': Token(registryAddres='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='105603725609947989499044129472074064723412167009068320432332286644752010444801'),
}, {
    'date': datetime.datetime(2021, 3, 25),
    'token': Token(registryAddres='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='29008894289059716691173729123664412627883963428002876020831939699607722786817'),
}, {
    'date': datetime.datetime(2021, 3, 26),
    'token': Token(registryAddres='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='92319092330910075162431766655763082221681235942393137704011888675062376562689'),
}, {
    'date': datetime.datetime(2021, 3, 27),
    'token': Token(registryAddres='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='24343393884017988685652554990480100049636101405691386574948147480323891920897'),
}, {
    'date': datetime.datetime(2021, 3, 28),
    'token': Token(registryAddres='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='27756626610640948989691358307332070697401420694720604130599955962904744820737'),
}, {
    'date': datetime.datetime(2021, 3, 29),
    'token': Token(registryAddres='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='24093022776342378134827809530625168732940087388395506520881445066877419126785'),
}]

class NotdManager:

    def __init__(self, blockProcessor: BlockProcessor, saver: Saver, retriever: NotdRetriever, workQueue: SqsMessageQueue, openseaClient: OpenseaClient, tokenClient: TokenClient, requester: Requester):
        self.blockProcessor = blockProcessor
        self.saver = saver
        self.retriever = retriever
        self.workQueue = workQueue
        self.openseaClient = openseaClient
        self.tokenClient = tokenClient
        self.requester = requester
        self._tokenCache = dict()

    @staticmethod
    def get_sponsored_token() -> Token:
        sponsoredToken = SPONSORED_TOKENS[0]['token']
        currentDate = date_util.datetime_from_now()
        allPastTokens = [sponsorItem['token'] for sponsorItem in SPONSORED_TOKENS if sponsorItem['date'] < currentDate]
        if allPastTokens:
            sponsoredToken = allPastTokens[-1]
        return sponsoredToken

    async def retrieve_ui_data(self, startDate: datetime.datetime, endDate: datetime.datetime) -> UiData:
        highestPricedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)],
            limit=1
        )
        mostTradedToken = await self.retriever.get_most_traded_token(startDate=startDate, endDate=endDate)
        mostTradedTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[
                StringFieldFilter(fieldName=TokenTransfersTable.c.registryAddress.key, eq=mostTradedToken.registryAddress),
                StringFieldFilter(fieldName=TokenTransfersTable.c.tokenId.key, eq=mostTradedToken.tokenId),
            ],
            orders=[Order(fieldName=TokenTransfersTable.c.value.key, direction=Direction.DESCENDING)]
        )
        randomTokenTransfers = await self.retriever.list_token_transfers(
            fieldFilters=[DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate)],
            orders=[RandomOrder()],
            limit=1
        )
        return UiData(
            highestPricedTokenTransfer=highestPricedTokenTransfers[0],
            mostTradedTokenTransfers=mostTradedTokenTransfers,
            randomTokenTransfer=randomTokenTransfers[0],
            sponsoredToken=self.get_sponsored_token(),
        )

    async def receive_new_blocks_deferred(self) -> None:
        await self.workQueue.send_message(message=ReceiveNewBlocksMessageContent().to_message())

    async def receive_new_blocks(self) -> None:
        latestTokenTransfers = await self.retriever.list_token_transfers(orders=[Order(fieldName=TokenTransfersTable.c.blockNumber.key, direction=Direction.DESCENDING)], limit=1)
        latestProcessedBlockNumber = latestTokenTransfers[0].blockNumber
        latestBlockNumber = await self.blockProcessor.get_latest_block_number()
        logging.info(f'Scheduling messages for processing blocks from {latestProcessedBlockNumber} to {latestBlockNumber}')
        batchSize = 25
        for startBlockNumber in reversed(range(latestProcessedBlockNumber, latestBlockNumber + 1, batchSize)):
            endBlockNumber = min(startBlockNumber + batchSize, latestBlockNumber + 1)
            await self.workQueue.send_message(message=ProcessBlockRangeMessageContent(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber).to_message())

    async def process_block_range(self, startBlockNumber: int, endBlockNumber: int) -> None:
        blockNumbers = list(range(startBlockNumber, endBlockNumber))
        await self.process_blocks(blockNumbers=blockNumbers)

    async def process_blocks(self, blockNumbers: Sequence[int]) -> None:
        await asyncio.gather(*[self.process_block(blockNumber=blockNumber) for blockNumber in blockNumbers])

    async def process_block(self, blockNumber: int) -> None:
        retrievedTokenTransfers = await self.blockProcessor.get_transfers_in_block(blockNumber=blockNumber)
        logging.info(f'Found {len(retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        for retrievedTokenTransfer in retrievedTokenTransfers:
            logging.debug(f'Transferred {retrievedTokenTransfer.tokenId} from {retrievedTokenTransfer.fromAddress} to {retrievedTokenTransfer.toAddress}')
            logging.debug(f'Paid {retrievedTokenTransfer.value / 100000000000000000.0}Ξ ({retrievedTokenTransfer.gasUsed * retrievedTokenTransfer.gasPrice / 100000000000000000.0}Ξ) to {retrievedTokenTransfer.registryAddress}')
            logging.debug(f'OpenSea url: https://opensea.io/assets/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
            logging.debug(f'OpenSea api url: https://api.opensea.io/api/v1/asset/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
            try:
                await self.saver.create_token_transfer(transactionHash=retrievedTokenTransfer.transactionHash, registryAddress=retrievedTokenTransfer.registryAddress, fromAddress=retrievedTokenTransfer.fromAddress, toAddress=retrievedTokenTransfer.toAddress, tokenId=retrievedTokenTransfer.tokenId, value=retrievedTokenTransfer.value, gasLimit=retrievedTokenTransfer.gasLimit, gasPrice=retrievedTokenTransfer.gasPrice, gasUsed=retrievedTokenTransfer.gasUsed, blockNumber=retrievedTokenTransfer.blockNumber, blockHash=retrievedTokenTransfer.blockHash, blockDate=retrievedTokenTransfer.blockDate)
            except DuplicateValueException:
                logging.debug(f'Ignoring previously saved transaction')

    async def retreive_registry_token(self, registryAddress: str, tokenId: str) -> RegistryToken:
        cacheKey = f'{registryAddress}:{tokenId}'
        if cacheKey in self._tokenCache:
            return self._tokenCache[cacheKey]
        try:
            registryToken = await self.openseaClient.retreive_registry_token(registryAddress=registryAddress, tokenId=tokenId)
        except NotFoundException:
            registryToken = await self.tokenClient.retreive_registry_token(registryAddress=registryAddress, tokenId=tokenId)
        self._tokenCache[cacheKey] = registryToken
        return registryToken

    async def subscribe_email(self, email: str) -> None:
        await self.requester.post(url='https://api.kiba.dev/v1/newsletter-subscriptions', dataDict={'topic': 'tokenhunt', 'email': email.lower()})
