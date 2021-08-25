import asyncio
import datetime
import logging
from typing import Sequence

from core.exceptions import DuplicateValueException
from core.exceptions import NotFoundException
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.store.retriever import DateFieldFilter
from core.store.retriever import Direction
from core.store.retriever import Order
from core.store.retriever import RandomOrder
from core.store.retriever import StringFieldFilter
from core.util import date_util
from core.util import list_util

from notd.block_processor import BlockProcessor
from notd.messages import ProcessBlockRangeMessageContent
from notd.messages import ReceiveNewBlocksMessageContent
from notd.model import RegistryToken
from notd.model import RetrievedTokenTransfer
from notd.model import Token
from notd.model import UiData
from notd.opensea_client import OpenseaClient
from notd.store.retriever import NotdRetriever
from notd.store.saver import Saver
from notd.store.schema import TokenTransfersTable
from notd.token_client import TokenClient

SPONSORED_TOKENS = [
    {'date': datetime.datetime(2021, 1, 1), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='64159879865138287087882027887075729047962830622590748212892263500451722297345')},
    {'date': datetime.datetime(2021, 3, 17), 'token': Token(registryAddress='0xeb30e885ad86882e6d7d357977fd6398526b08f6', tokenId='12600020004')},
    {'date': datetime.datetime(2021, 3, 18), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='46336616857044335826783636020397951689168313340333593985461699001474655191041')},
    {'date': datetime.datetime(2021, 3, 19), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='55250154536998404625027252047976608984451896300108729590900307027953738317825')},
    {'date': datetime.datetime(2021, 3, 21), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='25717709526662043702667024073050036494419818265012940397736896226900968472577')},
    {'date': datetime.datetime(2021, 3, 23), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='43801378208677021703013652720955131791329532695635720832601938054892750897153')},
    {'date': datetime.datetime(2021, 3, 24), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='105603725609947989499044129472074064723412167009068320432332286644752010444801')},
    {'date': datetime.datetime(2021, 3, 25), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='29008894289059716691173729123664412627883963428002876020831939699607722786817')},
    {'date': datetime.datetime(2021, 3, 26), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='92319092330910075162431766655763082221681235942393137704011888675062376562689')},
    {'date': datetime.datetime(2021, 3, 27), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='24343393884017988685652554990480100049636101405691386574948147480323891920897')},
    {'date': datetime.datetime(2021, 3, 28), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='27756626610640948989691358307332070697401420694720604130599955962904744820737')},
    {'date': datetime.datetime(2021, 3, 29), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='24093022776342378134827809530625168732940087388395506520881445066877419126785')},
    {'date': datetime.datetime(2021, 4, 6), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='76342150682492012527130272222408539120490122112533884247310952850290821300225')},
    {'date': datetime.datetime(2021, 4, 8), 'token': Token(registryAddress='0x60f80121c31a0d46b5279700f9df786054aa5ee5', tokenId='726570')},
    {'date': datetime.datetime(2021, 4, 9), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='8370')},
    {'date': datetime.datetime(2021, 4, 10), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='99676044512270035834243585942457171130947118632456127502028325840120639913985')},
    {'date': datetime.datetime(2021, 4, 11), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='107365703537559603625286105018717806731803205287939746917767951208164328734721')},
    {'date': datetime.datetime(2021, 4, 12), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='84419958519894822484349159784641745807875992324952889767860142621535112265729')},
    {'date': datetime.datetime(2021, 4, 13), 'token': Token(registryAddress='0x3a275655586a049fe860be867d10cdae2ffc0f33', tokenId='404')},
    {'date': datetime.datetime(2021, 4, 29), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='23851')},
    {'date': datetime.datetime(2021, 4, 30), 'token': Token(registryAddress='0xd07dc4262bcdbf85190c01c996b4c06a461d2430', tokenId='519902')},
    {'date': datetime.datetime(2021, 5, 1), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='54288986509980961627044848344103425498948313073962940939987547055279390588929')},
    {'date': datetime.datetime(2021, 5, 2), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='27798')},
    {'date': datetime.datetime(2021, 5, 3), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='102246215621931234854983516961584524249741870832420637379168818446594192965633')},
    {'date': datetime.datetime(2021, 5, 4), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='50351284325109780433681244533011450725220588723395223416911376259895259037697')},
    {'date': datetime.datetime(2021, 7, 8), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='23851')},
    {'date': datetime.datetime(2021, 7, 9), 'token': Token(registryAddress='0x1a92f7381b9f03921564a437210bb9396471050c', tokenId='8608')},
    {'date': datetime.datetime(2021, 7, 10), 'token': Token(registryAddress='0x3b3bc9b1dd9f3c8716fff083947b8769e2ff9781', tokenId='2491')},
    {'date': datetime.datetime(2021, 7, 11), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='66002780748994982626144006163509289231567768778061913896012243296857769377793')},
    {'date': datetime.datetime(2021, 7, 12), 'token': Token(registryAddress='0x3b3bc9b1dd9f3c8716fff083947b8769e2ff9781', tokenId='2491')},
    {'date': datetime.datetime(2021, 7, 27), 'token': Token(registryAddress='0x495f947276749ce646f68ac8c248420045cb7b5e', tokenId='66745729326815246883087876015061527361061274724079872296411828014787160178689')},
    {'date': datetime.datetime(2021, 7, 30), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='88081196100390197613502372721796212703872445580242466524616017838975500681217')},
    {'date': datetime.datetime(2021, 8, 2), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='105396633564879415009426829041684172579609570053458601633165868279695398666241')},
    {'date': datetime.datetime(2021, 8, 5), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='62381')},
    {'date': datetime.datetime(2021, 8, 8), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='61560')},
    {'date': datetime.datetime(2021, 8, 11), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='48009777219687553353266573207856084490164331626444899155064281889677699448833')},
    {'date': datetime.datetime(2021, 8, 14), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='49660350604499248360381827203761942161648024579795517639836571580713003909121')},
    {'date': datetime.datetime(2021, 8, 17), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='95479215457186577315460887603281689611501581374433554641161475835178891870209')},
    {'date': datetime.datetime(2021, 8, 23), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='75804228130349846080122888708441842295980916946164453065125507061084692938753')},
    {'date': datetime.datetime(2021, 8, 26), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='65446')},
    {'date': datetime.datetime(2021, 8, 29), 'token': Token(registryAddress='0x3B3ee1931Dc30C1957379FAc9aba94D1C48a5405', tokenId='64896')},
