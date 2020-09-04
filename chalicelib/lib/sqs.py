import json
from typing import Callable, Dict, Any

import boto3


def send_message(
    enable_queue: bool,
    queue_name: str,
    message: Dict[str, Any],
    message_handler: Callable,
) -> None:
    """
    Send a message to SQS (if enable_queue is true) otherwise call the callback sycronously

    :param enable_queue: Decide if to actually use queue
    :param queue_name: The name of the queue as named during creation
    :param message: Dict containing the message payload
    :param message_handler: The function that is expected to handle the send message (only when queue is disabled)
    """
    if enable_queue:  # Send to real SQS queue
        client = boto3.client("sqs")
        queue_data = client.get_queue_url(QueueName=queue_name)
        client.send_message(
            QueueUrl=queue_data["QueueUrl"], MessageBody=json.dumps(message)
        )
    else:  # Handle sync, used for testing
        evt = dict(body=json.dumps(message), receiptHandle="")
        message_handler(dict(Records=[evt]), None)
