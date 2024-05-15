import os
from dotenv import load_dotenv
from loguru import logger


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
        GIGA_TOGGLE (bool): Toggle for Gigachain functionality. Defaults to False.
        JOKE_TOGGLE (bool): Toggle for joke functionality. Defaults to False.
        HOLIDAYS_TOGGLE (bool): Toggle for holidays functionality. Defaults to False.
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
        self.GIGA_TOGGLE = False
        self.JOKE_TOGGLE = False
        self.HOLIDAYS_TOGGLE = False
        self.HOLIDAYS_URL = 'https://my-calend.ru/holidays'


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
