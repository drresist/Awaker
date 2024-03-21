from lxml import html
import json
import os
import time
from loguru import logger
import requests
import telebot
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import psycopg2
from holidays import get_holidays
from giga_srv import get_hokku
import argparse


class Config:
    def __init__(self):
        self.OW_API = os.getenv("OW_API")
        self.TG_BOT_API = os.getenv("TG_BOT_API", "None")
        self.CHAT_ID = os.getenv("CHAT_ID", "None")
        self.PG_HOST = os.getenv("PG_HOST")
        self.PG_DB = os.getenv("PG_DB")
        self.PG_USER = os.getenv("PG_USER")
        self.PG_PASS = os.getenv("PG_PASS")
        self.GIGA_TOGGLE = True
        self.HOLIDAYS_URL = 'https://my-calend.ru/holidays'


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

    logger.info("Requesting weather data from OW")

    with open("icons.json", "r", encoding="utf-8") as f:
        icons_mapping = json.load(f)

    logger.info(
        "Weather data received with status code: " + str(weather_data.status_code)
    )

    if weather_data.status_code == 200:
        weather_data = weather_data.json()
        # Extract relevant information
        description = weather_data["weather"][0]["description"]
        icon_code = weather_data["weather"][0]["icon"]
        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        pressure = weather_data["main"]["pressure"] * 0.75  # Convert pressure to mmHg
        # Get the icon for the current weather condition
        weather_icon = icons_mapping.get(icon_code, "?")

        # Format the text message
        text_message = f"""
Сейчас в городе {weather_data['name']}:

{weather_icon} {description}

🌡️ Температура воздуха — {temperature:.2f}°C
👀 Чувствуется как — {feels_like:.1f}°C
💦 Влажность — {humidity}%
💨 Ветер — {wind_speed} м/с
📍 Атмосферное давление — {pressure:.0f} мм рт.ст.
        """
        return text_message
    else:
        return None


@log_error_and_continue
def get_birthdays_db() -> str | None:
    config = initialize_config()
    conn = psycopg2.connect(
        host=config.PG_HOST,
        database=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASS,
    )
    today_date = f"{datetime.today().day}-{datetime.today().month}"
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM birthdays")
    birthdays = cursor.fetchall()
    cursor.close()
    conn.close()

    birthday_list = [
        f"{birthday[1]}" for birthday in birthdays if birthday[0] == today_date
    ]
    logger.info(f"Found {len(birthday_list)} birthdays")

    if not birthday_list:
        return ""
    return "День рождения у 🎂: \n" + "\n".join(birthday_list)



def create_message() -> str:
    config = initialize_config()
    if config.GIGA_TOGGLE:
        weather = f"{get_weather()} \n*{get_hokku()}*"
    else:
        weather = get_weather() or "Ошибка при получении погоды."
    birthday = get_birthdays_db() or ""
    holidays = get_holidays(config.HOLIDAYS_URL) or ""
    return f"*Всем привет!👋*\n {weather}\n {birthday}\n {holidays}\n"


def send_message(text: str) -> None:
    config = initialize_config()
    bot = telebot.TeleBot(token=config.TG_BOT_API)

    logger.info(f"Sending message {text}")

    bot.send_message(
        text=text,
        chat_id=config.CHAT_ID,
        disable_notification=True,
        parse_mode="markdown",
    )


def parser_arguments():
    parser = argparse.ArgumentParser(description="Weather and Birthday Bot")
    parser.add_argument("--test", action="store_true", help="Enable testing mode")
    parser.add_argument(
        "--hour", type=int, default=8, help="Hour for sending messages (24-hour format)"
    )
    parser.add_argument(
        "--minute", type=int, default=0, help="Minute for sending messages"
    )

    return parser.parse_args()


def main_loop():
    while True:
        current_time_utc3 = datetime.utcnow() + timedelta(hours=3)
        if current_time_utc3.hour == 8 and current_time_utc3.minute == 0:
            try:
                send_message(create_message())
            except Exception as e:
                logger.error(f"An error occurred: {e}")

        time.sleep(60)


def test_app():
    try:
        send_message(create_message())
        logger.info("Test message sent successfully.")
    except Exception as e:
        logger.error(f"An error occurred during testing: {e}")


def main():
    initialize_logger()
    args = parser_arguments()

    if args.test:
        test_app()
    else:
        main_loop()


if __name__ == "__main__":
    main()
