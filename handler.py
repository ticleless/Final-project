import json
import boto3
import uuid
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

HOOK_URL = os.environ['HOOK_URL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

data = {
    "result": "success",
    "error_code": "0",
    "device_id": "39278391",
        "coord": {
            "lon": -8.61,
            "lat": 41.15
          },
    "server_time": "1416895635000",
        "temperature": 38.5,
        "pressure": 1014,
        "humidity": 88,
        "co2": 413.2,
}

def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))
    
    client = boto3.client('kinesis')

    # discord webhook
    if event is None:
        discord_message = {
            'username': 'TeamD',
            'avatar_url': 'https://i.imgur.com/4M34hi2.png',
            'content': 'Payload is null'
        }
        payload = json.dumps(discord_message).encode('utf-8')
        
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': len(payload),
            'Host': 'discord.com',
            'user-agent': 'Mozilla/5.0'
        }

        req = Request(HOOK_URL, payload, headers)

        try:
            response = urlopen(req)
            response.read()
            logger.info("Message posted to discord")
        except HTTPError as e:
            logger.error("Request failed: %d %s", e.code, e.reason)
            logger.error(e.read())
        except URLError as e:
            logger.error("Server connection failed: %s", e.reason)
    
    
    #kinesis Put_Record
    response = client.put_record(
        StreamName='test-kyy',
        Data=json.dumps(event),
        PartitionKey=str(uuid.uuid4())
    )
    
    
    print(response)
    return response
