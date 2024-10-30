import datetime
import sqlite3
import logging
import config
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import pytz
from weather import get_today_weather

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def get_birthdays_db():
    with sqlite3.connect("birthday.db") as conn:
        cursor = conn.cursor()
        today_date = datetime.datetime.now().strftime("%d-%m")
        cursor.execute("SELECT name FROM birthdays WHERE date = ?", (today_date,))
        birthdays = cursor.fetchall()

    if not birthdays:
        return None
    birthday_list = [birthday[0] for birthday in birthdays]
    logging.info(f"Найдено {len(birthday_list)} дней рождения")
    return "День рождения у 🎂: \n" + "\n".join(birthday_list)


def create_message() -> str:
    weather = get_today_weather("Москва") or "Ошибка при получении погоды."
    birthday = get_birthdays_db() or ""
    return f"*Всем привет!👋*\n{weather}\n{birthday}\n"


async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a periodic message."""
    message = create_message()
    logging.info("send periodic message")
    await context.bot.send_message(
        chat_id=config.CHAT_ID,
        text=message,
        disable_notification=True,
        parse_mode="Markdown",
    )


async def test_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logging.info("calling test message")
    await update.message.reply_text(text=create_message(), parse_mode="Markdown")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(config.TG_BOT_API).build()

    job_queue = application.job_queue
    job_daily = job_queue.run_daily(
        send_periodic_message,
        days=(0, 1, 2, 3, 4, 5, 6),
        time=datetime.time(hour=19, minute=31, tzinfo=pytz.timezone("Europe/Moscow")),
    )
    application.add_handler(CommandHandler("test", test_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
