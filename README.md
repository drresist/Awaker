# Awaker bot

[![Python application](https://github.com/drresist/Awaker/actions/workflows/python-app.yml/badge.svg)](https://github.com/drresist/Awaker/actions/workflows/python-app.yml)

Welcome to the Telegram Weather and Birthday Bot project! This Python script is designed to retrieve weather information for Moscow from the OpenWeatherMap API and notify users about birthdays from a CSV file.

The bot will send a formatted message containing weather data and any upcoming birthdays to a specified chat using Telegram's Bot API.
Prerequisites

Before running the bot, make sure you have the following:

    Python (>= 3.6)
    OpenWeatherMap API Key: Obtain an API key from OpenWeatherMap to access weather data.
    Telegram Bot API Key: Create a Telegram bot and get the API token from BotFather.
    Chat ID: Identify the chat ID where the bot will send messages. This can be your private chat ID or a group chat ID.

## Installation

Clone this repository to your local machine.

    git clone https://github.com/your-username/telegram-weather-bot.git
Change into the project directory.

    cd telegram-weather-bot

Install the required Python dependencies using pip.

    pip install -r requirements.txt

Create a .env file in the project root and add your API keys and chat ID.

    OW_API=YOUR_OPENWEATHERMAP_API_KEY
    TG_BOT_API=YOUR_TELEGRAM_BOT_API_KEY
    CHAT_ID=YOUR_CHAT_ID

## Usage

To run the Telegram Weather and Birthday Bot, execute the main() function in the bot.py script.

    python bot.py

The bot will start running and will send periodic messages to the specified chat with weather information and upcoming birthdays for the day.
