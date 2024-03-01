# Weather and Birthday Bot

## Overview

The Weather and Birthday Bot is a Telegram bot designed to provide daily weather updates and birthday reminders. It fetches weather information using the OpenWeatherMap API and birthday data from a PostgreSQL database.

## Features

- **Weather Updates:** Receive daily weather updates for Moscow, including temperature, feels-like temperature, weather description, and humidity.

- **Birthday Reminders:** Get notifications for birthdays stored in a PostgreSQL database.

- **Telegram Integration:** Messages are sent to a specified Telegram channel at a scheduled time.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Makefile Commands](#makefile-commands)

## Prerequisites

Before running the bot, ensure you have the following:

- OpenWeatherMap API key
- Telegram Bot API key and Chat ID
- PostgreSQL database with a 'birthdays' table

## Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/weather-birthday-bot.git
   ```

2. **Install Dependencies:**

    ```bash
    cd weather-birthday-bot
    pip install -r requirements.txt
    ```
3. **Set up Environment Variables:**

    ```plaintext
    OW_API=your_openweathermap_api_key
    TG_BOT_API=your_telegram_bot_api_key
    CHAT_ID=your_telegram_chat_id
    PG_HOST=your_postgresql_host
    PG_DB=your_postgresql_database
    PG_USER=your_postgresql_user
    PG_PASS=your_postgresql_password
    ```
4. **Run bot:**
    ```bash
    python3 main.py
    ```

## Configuration

* OW_API: OpenWeatherMap API key.
* TG_BOT_API: Telegram Bot API key.
* CHAT_ID: Telegram Chat ID.
* PG_HOST, PG_DB, PG_USER, PG_PASS: PostgreSQL database connection details.
* GIGA_AUTH_DATA: auth data for working with GigaChat SDK

## Usage

The bot is configured to send messages at 8:00 AM daily. Adjust the main function in bot.py if you want to change the schedule.

## Makefile Commands

The project includes a Makefile to simplify common tasks:
```bash
# Initialize Virtual Environment:
make init-venv

# Install Requirements:
make install-requirements

# Run the Bot:
make run

# Clean Virtual Environment:
make clean-venv
```