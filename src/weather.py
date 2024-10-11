import requests
from datetime import datetime
import time
import locale

from src.utils import config_logger

log = config_logger()


def fetch_weather_data(city):
    """Fetch weather data from wttr.in API."""
    url = f"https://wttr.in/{city}?format=%c+%C+%t&lang=ru"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.text.strip()


def process_weather_data(data, city):
    """Process the weather data and create a simplified formatted message in Russian."""
    weather_info = data.split(" ")
    current_emoji = weather_info[0]
    current_desc = " ".join(weather_info[1:-1])
    current_temp = weather_info[-1]

    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    message = f"🌍 Погода в {city} - {datetime.now().strftime('%d %B %Y')}\n"
    message += f"{current_emoji} {current_desc.capitalize()}\n"
    message += f"🌡️ Температура: {current_temp}"

    return message.strip()


def get_today_weather(city, max_retries=3, retry_delay=5):
    """Retrieve current weather with retry logic."""
    for attempt in range(max_retries):
        try:
            data = fetch_weather_data(city)
            return process_weather_data(data, city)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(
                    f"Попытка {attempt + 1} не удалась. Повторная попытка через {retry_delay} секунд..."
                )
                time.sleep(retry_delay)
            else:
                return f"❌ Ошибка получения данных о погоде после {max_retries} попыток: {e}"
        except (IndexError, ValueError) as e:
            return f"❌ Ошибка обработки данных о погоде: {e}"
