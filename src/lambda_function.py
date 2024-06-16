import json
import os
import requests
from datetime import datetime


def current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return (current_time)

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
    

def get_current_weather():
    WEATHER_API_TOKEN = os.environ.get('WEATHER_API_TOKEN')
    send_text = 'http://api.openweathermap.org/data/2.5/weather?lat=52.26131518259818&lon=20.95682398281323&appid=' + WEATHER_API_TOKEN + \
                '&units=metric'
    try:
        response = requests.get(send_text)
        current_temperature = response.json()['main']
    except:
        current_temperature = "Unknown"
    
    return response.json()

def get_forecast_weather():
    WEATHER_API_TOKEN = os.environ.get('WEATHER_API_TOKEN')
    send_text = 'http://api.openweathermap.org/data/2.5/forecast?lat=52.26131518259818&lon=20.95682398281323&appid=' + WEATHER_API_TOKEN + \
                '&units=metric'
    response = requests.get(send_text)
    return response.json()

def lambda_handler(event, context):
    print(event)
    print(context)

    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID')
    cur_tm = current_time()

    if event.get('message').get('text') == '/weather5':
        forecast_weather_json = get_forecast_weather()
        #formatting the message to be sent to the bot
        try:
            forecast_weather = f"{get_weather_emoticon(forecast_weather_json['list'][0]['weather'][0]['main'])} {forecast_weather_json['list'][0]['weather'][0]['main']} {forecast_weather_json['list'][0]['main']['temp']}°C"
        except:
            forecast_weather = "Unknown"

        bot_message = f"Forecast weather is {forecast_weather}"
        send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                    '&parse_mode=HTML&text=' + bot_message
        response = requests.get(send_text)
        #print(response)
        return {
            'statusCode': 200,
            #'body': json.dumps('Hello from Lambda!')
            'body': forecast_weather_json
        }
    else:
        current_weather_json = get_current_weather()
        #formatting the message to be sent to the bot
        try:
            current_weather = f"{get_weather_emoticon(current_weather_json['weather'][0]['main'])} {current_weather_json['weather'][0]['main']} {current_weather_json['main']['temp']}°C"
        except:
            current_weather = "Unknown"

        bot_message = f"Current weather is {current_weather}"
        send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                    '&parse_mode=HTML&text=' + bot_message
        response = requests.get(send_text)
        #print(response)    
        return {
            'statusCode': 200,
            #'body': json.dumps('Hello from Lambda!')
            'body': current_weather_json
        }

#fix for local testing
if __name__ == "__main__":
    #reading event and context from the file
    with open('events/event.json') as f:
        event = json.load(f)
    print(event)
    context = {}
    lambda_handler(event, context)