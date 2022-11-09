import asyncio
import datetime
import json
import os
import sys

import asyncclick as click
from core import logging
from core.store.database import Database
from core.util import chain_util
from core.util import date_util
from eth_account.messages import encode_defunct
from web3.auto import w3

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from notd.badge_manager import BadgeManager
from notd.badge_processor import BadgeProcessor
from notd.model import COLLECTION_RUDEBOYS_ADDRESS
from notd.store.retriever import Retriever
from notd.store.saver import Saver


@click.command()
async def backfill_collection_activities():
    publicKey = chain_util.normalize_address(os.environ['ACCOUNT_ADDRESS'])
    privateKey = os.environ['PRIVATE_KEY']

    databaseConnectionString = Database.create_psql_connection_string(username=os.environ["DB_USERNAME"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], port=os.environ["DB_PORT"], name=os.environ["DB_NAME"])
    database = Database(connectionString=databaseConnectionString)
    saver = Saver(database=database)
    retriever = Retriever(database=database)
    badgeProcessor = BadgeProcessor(retriever=retriever, saver=saver)
    badgeManager = BadgeManager(retriever=retriever, saver=saver, workQueue=None, badgeProcessor=badgeProcessor)

    await database.connect()

    achievedDate = datetime.datetime.now()
    registryAddress = COLLECTION_RUDEBOYS_ADDRESS
    ownerAddress = '0x18090cDA49B21dEAffC21b4F886aed3eB787d032'
    assignerAddress = publicKey
    badgeKey = 'TEST_BADGE'

    command = 'ASSIGN_BADGE'
    message = {
        'registryAddress': registryAddress,
        'ownerAddress': ownerAddress,
        'badgeKey': badgeKey,
        'assignerAddress': assignerAddress,
        'achievedDate': date_util.datetime_to_string(achievedDate),
    }
    signatureMessage = json.dumps({ 'command': command, 'message': message }, indent=2, ensure_ascii=False)
    message = encode_defunct(text=signatureMessage)
    signedMessage = w3.eth.account.sign_message(message, private_key=privateKey)
    signature = signedMessage.signature.hex()
    await badgeManager.assign_badge(registryAddress=registryAddress, ownerAddress=ownerAddress, badgeKey=badgeKey, assignerAddress=assignerAddress, achievedDate=achievedDate, signature=signature)

    await database.disconnect()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(backfill_collection_activities())
