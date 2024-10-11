import argparse
import time
from datetime import datetime, timedelta, timezone

import psycopg2
import requests
import telebot
from loguru import logger
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import config

from src.weather import get_today_weather

# Инициализация конфигурации и логгера
logger.add("logs/debug.log", level="DEBUG")

def log_error_and_continue(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Произошла ошибка: {e}")
            return None
    return wrapper

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Я проснулся!", callback_data="cb_awake"))
    return markup


@log_error_and_continue
def get_birthdays_db() :
    with psycopg2.connect(
        host=config.PG_HOST,
        database=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASS,
    ) as conn:
        with conn.cursor() as cursor:
            today_date = datetime.now().strftime("%d-%m")
            cursor.execute("SELECT name FROM birthdays WHERE date = %s", (today_date,))
            birthdays = cursor.fetchall()

    if not birthdays:
        return None
    birthday_list = [birthday[0] for birthday in birthdays]
    logger.info(f"Найдено {len(birthday_list)} дней рождения")
    return "День рождения у 🎂: \n" + "\n".join(birthday_list)

@log_error_and_continue
def create_message() -> str:
    weather = get_today_weather("Москва") or "Ошибка при получении погоды."
    birthday = get_birthdays_db() or ""
    return f"*Всем привет!👋*\n{weather}\n{birthday}\n"

def send_message(text: str) -> None:
    bot = telebot.TeleBot(token=config.TG_BOT_API)
    logger.info(f"Отправка сообщения: {text}")
    button = gen_markup()
    bot.send_message(
        text=text,
        chat_id=config.CHAT_ID,
        disable_notification=True,
        parse_mode="markdown",
        reply_markup=button
    )

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Бот погоды и дней рождения")
    parser.add_argument("--test", action="store_true", help="Включить режим тестирования")
    return parser.parse_args()

def test_app(args):
    try:
        send_message(create_message())
        logger.info("Тестовое сообщение успешно отправлено.")
    except Exception as e:
        logger.error(f"Произошла ошибка во время тестирования: {e}")

def main_loop():
    while True:
        current_time_utc3 = datetime.now(timezone.utc) + timedelta(hours=3)
        if current_time_utc3.hour == 8 and current_time_utc3.minute == 0:
            try:
                send_message(create_message())
            except Exception as e:
                logger.error(f"Произошла ошибка: {e}")
        time.sleep(60)

def main():
    args = parse_arguments()
    if args.test:
        test_app(args)
    else:
        main_loop()

if __name__ == "__main__":
    main()
