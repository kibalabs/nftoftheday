import os
import sys
import asyncio

import sqlalchemy
# from sqlalchemy.sql import functions as sqlalchemyfunc
import logging
from core.http.basic_authentication import BasicAuthentication
from core.store.database import Database
from core.requester import Requester
from core.web3.eth_client import RestEthClient
from core.util import list_util

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.store.saver import Saver
from notd.store.retriever import Retriever

from notd.token_staking_processor import TokenStakingProcessor
from notd.store.schema import TokenTransfersTable
from notd.store.schema import TokenStakingsTable
from notd.model import CREEPZ_STAKING_ADDRESS

async def main():
    ethNodeUsername = os.environ["ETH_NODE_USERNAME"]
    ethNodePassword = os.environ["ETH_NODE_PASSWORD"]
    ethNodeUrl = os.environ["ETH_NODE_URL"]
    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    ethNodeAuth = BasicAuthentication(username=ethNodeUsername, password=ethNodePassword)
    ethNodeRequester = Requester(headers={'Authorization': f'Basic {ethNodeAuth.to_string()}'})
    ethClient = RestEthClient(url=ethNodeUrl, requester=ethNodeRequester)
    tokenStakingProcessor = TokenStakingProcessor(ethClient=ethClient, retriever=retriever)
    
    await database.connect()
    ownerQuery = (
        sqlalchemy.select(TokenTransfersTable.c.fromAddress.distinct())
        .where((TokenTransfersTable.c.toAddress == CREEPZ_STAKING_ADDRESS))
    )
    stakerAddressesResult = await retriever.database.execute(query=ownerQuery)
    stakerAddresses = [stakerAddress for stakerAddress, in list(stakerAddressesResult)]
    for index, stakerAddress in enumerate(stakerAddresses):
        print(f'index: {index}')
        retrievedTokenStakings = await tokenStakingProcessor.retrieve_owner_token_stakings(ownerAddress=stakerAddress, stakingAddress=CREEPZ_STAKING_ADDRESS)
        query = (
            sqlalchemy.select(TokenStakingsTable.c.tokenStakingId)
            .where((TokenStakingsTable.c.ownerAddress == stakerAddress))
        )
        async with saver.create_transaction() as connection:
            result = await retriever.database.execute(query=query, connection=connection)
            tokenStakingIdsToDelete = [tokenStakingId for tokenStakingId, in result]
            retrievedTokenStakings = [ elem for elem in retrievedTokenStakings if elem != '']
            logging.info(f'Deleting {len(tokenStakingIdsToDelete)} tokenStaking.')
            await saver.delete_token_stakings(tokenStakingIds=tokenStakingIdsToDelete, connection=connection)
            logging.info(f'Saving {len(retrievedTokenStakings)} tokenStaking.')
            await saver.create_token_stakings(retrievedTokenStakings=retrievedTokenStakings, connection=connection)
    await database.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
