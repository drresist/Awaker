"""Пример работы с чатом через gigachain"""
from datetime import date
from langchain.prompts import load_prompt
from langchain.chat_models.gigachat import GigaChat
import os
from loguru import logger

logger.info(os.getenv('GIGA_AUTH_DATA'))

def get_weather_description(weather : str):
    GIGA_CLIENT = os.getenv('GIGA_AUTH_DATA')
    # Авторизация в сервисе GigaChat
    chat = GigaChat(credentials=GIGA_CLIENT, 
                    verify_ssl_certs=False, 
                    scope="GIGACHAT_API_PERS",
                    model="GigaChat:latest")


    prompt = load_prompt("prompts/content/text_rewrite.yaml")
    chain = prompt | chat
    content = chain.invoke(
        {
            "text": f"Сегодня {date.today()}, Погода в Москве {weather}",
            "style": "Письмо коллегам"
        }
    ).content
    logger.info(content)
    return content