import requests
from datetime import datetime
import time

from src.utils import config_logger


log = config_logger()

def get_weather_emoji(description):
    """Return an appropriate emoji for the weather description."""
    description = description.lower()
    if "ясно" in description:
        return "☀️"
    elif "облачно" in description:
        return "☁️"
    elif "дождь" in description:
        return "🌧️"
    elif "снег" in description:
        return "❄️"
    elif "гроза" in description:
        return "⛈️"
    else:
        return "🌤️"

def fetch_weather_data(city):
    """Fetch weather data from wttr.in."""
    url = f"http://wttr.in/{city}?format=j1&lang=ru"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def process_weather_data(data, city):
    """Process the weather data and create a formatted message in Russian."""
    today = datetime.now().date()
    current = data['current_condition'][0]
    forecasts = data['weather'][0]['hourly']

    message = f"🌍 Погода в {city} - {today.strftime('%d %B %Y')}\n\n"

    # Current weather
    current_temp = f"{current['temp_C']}°C"
    current_desc = current['lang_ru'][0]['value']
    current_emoji = get_weather_emoji(current_desc)
    # message += f"Сейчас:\n {current_emoji} {current_desc}\n 🌡️ Температура: {current_temp}\n\n"

    # Forecast for the day
    for period, hour in [("Утро", "9"), ("День", "15"), ("Вечер", "21")]:
        for forecast in forecasts:
            if forecast['time'] == hour + "00":
                temp = f"{forecast['tempC']}°C"
                desc = forecast['lang_ru'][0]['value']
                emoji = get_weather_emoji(desc)
                message += f"{period}: {emoji} {desc} 🌡️ Температура: {temp}\n"
                break

    return message.strip()

def get_today_weather(city, max_retries=3, retry_delay=5):
    """Retrieve weather forecast with retry logic."""
    for attempt in range(max_retries):
        try:
            data = fetch_weather_data(city)
            return process_weather_data(data, city)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"Попытка {attempt + 1} не удалась. Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
            else:
                return f"❌ Ошибка получения данных о погоде после {max_retries} попыток: {e}"
        except (KeyError, IndexError) as e:
            return f"❌ Ошибка обработки данных о погоде: {e}"
