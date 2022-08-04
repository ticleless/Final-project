import json
import boto3
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

HOOK_URL = os.environ['HOOK_URL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def discord_alarm(data, attribute):
    logger.info("Event: " + str(data))

    username = "TeamD SmartFarm"
    message_coord = data["dst"]
    message_attribute = '온도'
    content_message = f'[경보] {message_coord} {message_attribute} 기준치 초과!'



    discord_message = {
        'username': username,
        'avatar_url': 'https://i.imgur.com/4M34hi2.png',
        'content': 'test'
    }
    
    if attribute == 'temperature':
        message_temperature = f'현재 온도: {data["temperature"]}도'
        message_attribute = '온도'
        discord_message = {
        'username': username,
        'content': content_message + message_temperature
        }
    
    if attribute == 'pressure':
        message_pressure = f'현재 기압: {data["pressure"]}hPa'
        message_attribute = "기압"
        discord_message = {
        'username': username,
        'content': content_message + message_pressure
        }
    
    if attribute == 'humidity':
        message_humidity = f'현재 습도: {data["humidity"]}%'
        message_attribute = "습도"
        discord_message = {
        'username': username,
        'content': content_message + message_humidity
        }
    
    if attribute == 'co2':
        message_co2 = f'현재 Co2 농도: {data["co2"]}ppm'
        message_attribute = "Co2 농도"
        discord_message = {
        'username': username,
        'content': content_message + message_co2
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
    json_event = json.dumps(event)
    
    print(json_event)
    s3_key = event['Records'][0]['s3']['object']['key']
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
    print(response)
    data = response['Body'].read()
    print(data, 'data')
    load_data = json.loads(data)

    
    temperature = load_data["temperature"]
    pressure = load_data["pressure"]
    humidity= load_data["humidity"]
    co2 = load_data["co2"]
    
    temperature_value = 31
    pressure_value = 900
    humidity_value = 85
    co2_value = 410

    if temperature > temperature_value:
        discord_alarm(load_data, 'temperature')
        print('alarm temperature')

    if pressure > pressure_value:
        discord_alarm(load_data, 'pressure')
        print('alarm pressure')

    if humidity > humidity_value:
        discord_alarm(load_data, 'humidity')
        print('alarm humidity')
    
    if co2 > co2_value:
        discord_alarm(load_data, 'co2')
        print('alarm co2')

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

