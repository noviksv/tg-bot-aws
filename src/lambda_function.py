import json
import os
from decimal import Decimal
from datetime import datetime
import requests
import boto3



WEATHER_API_TOKEN = os.environ.get('WEATHER_API_TOKEN')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
#BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID')


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('weather_bot_settings')


def extract_chat_id(payload):
    try:
        # Parse the payload JSON
        event = json.loads(payload)
        
        # Extract the chat ID from the parsed event
        chat_id = event['message']['chat']['id']
        
        return chat_id
    except (KeyError, json.JSONDecodeError) as e:
        # Handle potential errors
        print(f"Error extracting chat ID: {e}")
        return None


def get_weather_emoticon(weather):
    if weather == "Clear":
        return "☀️"
    elif weather == "Clouds":
        return "☁️"
    elif weather == "Rain":
        return "🌧️"
    elif weather == "Drizzle":
        return "🌦️"
    elif weather == "Thunderstorm":
        return "⛈️"
    elif weather == "Snow":
        return "❄️"
    else:
        return "🤷"
    

def send_tg_msg(bot_message, chat_id):
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + str(chat_id) + \
                    '&parse_mode=HTML&text=' + bot_message
    response = requests.get(send_text)
    print("message was sent")
    response.raise_for_status()
    return response.json()


def get_current_weather():
    send_text = 'http://api.openweathermap.org/data/2.5/weather?lat=52.26131518259818&lon=20.95682398281323&appid=' + WEATHER_API_TOKEN + \
                '&units=metric'
    try:
        response = requests.get(send_text)
        current_temperature = response.json()['main']
    except:
        current_temperature = "Unknown"
    
    return response.json()

def get_forecast_weather(lat, lon):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'units': 'metric',
        'appid': WEATHER_API_TOKEN,
        'lat': lat,
        'lon': lon
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200 and response.json():
        return response.json()
    return None

def get_city_coordinates(city_name):
    base_url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': city_name,
        'limit': 1,
        'appid': WEATHER_API_TOKEN
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200 and response.json():
        location = response.json()[0]
        return location['lat'], location['lon']
    return None, None


def get_user_city(chat_id):
    try:
        response = table.get_item(Key={'chat_id': str(chat_id)})
        if 'Item' in response:
            return response['Item']
    except Exception as e:
        print(f"Error getting user city: {e}")
    return None



def set_user_city(chat_id, city):
    lat, lon = get_city_coordinates(city)
    if lat and lon:
        try:
            table.put_item(
                Item={
                    'chat_id': str(chat_id),  # Ensure chat_id is a string
                    'city': city,
                    'lat': Decimal(str(lat)),  # Convert to Decimal for DynamoDB
                    'lon': Decimal(str(lon))  # Convert to Decimal for DynamoDB
                }
            )
            return True
        except Exception as e:
            print(f"Error setting user city: {e}")
            return False
    return False


def lambda_handler(event, context):
    print(f"event = {event}")
    print(f"context = {context}")
    # Check if the body is a string and needs parsing
    event_body = event.get("body")
    
    # If the body is already a dictionary, skip parsing
    if isinstance(event_body, str):
        event_body = json.loads(event_body)

    # Instead of os.environ.get('BOT_CHAT_ID'), use:
    chat_id = extract_chat_id(json.dumps(event_body))
    print(f"Extracted chat_id: {chat_id}, Type: {type(chat_id)}")
    
    if chat_id is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Failed to extract chat ID from the event')
        }
    
    weather_json = {}

    message_text = event_body.get('message', {}).get('text', '').strip()
    
    if message_text.startswith('/setcity'):
        city = message_text.replace('/setcity', '').strip()
        if set_user_city(chat_id, city):
            bot_message = f"City set to {city}"
        else:
            bot_message = "Failed to set city. Please try again with a valid city name."
    
    elif message_text in ['/weather', '/weather5']:
        user_city = get_user_city(chat_id)
        if not user_city:
            bot_message = "Please set your city first using /setcity command"
        else:
            lat, lon = user_city['lat'], user_city['lon']
            if message_text == '/weather':
                weather_json = get_current_weather(lat, lon)
                if weather_json:
                    weather = f"{get_weather_emoticon(weather_json['weather'][0]['main'])} {weather_json['weather'][0]['main']} {weather_json['main']['temp']}°C"
                    bot_message = f"Current weather in {user_city['city']} is {weather}"
                else:
                    bot_message = "Failed to fetch weather data"
            else:  # /weather5
                weather_json = get_forecast_weather(lat, lon)
                if weather_json:
                    weather = f"{get_weather_emoticon(weather_json['list'][0]['weather'][0]['main'])} {weather_json['list'][0]['weather'][0]['main']} {weather_json['list'][0]['main']['temp']}°C"
                    bot_message = f"Forecast weather in {user_city['city']} is {weather}"
                else:
                    bot_message = "Failed to fetch forecast data"
    
    else:
        bot_message = "Unknown command. Available commands: /setcity [city name], /weather, /weather5"

    send_tg_msg(bot_message=bot_message, chat_id=chat_id)

    set_user_city(chat_id, 'Warsaw')
        
    # return {
    #     'statusCode': 200,
    #     #'body': json.dumps('Hello from Lambda!')
    #     'body': weather_json
    # }
    #print(get_city_coordinates('London'))

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(weather_json
        ),
        'isBase64Encoded': False
    }



#fix for local testing
if __name__ == "__main__":
    #reading event and context from the file
    with open('events/event.json') as f:
        event = json.load(f)
    print(event)
    context = {}
    lambda_handler(event, context)