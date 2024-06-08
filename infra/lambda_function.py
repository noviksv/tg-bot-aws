import json
import os
import requests
from datetime import datetime


def current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return (current_time)

def get_current_weather():
    WEATHER_API_TOKEN = os.environ.get('WEATHER_API_TOKEN')
    send_text = 'http://api.openweathermap.org/data/2.5/weather?lat=52.26131518259818&lon=20.95682398281323&appid=' + WEATHER_API_TOKEN + \
                '&units=metric'
    response = requests.get(send_text)
    current_temperature = response.json()['main']   
    
    return current_temperature

def lambda_handler(event, context):

    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID')
    cur_tm = current_time()
    current_weather = get_current_weather()
    bot_message = f"Current weather is ```{current_weather}```"
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + \
                '&parse_mode=HTML&text=' + bot_message
    response = requests.get(send_text)
    #print(response)    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

