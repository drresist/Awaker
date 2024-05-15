import json
from utils import log_error_and_continue, initialize_config
from loguru import logger
import requests
from PIL import Image,  ImageDraw, ImageFont


# Assuming initialize_config and icons.json loading happens outside the function
config = initialize_config()
with open("icons.json", "r", encoding="utf-8") as f:
    icons_mapping = json.load(f)


@log_error_and_continue
def get_weather() -> str | None:
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={config.OW_API}&lang=ru&units=metric"
    logger.info("Requesting weather data from OW")

    with requests.get(url) as weather_response:
        logger.info(f"Weather data received with status code: {weather_response.status_code}")

        if weather_response.status_code != 200:
            return None
        weather_data = weather_response.json()
        return format_weather_data(weather_data, icons_mapping)


def format_weather_data(weather_data: dict, icons_mapping: dict) -> str:
    description = weather_data["weather"][0]["description"]
    icon_code = weather_data["weather"][0]["icon"]
    temperature = weather_data["main"]["temp"]
    feels_like = weather_data["main"]["feels_like"]
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]
    pressure = weather_data["main"]["pressure"] * 0.75  # Convert pressure to mmHg
    weather_icon = icons_mapping.get(icon_code, "?")

    return f"""
Сейчас в городе {weather_data['name']}:

{weather_icon} {description}

🌡️ Температура воздуха — {temperature:.2f}°C
👀 Чувствуется как — {feels_like:.1f}°C
💦 Влажность — {humidity}%
💨 Ветер — {wind_speed} м/с
📍 Атмосферное давление — {pressure:.0f} мм рт.ст.
    """


def generate_image(weather_info: str):
    """
    Generate image based on formatted weather information.
    """
    width, height = 600, 400
    image = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype("Symbola.ttf", 18)
    font_size = 16

    weather_lines = weather_info.split("\n")
    for weather_line in weather_lines:
        draw.text((10, 10 + (weather_lines.index(weather_line) * 20)), weather_line, font=font, fill="black")

    image.save("weather.png")
    logger.info("Generated weather image")
