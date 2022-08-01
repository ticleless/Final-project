import json
import boto3
import uuid
import random

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
    return data;
        
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
    return result;
   

