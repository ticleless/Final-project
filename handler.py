import json
import boto3
import uuid

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
    client = boto3.client('kinesis')
    
    response = client.put_record(
        StreamName='test-kyy',
        Data=json.dumps(event),
        PartitionKey=str(uuid.uuid4())
    )
    
    
    print(response)
    return response
