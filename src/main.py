import argparse
import sys
import time
from datetime import datetime, timedelta, timezone

import psycopg2
import requests
import telebot
from loguru import logger

# from giga_srv import get_hokku
from holidays import get_holidays
from utils import initialize_config
from weather import get_weather, generate_image


config = initialize_config()

def initialize_logger():
    """
    Initializes the logger configuration.

    Adds log handlers for standard output with log level "INFO",
    standard error with log level "ERROR", and a file named "logs/debug.log"
    with log level "DEBUG".
    """
    # logger.add(sys.stdout, level="INFO")
    # logger.add(sys.stderr, level="ERROR")
    logger.add("logs/debug.log", level="DEBUG")


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


@log_error_and_continue
def get_joke() -> str | None:
    """
    Retrieves a random joke from the specified URL.

    Returns:
        str | None: The content of the joke if successful, otherwise None.
    """
    url = "https://jokesrv.fermyon.app/"
    logger.info("Requesting joke data")

    with requests.get(url) as joke_response:
        logger.info(f"Joke data received with status code: {joke_response.status_code}")

        if joke_response.status_code != 200:
            return None
        joke_data = joke_response.json()
        return joke_data["content"]


def create_message() -> str:
    """
    Creates a message containing weather, birthdays, and holidays information.

    Returns:
        str: The formatted message.
    """
    weather = get_weather() or "Ошибка при получении погоды."
    generate_image(weather)
    birthday = get_birthdays_db() if (birthdays := get_birthdays_db()) else ""
    holidays = get_holidays(config.HOLIDAYS_URL) if config.HOLIDAYS_TOGGLE and (
        holidays := get_holidays(config.HOLIDAYS_URL)) else ""

    additional_content = ""
    # if config.GIGA_TOGGLE:
    #     # additional_content = f"\n*{get_hokku()}*"
        
    if config.JOKE_TOGGLE:
        additional_content = f"\n*{get_joke()}*"

    return f"*Всем привет!👋*\n {weather}\n {birthday}\n {holidays}{additional_content}\n"


def send_message(text: str) -> None:
    """
    Sends a message using the Telegram Bot API.

    Args:
        text (str): The text of the message to send.

    Returns:
        None
    """
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
    parser.add_argument("--hokku", action="store_true", help="Enable hokku functionality")
    parser.add_argument("--joke", action="store_true", help="Enable joke functionality")
    parser.add_argument("--holidays", action="store_true", help="Enable holidays functionality")
    return parser.parse_args()


def test_app(args):
    """
    Tests the application by sending a test message.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Raises:
        Exception: If an error occurs during testing.
    """
    config.GIGA_TOGGLE = args.hokku
    config.JOKE_TOGGLE = args.joke
    config.HOLIDAYS_TOGGLE = args.holidays

    try:
        send_message(create_message())
        logger.info("Test message sent successfully.")
    except Exception as e:
        logger.error(f"An error occurred during testing: {e}")


def main_loop():
    while True:
        current_time_utc3 = datetime.now(timezone.utc) + timedelta(hours=3)
        if current_time_utc3.hour == 8 and current_time_utc3.minute == 0:
            try:
                send_message(create_message())
            except Exception as e:
                logger.error(f"An error occurred: {e}")

        time.sleep(60)


def main():
    config = initialize_config()
    initialize_logger()
    args = parser_arguments()

    if args.test:
        test_app(args)
    else:
        config.GIGA_TOGGLE = args.hokku
        config.JOKE_TOGGLE = args.joke
        config.HOLIDAYS_TOGGLE = args.holidays
        main_loop()


if __name__ == "__main__":
    main()
