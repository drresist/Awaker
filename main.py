import csv
import json
import os
import time
from loguru import logger
import requests
import telebot
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OW_API = os.getenv("OW_API")
TG_BOT_API = os.getenv("TG_BOT_API")
CHAT_ID = os.getenv("CHAT_ID")

# Check that environment variables are set
if not OW_API or not TG_BOT_API or not CHAT_ID:
    raise ValueError("Environment variables OW_API, TG_BOT_API, and CHAT_ID must be set.")

# Configure logger
logger.add("app.log", retention="10 days")  # Cleanup after some time

def log_error_and_continue(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None
    return wrapper

@log_error_and_continue
def get_weather() -> str | None:
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={OW_API}&lang=ru&units=metric"
    weather_data = requests.get(url)
    
    logger.info(f"Requesting weather data from OW")
    
    with open('icons.json', 'r', encoding='utf-8') as f:
        icons = json.load(f)
        
    logger.info("Weather data received with status code: " + str(weather_data.status_code))
    
    if weather_data.status_code == 200:
        weather_data = weather_data.json()
        text = f"Погода {icons[weather_data['weather'][0]['icon']]}: {int(weather_data['main']['temp'])}°C" \
               f" (ощ. {int(weather_data['main']['feels_like'])}°C), " \
               f"{weather_data['weather'][0]['description']}"
        logger.info(text)
        return text
    else:
        return None

@log_error_and_continue
def get_birthday() -> str | None:
    today_date = f"{datetime.today().day}-{datetime.today().month}"
    names = []

    with open("./birthdays.csv", "r") as file:
        csv_file = csv.DictReader(file)
        
        for line in csv_file:
            if line["date"] == today_date:
                names.append(line["Name"])
                
        logger.info(f"Found {len(names)} names")
        
    if names:
        return "День рождения у 🎂: \n" + '\n'.join(names)
    else:
        return None

def create_message() -> str:
    weather = get_weather() or "Ошибка при получении погоды."
    birthday = get_birthday() or "Сегодня нет дней рождения."

    return f"*Всем привет!👋*\n" \
           f"{weather}\n" \
           f"{birthday}\n"

def send_message(text: str) -> None:
    bot = telebot.TeleBot(token=TG_BOT_API)
    
    logger.info(f"Sending message {text}")
    
    bot.send_message(
        text=text,
        chat_id=CHAT_ID,
        disable_notification=True,
        parse_mode="markdown"
    )

def main() -> None:
    while True:
        # Get the current time in UTC+3
        current_time_utc3 = datetime.utcnow() + timedelta(hours=3)
        
        # Check if it's within the desired time range (e.g., between 8 AM and 9 AM in UTC+3)
        if current_time_utc3.hour == 8:
            try:
                send_message(create_message())
            except Exception as e:
                logger.error(f"An error occurred: {e}")
        
        # Sleep for a certain interval (e.g., 1 hour) before checking the time again
        time.sleep(3600)


if __name__ == '__main__':
    main()
