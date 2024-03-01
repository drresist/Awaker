import csv
import json
import os
import time
from loguru import logger
import requests
import telebot
from datetime import datetime, timedelta
from dotenv import load_dotenv
import psycopg2

from giga_srv import get_weather_description


class Config:
    def __init__(self):
        self.OW_API = os.getenv("OW_API")
        self.TG_BOT_API = os.getenv("TG_BOT_API")
        self.CHAT_ID = os.getenv("CHAT_ID")
        self.PG_HOST = os.getenv("PG_HOST")
        self.PG_DB = os.getenv("PG_DB")
        self.PG_USER = os.getenv("PG_USER")
        self.PG_PASS = os.getenv("PG_PASS")
        self.GIGA_TOGGLE = False

def initialize_logger():
    logger.add("app.log", retention="10 days")


def initialize_config():
    load_dotenv()
    return Config()


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
    config = initialize_config()
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={config.OW_API}&lang=ru&units=metric"
    weather_data = requests.get(url)

    logger.info(f"Requesting weather data from OW")

    with open('icons.json', 'r', encoding='utf-8') as f:
        icons = json.load(f)

    logger.info("Weather data received with status code: " + str(weather_data.status_code))

    if weather_data.status_code == 200:
        logger.info(weather_data.json())
        weather_data = weather_data.json()
        text = f"Погода {icons[weather_data['weather'][0]['icon']]}: {int(weather_data['main']['temp'])}°C" \
               f" (ощущается как {int(weather_data['main']['feels_like'])}°C), " \
               f"{weather_data['weather'][0]['description']}, " \
               f"влажность: {weather_data['main']['humidity']}%"
        logger.info(text)
        return text
    else:
        return None


@log_error_and_continue
def get_birthdays_db() -> str | None:
    config = initialize_config()
    conn = psycopg2.connect(
        host=config.PG_HOST,
        database=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASS
    )
    today_date = f"{datetime.today().day}-{datetime.today().month}"
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM birthdays")
    birthdays = cursor.fetchall()
    cursor.close()
    conn.close()

    birthday_list = [f"{birthday[1]}" for birthday in birthdays if birthday[0] == today_date]
    birthday_string = "\n".join(birthday_list)
    logger.info(f"Found {len(birthday_list)} birthdays")

    if not birthday_list:
        return ""
    return "День рождения у 🎂: \n" + '\n'.join(birthday_list)


def create_message() -> str:
    config = initialize_config()
    if config.GIGA_TOGGLE:
        weather = get_weather_description(get_weather())
    else:
        weather = get_weather() or "Ошибка при получении погоды."
    birthday = get_birthdays_db() or ""
    return f"*Всем привет!👋*\n" \
           f"{weather}\n" \
           f"{birthday}\n"


def send_message(text: str) -> None:
    config = initialize_config()
    bot = telebot.TeleBot(token=config.TG_BOT_API)

    logger.info(f"Sending message {text}")

    bot.send_message(
        text=text,
        chat_id=config.CHAT_ID,
        disable_notification=True,
        parse_mode="markdown"
    )


def main_loop():
    while True:
        current_time_utc3 = datetime.utcnow() + timedelta(hours=3)
        if current_time_utc3.hour == 8 and current_time_utc3.minute == 0:
            try:
                send_message(create_message())
            except Exception as e:
                logger.error(f"An error occurred: {e}")

        time.sleep(60)


def main():
    initialize_logger()
    main_loop()


if __name__ == '__main__':
    main()
