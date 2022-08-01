import json
import boto3

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    json_event = json.dumps(event)
    
    print(json_event)
    s3_key = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    print(response)
    data = response['Body'].read()
    print(data)
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }