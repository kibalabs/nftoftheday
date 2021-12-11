import asyncio
import logging
import os
import boto3
import time
from core.queues.sqs_message_queue import SqsMessageQueue
from core.requester import Requester
from core.slack_client import SlackClient

async def post():
    sqsClient = boto3.client(service_name='sqs', region_name='us-east-1', aws_access_key_id=os.environ['AWS_KEY'], aws_secret_access_key=os.environ['AWS_SECRET'])
    workQueue = SqsMessageQueue(sqsClient=sqsClient, queueUrl='https://sqs.us-east-1.amazonaws.com/113848722427/test1')
    requester = Requester()
    slackClient = SlackClient(webhookUrl=os.environ['SLACK_WEBHOOK_URL'], requester=requester, defaultSender='worker', defaultChannel='notd-notifications')
    queuesResponse = await workQueue.get_queues()
    queueUrls = queuesResponse.get("QueueUrls")

    messages =[]
    for queueUrl in queueUrls:
        len = await workQueue.get_queues_attribute(queue=queueUrl)
        len = len.get("Attributes").get("ApproximateNumberOfMessages")
        messages.append(f"queue_name {queueUrl}: queue_size {len} ")
    
    text = f'AWS SQS Stats: {"".join(map(str,messages))}'
    slackClient.post(text)
    time.sleep(3600)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(post())
