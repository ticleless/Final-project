import json
import boto3
import uuid
import random
from datetime import datetime
    
#random generator
def random_generator():
    #temp, pressure, humiditym co2
    valueList = iter([34,40,1000,1015,40,100,400,415])
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
        "server_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
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
        StreamName='test-stream',
        Data=json.dumps(event),
        PartitionKey=str(uuid.uuid4())
    )
    return response


def lambda_handler(event, context):
    data = random_generator()
    print(data)
    result = put_record_stream(data)  
    print(result)
    return result
   

