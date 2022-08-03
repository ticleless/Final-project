import json
import boto3
import uuid
import random
import datetime
import dateutil.tz
import json
from json import JSONEncoder


#Json Encoding
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()


#random generator
def random_generator():
    #lon,lat Ulsan, Masan GawngJu YangYang Yeosu
    coordList = [[129.33,35.57],[128.58,35.22],[128.62,38.07],[126.90,35.18],[127.66,34.75]]
    coordValue = coordList[random.randrange(0,5)]
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
        "server_time": now,
            "temperature": resultList[0],
            "pressure": resultList[1],
            "humidity": resultList[2],
            "co2": resultList[3],
    }

    encodingJsonData = json.dumps(data, cls=DateTimeEncoder)
    

    return encodingJsonData
        
#put record on stream
def put_record_stream(event):

    client = boto3.client('kinesis')
    response = client.put_record(
        StreamName='test-stream',
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
   

