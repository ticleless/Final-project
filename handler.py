import json

# data = {
#     "result": "success",
#     "error_code": "0",
#     "device_id: "39278391",
#         "coord": {
#             "lon": -8.61,
#             "lat": 41.15
#           },
#     "server_time": "1416895635000",
#         "temperature": 38.5,
#         "pressure": 1014,
#         "humidity": 88,
#         "co2": 413.2,
# }

def hello(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
