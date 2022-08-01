import json
import boto3
import uuid
import logging
import os
import random

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

HOOK_URL = os.environ['HOOK_URL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)
    
#random generator
def random_generator():
    valueList = iter([34,39,1000,1015,40,100,400,415])
    resultList = []
    for x, y in zip(valueList, valueList):
        # print(x,y)
        result = random.randrange(x,y)
        resultList.append(result)
        # print(result)
    data = {
        "result": "success",
        "error_code": "0",
        "device_id": "39278391",
            "coord": {
                "lon": -8.61,
                "lat": 41.15
            },
        "server_time": "1416895635000",
            "temperature": resultList[0],
            "pressure": resultList[1],
            "humidity": resultList[2],
            "co2": resultList[3],
    }
    return data
        
#put record on stream
def put_record_stream(event):

    client = boto3.client('kinesis')
    response = client.put_record(
        StreamName='test-kyy',
        Data=json.dumps(event),
        PartitionKey=str(uuid.uuid4())
    )
    return response

def discord_wehbook(event):
    # discord webhook

    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0])
    logger.info("Message: " + str(message))

    
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

def lambda_handler(event, context):
    if event is None:
        discord_wehbook()
    data = random_generator()
    result = put_record_stream(data)
    
    print(result)
    return result
   

