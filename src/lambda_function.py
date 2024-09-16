import json
import os
import requests
from datetime import datetime

WEATHER_API_TOKEN = os.environ.get('WEATHER_API_TOKEN')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
#BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID')


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

def get_forecast_weather():
    send_text = 'http://api.openweathermap.org/data/2.5/forecast?lat=52.26131518259818&lon=20.95682398281323&appid=' + WEATHER_API_TOKEN + \
                '&units=metric'
    response = requests.get(send_text)
    return response.json()

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
    
    if chat_id is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Failed to extract chat ID from the event')
        }
    
    weather_json = {}


    if event_body.get('message') and event_body.get('message').get('text') == '/weather5':
        weather_json = get_forecast_weather()
        #formatting the message to be sent to the bot
        try:
            weather = f"{get_weather_emoticon(weather_json['list'][0]['weather'][0]['main'])} {weather_json['list'][0]['weather'][0]['main']} {weather_json['list'][0]['main']['temp']}°C"
        except:
            weather = "Unknown"
        bot_message = f"Forecast weather is {weather}"

    elif event_body.get('message') and event_body.get('message').get('text') == '/weather':
        weather_json = get_current_weather()
        #formatting the message to be sent to the bot
        try:
            weather = f"{get_weather_emoticon(weather_json['weather'][0]['main'])} {weather_json['weather'][0]['main']} {weather_json['main']['temp']}°C"
        except:
            weather = "Unknown"
        bot_message = f"Current weather is {weather}"
    
    else: 
        bot_message = f"Unknown command"

    
    send_tg_msg(bot_message=bot_message, chat_id=chat_id)
        
    # return {
    #     'statusCode': 200,
    #     #'body': json.dumps('Hello from Lambda!')
    #     'body': weather_json
    # }
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