<<<<<<< HEAD
    {'date': datetime.datetime(2021, 9, 1), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='85364157633350634373635596396121761067444146987595609300037457530101165981697')},]
=======
    {'date': datetime.datetime(2021, 9, 1), 'token': Token(registryAddress='0x495f947276749Ce646f68AC8c248420045cb7b5e', tokenId='85364157633350634373635596396121761067444146987595609300037457530101165981697')},
]
>>>>>>> main

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
                DateFieldFilter(fieldName=TokenTransfersTable.c.blockDate.key, gte=startDate, lt=endDate),
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
        batchSize = 5
        for startBlockNumber in reversed(range(latestProcessedBlockNumber, latestBlockNumber + 1, batchSize)):
            endBlockNumber = min(startBlockNumber + batchSize, latestBlockNumber + 1)
            await self.workQueue.send_message(message=ProcessBlockRangeMessageContent(startBlockNumber=startBlockNumber, endBlockNumber=endBlockNumber).to_message())

    async def process_block_range(self, startBlockNumber: int, endBlockNumber: int) -> None:
        blockNumbers = list(range(startBlockNumber, endBlockNumber))
        await self.process_blocks(blockNumbers=blockNumbers)

    async def process_blocks(self, blockNumbers: Sequence[int]) -> None:
        await asyncio.gather(*[self.process_block(blockNumber=blockNumber) for blockNumber in blockNumbers])

    async def _create_token_transfer(self, retrievedTokenTransfer: RetrievedTokenTransfer) -> None:
        try:
            await self.saver.create_token_transfer(transactionHash=retrievedTokenTransfer.transactionHash, registryAddress=retrievedTokenTransfer.registryAddress, fromAddress=retrievedTokenTransfer.fromAddress, toAddress=retrievedTokenTransfer.toAddress, tokenId=retrievedTokenTransfer.tokenId, value=retrievedTokenTransfer.value, gasLimit=retrievedTokenTransfer.gasLimit, gasPrice=retrievedTokenTransfer.gasPrice, gasUsed=retrievedTokenTransfer.gasUsed, blockNumber=retrievedTokenTransfer.blockNumber, blockHash=retrievedTokenTransfer.blockHash, blockDate=retrievedTokenTransfer.blockDate)
        except DuplicateValueException:
            logging.debug('Ignoring previously saved transfer')

    async def process_block(self, blockNumber: int) -> None:
        retrievedTokenTransfers = await self.blockProcessor.get_transfers_in_block(blockNumber=blockNumber)
        logging.info(f'Found {len(retrievedTokenTransfers)} token transfers in block #{blockNumber}')
        for retrievedTokenTransfer in retrievedTokenTransfers:
            logging.debug(f'Transferred {retrievedTokenTransfer.tokenId} from {retrievedTokenTransfer.fromAddress} to {retrievedTokenTransfer.toAddress}')
            logging.debug(f'Paid {retrievedTokenTransfer.value / 100000000000000000.0}Ξ ({retrievedTokenTransfer.gasUsed * retrievedTokenTransfer.gasPrice / 100000000000000000.0}Ξ) to {retrievedTokenTransfer.registryAddress}')
            logging.debug(f'OpenSea url: https://opensea.io/assets/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
            logging.debug(f'OpenSea api url: https://api.opensea.io/api/v1/asset/{retrievedTokenTransfer.registryAddress}/{retrievedTokenTransfer.tokenId}')
        for retrievedTokenTransfersChunk in list_util.generate_chunks(retrievedTokenTransfers, 30):
            await asyncio.gather(*[self._create_token_transfer(retrievedTokenTransfer=retrievedTokenTransfer) for retrievedTokenTransfer in retrievedTokenTransfersChunk])

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
