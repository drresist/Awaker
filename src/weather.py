import json
from utils import log_error_and_continue, initialize_config
from loguru import logger
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from io import BytesIO

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
    Генерирует изображение на основе информации о погоде с графиками и крупным текстом.
    """
    width, height = 1000, 800
    background_color = (240, 248, 255)  # Светло-голубой фон
    text_color = (0, 0, 0)  # Черный цвет текста
    
    image = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    # Загрузка шрифтов
    try:
        title_font = ImageFont.truetype("Symbola.ttf", 48)
        weather_font = ImageFont.truetype("Symbola.ttf", 36)
    except IOError:
        logger.warning("Шрифт Arial не найден. Используется шрифт по умолчанию.")
        title_font = ImageFont.load_default()
        weather_font = ImageFont.load_default()
    
    # Добавление заголовка
    title = "Прогноз погоды на сегодня"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) / 2, 20), title, font=title_font, fill=text_color)
    
    # Разделение информации о погоде на строки
    weather_lines = weather_info.split("\n")
    
    # Извлечение данных для графиков
    times = []
    temperatures = []
    humidity = []
    
    for line in weather_lines:
        parts = line.split(", ")
        times.append(parts[0].split(":")[0])
        temperatures.append(float(parts[1].split(":")[1].replace("°C", "")))
        humidity.append(int(parts[2].split(":")[1].replace("%", "")))
    
    # Создание графиков
    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    
    ax1.plot(times, temperatures, marker='o', color='red')
    ax1.set_title("Температура")
    ax1.set_ylabel("°C")
    
    ax2.plot(times, humidity, marker='o', color='blue')
    ax2.set_title("Влажность")
    ax2.set_ylabel("%")
    
    plt.tight_layout()
    
    # Сохранение графиков в буфер
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_image = Image.open(buf)
    
    # Вставка графиков в основное изображение
    image.paste(chart_image, (width - chart_image.width - 20, 100))
    
    # Отрисовка информации о погоде
    y_position = 100
    for line in weather_lines:
        text_bbox = draw.textbbox((0, 0), line, font=weather_font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((20, y_position), line, font=weather_font, fill=text_color)
        y_position += 60
    
    # Добавление декоративных элементов
    draw.rectangle([10, 10, width - 10, height - 10], outline=(100, 149, 237), width=3)
    
    # Сохранение изображения
    image.save("weather.png")
    logger.info("Сгенерировано изображение погоды с графиками")