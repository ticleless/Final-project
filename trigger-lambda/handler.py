import json
import boto3
import uuid
import random
import datetime
import dateutil.tz
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from json import JSONEncoder

HOOK_URL = os.environ['HOOK_URL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Json Encoding
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()


#random generator
def random_generator():
    #lon,lat Busan, Incheon, Gawngju, Daejon, Jeju
    coordList = [[129.075,35.18],[126.97,37.57],[127.25,37.43],[128.10,35.19],[126.71,35.96]]
    #Busan, Incheon, Gawngju, Daejon, Jeju
    mapList = ["Busan","Incheon","Gwangju","Daejeon","Jeju"]
    randomValue = random.randrange(0,5)
    coordValue = coordList[randomValue]
    
    #temp, pressure, humidity, co2
    valueList = iter([30,40,950,1015,40,100,370,415])
    resultList = []
    for x, y in zip(valueList, valueList):
        # print(x,y)
        result = random.randrange(x,y)
        resultList.append(result)
        # print(result)
    eastern = dateutil.tz.gettz('Asia/Seoul')
    now = datetime.datetime.now(tz=eastern)
    data = {
        "result": "success",
        "error_code": "0",
        "device_id": "39278391",
            "coord": {
                "lon": coordValue[0],
                "lat": coordValue[1]
            },
        "dst": mapList[randomValue],
        "server_time": now,
            "temperature": resultList[0],
            "pressure": resultList[1],
            "humidity": resultList[2],
            "co2": resultList[3],
    }

    encodingJsonData = json.dumps(data, cls=DateTimeEncoder)
    

    return encodingJsonData

def payload_alarm():
    discord_message = {
            'username': 'TeamD Error',
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
        
#put record on stream
def put_record_stream(event):

    client = boto3.client('kinesis')
    response = client.put_record(
        StreamName='test-kyy',
        Data=event,
        PartitionKey=str(uuid.uuid4())
    )
    return response


def lambda_handler(event, context):
    data = random_generator()
    print(data)
    result = put_record_stream(data)  
    print(result)
    return result
   

