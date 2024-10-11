import requests
from datetime import datetime
import time
import os
import locale

from src.utils import config_logger

log = config_logger()

# Step 1: Update imports and add OpenWeather API key
OPENWEATHER_API_KEY = os.environ.get('OW_API')
if not OPENWEATHER_API_KEY:
    raise ValueError("OpenWeather API key not found in environment variables")

def get_weather_emoji(description):
    """Return an appropriate emoji for the weather description."""
    description = description.lower()
    if "clear" in description:
        return "☀️"
    elif "cloud" in description:
        return "☁️"
    elif "rain" in description:
        return "🌧️"
    elif "snow" in description:
        return "❄️"
    elif "thunderstorm" in description:
        return "⛈️"
    else:
        return "🌤️"

def fetch_weather_data(city):
    """Fetch weather data from OpenWeather API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def process_weather_data(data, city):
    """Process the weather data and create a simplified formatted message in Russian."""
    current_temp = round(data['main']['temp'])
    current_desc = data['weather'][0]['description']
    current_emoji = get_weather_emoji(data['weather'][0]['main'])

    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    message = f"🌍 Погода в {city} - {datetime.now().strftime('%d %B %Y')}\n"
    message += f"{current_emoji} {current_desc.capitalize()}\n"
    message += f"🌡️ Температура: {current_temp}°C"

    return message.strip()

def get_today_weather(city, max_retries=3, retry_delay=5):
    """Retrieve current weather with retry logic."""
    for attempt in range(max_retries):
        try:
            data = fetch_weather_data(city)
            return process_weather_data(data, city)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                log.warning(f"Попытка {attempt + 1} не удалась. Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
            else:
                return f"❌ Ошибка получения данных о погоде после {max_retries} попыток: {e}"
        except (KeyError, IndexError) as e:
            return f"❌ Ошибка обработки данных о погоде: {e}"
