import json
from utils import log_error_and_continue, initialize_config
from loguru import logger
import requests
from PIL import Image, ImageDraw, ImageFont

# Assuming initialize_config and icons.json loading happens outside the function
config = initialize_config()
with open("icons.json", "r", encoding="utf-8") as f:
    icons_mapping = json.load(f)

def get_weather() -> str | None:
    url = f"http://api.openweathermap.org/data/2.5/forecast?q=Moscow&appid={config.OW_API}&lang=ru&units=metric"
    logger.info("Requesting weather data from OW")

    weather_response = requests.get(url)
    logger.info(f"Weather data received with status code: {weather_response.status_code}")

    if weather_response.status_code != 200:
        return None
    weather_data = weather_response.json()
    return format_weather_data(weather_data, icons_mapping)

def format_weather_data(weather_data: dict, icons_mapping: dict) -> str:
    # Фильтрация данных для утреннего, дневного и вечернего времени
    morning_data = next(item for item in weather_data['list'] if '09:00:00' in item['dt_txt'])
    day_data = next(item for item in weather_data['list'] if '12:00:00' in item['dt_txt'])
    evening_data = next(item for item in weather_data['list'] if '18:00:00' in item['dt_txt'])

    # Форматирование данных
    morning_weather = format_single_weather(morning_data, icons_mapping, "Утро")
    day_weather = format_single_weather(day_data, icons_mapping, "День")
    evening_weather = format_single_weather(evening_data, icons_mapping, "Вечер")

    return f"{morning_weather}\n{day_weather}\n{evening_weather}"

def format_single_weather(weather_data: dict, icons_mapping: dict, time_of_day: str) -> str:
    description = weather_data["weather"][0]["description"]
    icon_code = weather_data["weather"][0]["icon"]
    temperature = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    weather_icon = icons_mapping.get(icon_code, "?")
    return f"{time_of_day}: {weather_icon} {description}, 🌡:{temperature:.2f}°C, 💦: {humidity}%"

def generate_image(weather_info: str):
    """
    Generate image based on formatted weather information.
    """
    width, height = 600, 400
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("Symbola.ttf", 18)

    weather_lines = weather_info.split("\n")
    for weather_line in weather_lines:
        draw.text((10, 10 + (weather_lines.index(weather_line) * 20)), weather_line, font=font, fill="black")

    image.save("weather.png")
    logger.info("Generated weather image")
