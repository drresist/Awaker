from langchain.prompts import load_prompt
from langchain.chat_models.gigachat import GigaChat
import os
from loguru import logger


def get_hokku() -> str:
    """
    Retrieves a humorous haiku about IT from the GigaChat service.

    Returns:
        str: The retrieved haiku.

    Raises:
        Exception: If an error occurs during GigaChat interaction.
    """
    try:
        chat = GigaChat(
            credentials=os.getenv('GIGA_AUTH_DATA'),
            verify_ssl_certs=False,
            scope="GIGACHAT_API_PERS",
            model="GigaChat:latest"
        )
        prompt = load_prompt("../prompts/content/text_rewrite.yaml")
        chat_chain = prompt | chat
        input_data = {
            "text": "смешное хокку про IT",
            "style": "шуточное хокку"
        }
        content = chat_chain.invoke(input_data).content
        logger.info(content)
        return content
    except Exception as e:
        logger.error(f"An error occurred during GigaChat interaction: {e}")
        return "Error during GigaChat interaction. Please check logs for details."
