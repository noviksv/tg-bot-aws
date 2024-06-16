import json
import os
import requests
from datetime import datetime

WEATHER_API_TOKEN = os.environ.get('WEATHER_API_TOKEN')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID')


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
    

def send_tg_msg(bot_message):
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                    '&parse_mode=HTML&text=' + bot_message
    response = requests.get(send_text)
    response.raise_for_status()


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
    print(event)
    print(context)


    if event.get('message').get('text') == '/weather5':
        weather_json = get_forecast_weather()
        #formatting the message to be sent to the bot
        try:
            weather = f"{get_weather_emoticon(weather_json['list'][0]['weather'][0]['main'])} {weather_json['list'][0]['weather'][0]['main']} {weather_json['list'][0]['main']['temp']}°C"
        except:
            weather = "Unknown"
        bot_message = f"Forecast weather is {weather}"

    else:
        weather_json = get_current_weather()
        #formatting the message to be sent to the bot
        try:
            weather = f"{get_weather_emoticon(weather_json['weather'][0]['main'])} {weather_json['weather'][0]['main']} {weather_json['main']['temp']}°C"
        except:
            weather = "Unknown"

        bot_message = f"Current weather is {weather}"
    
    send_tg_msg(bot_message=bot_message )
        
    return {
        'statusCode': 200,
        #'body': json.dumps('Hello from Lambda!')
        'body': weather_json
    }




#fix for local testing
if __name__ == "__main__":
    #reading event and context from the file
    with open('events/event.json') as f:
        event = json.load(f)
    print(event)
    context = {}
    lambda_handler(event, context)