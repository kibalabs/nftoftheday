import asyncio
import logging
import os
import time
from typing import List

import boto3
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient


async def post():
    sqsClient = boto3.client(service_name='sqs', region_name='us-east-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    requester = Requester()
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    sqsResponse = sqsClient.list_queues()
    sqsQueueUrls = sqsResponse.get("QueueUrls")
    messages =[]
    for sqsQueueUrl in sqsQueueUrls:
        len = sqsClient.get_queue_attributes(QueueUrl=sqsQueueUrl, AttributeNames=['ApproximateNumberOfMessages',])
        len = len.get("Attributes").get("ApproximateNumberOfMessages")
        messages.append(f"{sqsQueueUrl}: {len}\n")
    
    text = f'AWS SQS Stats:\n{"".join(map(str,messages))}'
    await slackClient.post(text)
    logging.info("Going to sleep for 1 hour")
    time.sleep(3600)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(post())
