import json
import sys
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
    """
    Stores configuration settings for the application.

    Attributes:
        OW_API (str): The OpenWeather API key.
        TG_BOT_API (str): The Telegram Bot API key. Defaults to "None".
        CHAT_ID (str): The Telegram chat ID. Defaults to "None".
        PG_HOST (str): The PostgreSQL host.
        PG_DB (str): The PostgreSQL database name.
        PG_USER (str): The PostgreSQL username.
        PG_PASS (str): The PostgreSQL password.
        GIGA_TOGGLE (bool): Toggle for Gigachain functionality. Defaults to True.
        HOLIDAYS_URL (str): The URL for holiday data.
    """
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
    """
    Initializes the logger configuration.

    Adds log handlers for standard output with log level "INFO",
    standard error with log level "ERROR", and a file named "logs/debug.log"
    with log level "DEBUG".
    """
    logger.add(sys.stdout, level="INFO")
    logger.add(sys.stderr, level="ERROR")
    logger.add("logs/debug.log", level="DEBUG")


def initialize_config():
    load_dotenv()
    return Config()


def log_error_and_continue(func):
    """
    Decorator that logs any exceptions that occur during the execution of the wrapped function
    and allows the function to continue running.

    Args:
        func (callable): The function to be wrapped.

    Returns:
        callable: The decorated version of the function.

    Example:
        @log_error_and_continue
        def divide(a, b):
            return a / b

        result = divide(10, 0)
        # Logs an error and returns None
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    return wrapper



# Assuming initialize_config and icons.json loading happens outside the function
config = initialize_config()
with open("icons.json", "r", encoding="utf-8") as f:
    icons_mapping = json.load(f)

@log_error_and_continue
def get_weather() -> str | None:
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={config.OW_API}&lang=ru&units=metric"
    logger.info("Requesting weather data from OW")

    with requests.get(url) as weather_response:
        logger.info(f"Weather data received with status code: {weather_response.status_code}")

        if weather_response.status_code != 200:
            return None
        weather_data = weather_response.json()
        return format_weather_data(weather_data, icons_mapping)

def format_weather_data(weather_data: dict, icons_mapping: dict) -> str:
    description = weather_data["weather"][0]["description"]
    icon_code = weather_data["weather"][0]["icon"]
    temperature = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]
    pressure = weather_data["main"]["pressure"] * 0.75  # Convert pressure to mmHg
    weather_icon = icons_mapping.get(icon_code, "?")

    return f"""
Сейчас в городе {weather_data['name']}:

{weather_icon} {description}

🌡️ Температура воздуха — {temperature:.2f}°C
👀 Чувствуется как — {feels_like:.1f}°C
💦 Влажность — {humidity}%
💨 Ветер — {wind_speed} м/с
📍 Атмосферное давление — {pressure:.0f} мм рт.ст.
    """


@log_error_and_continue
def get_birthdays_db() -> str | None:
    """
    Retrieves today's birthdays from the database and returns a formatted string.

    Returns:
        str | None: A string containing the birthdays if there are any, otherwise None.
    """
    config = initialize_config()
    conn = psycopg2.connect(
        host=config.PG_HOST,
        database=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASS,
    )
    today_date = f"{datetime.now().day}-{datetime.now().month}"
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
    """
    Creates a message containing weather, birthdays, and holidays information.

    Returns:
        str: The formatted message.
    """
    config = initialize_config()
    weather = f"{get_weather()} \n*{get_hokku()}*" if config.GIGA_TOGGLE else get_weather() or "Ошибка при получении погоды."
    birthday = get_birthdays_db() if (birthdays := get_birthdays_db()) else ""
    holidays = get_holidays(config.HOLIDAYS_URL) if (holidays := get_holidays(config.HOLIDAYS_URL)) else ""
    return f"*Всем привет!👋*\n {weather}\n {birthday}\n {holidays}\n"



def send_message(text: str) -> None:
    """
    Sends a message using the Telegram Bot API.

    Args:
        text (str): The text of the message to send.

    Returns:
        None
    """
    config = initialize_config()
    bot = telebot.TeleBot(token=config.TG_BOT_API)

    logger.info(f"Sending message {text}")

    bot.send_message(
        text=text,
        chat_id=config.CHAT_ID,
        disable_notification=True,
        parse_mode="markdown",
    )



def parser_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for the Weather and Birthday Bot.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Weather and Birthday Bot")
    parser.add_argument("--test", action="store_true", help="Enable testing mode")
    parser.add_argument(
        "--hour", type=int, default=8, help="Hour for sending messages (24-hour format)"
    )
    parser.add_argument(
        "--minute", type=int, default=0, help="Minute for sending messages"
    )

    return parser.parse_args()


    return parser.parse_args()


def main_loop():
    while True:
        current_time_utc3 = datetime.now(timezone.utc) + timedelta(hours=3)
        if current_time_utc3.hour == 8 and current_time_utc3.minute == 0:
            try:
                send_message(create_message())
            except Exception as e:
                logger.error(f"An error occurred: {e}")

        time.sleep(60)


def test_app():
    """
    Tests the application by sending a test message.

    Raises:
        Exception: If an error occurs during testing.
    """
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
