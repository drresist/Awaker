import csv
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

from giga_srv import get_hokku
import argparse


class Config:
    def __init__(self):
        self.OW_API = os.getenv("OW_API")
        self.TG_BOT_API = os.getenv("TG_BOT_API")
        self.CHAT_ID = os.getenv("CHAT_ID")
        self.PG_HOST = os.getenv("PG_HOST")
        self.PG_DB = os.getenv("PG_DB")
        self.PG_USER = os.getenv("PG_USER")
        self.PG_PASS = os.getenv("PG_PASS")
        self.GIGA_TOGGLE = True


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

    with open("icons.json", "r", encoding="utf-8") as f:
        icons_mapping = json.load(f)

    logger.info(
        "Weather data received with status code: " + str(weather_data.status_code)
    )

    if weather_data.status_code == 200:
        logger.info(weather_data.json())
        weather_data = weather_data.json()
        # Extract relevant information
        description = weather_data["weather"][0]["description"]
        icon_code = weather_data["weather"][0]["icon"]
        temperature = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]
        pressure = weather_data["main"]["pressure"] * 0.75  # Convert pressure to mmHg
        sunrise_timestamp = weather_data["sys"]["sunrise"]
        sunset_timestamp = weather_data["sys"]["sunset"]

        # Convert timestamps to human-readable time in UTC
        sunrise_utc = datetime.utcfromtimestamp(sunrise_timestamp)
        sunset_utc = datetime.utcfromtimestamp(sunset_timestamp)

        # Convert to Moscow time (UTC+3) by adding 3 hours
        moscow_timezone = timezone(timedelta(hours=3))
        sunrise_moscow = (
            sunrise_utc.replace(tzinfo=timezone.utc)
            .astimezone(moscow_timezone)
            .strftime("%H:%M:%S")
        )
        sunset_moscow = (
            sunset_utc.replace(tzinfo=timezone.utc)
            .astimezone(moscow_timezone)
            .strftime("%H:%M:%S")
        )

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
        logger.info(text_message)
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
    birthday_string = "\n".join(birthday_list)
    logger.info(f"Found {len(birthday_list)} birthdays")

    if not birthday_list:
        return ""
    return "День рождения у 🎂: \n" + "\n".join(birthday_list)


def get_today_holidays(url):
    # Fetch HTML content from the URL
    response = requests.get(url)
    if response.status_code == 200:
        # Parse HTML content
        tree = html.fromstring(response.content)
        xpath = "/html/body/div[1]/main/div[1]/article/section[1]/ul/li"

        # Get list of li elements based on the provided XPath
        li_elements = tree.xpath(xpath)

        # Create a dictionary to store the values
        li_values = {}

        # Iterate through each li element, extract the like value, and save it in the dictionary
        for li_element in li_elements:
            input_element = li_element.find("form/input")
            if input_element is not None:
                like_value = int(input_element.attrib["value"])
                li_values[li_element] = like_value

        # Sort the dictionary by like values
        sorted_li_values = dict(
            sorted(li_values.items(), key=lambda item: item[1], reverse=True)
        )

        # Retrieve text content for each li element
        text_dict = {}
        for li_element, like_count in sorted_li_values.items():
            li_text = li_element.text_content().strip()
            text_dict[li_text] = like_count
        logger.info(text_dict)
        return text_dict
    else:
        print("Failed to fetch HTML content from the URL.")
        return None


def create_message() -> str:
    config = initialize_config()
    if config.GIGA_TOGGLE:
        weather = f"{get_weather()} \n*{get_hokku()}*"
    else:
        weather = get_weather() or "Ошибка при получении погоды."
    birthday = get_birthdays_db() or ""
    return f"*Всем привет!👋*\n" f"{weather}\n" f"{birthday}\n"


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
        # get_today_holidays("https://my-calend.ru/holidays")
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
