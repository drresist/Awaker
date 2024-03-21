from langchain.prompts import load_prompt
from langchain.chat_models.gigachat import GigaChat
import os
from loguru import logger


def get_hokku() -> str:
    try:
        GIGA_CLIENT = os.getenv('GIGA_AUTH_DATA')

        # Authenticate with the GigaChat service
        chat = GigaChat(
            credentials=GIGA_CLIENT,
            verify_ssl_certs=False,
            scope="GIGACHAT_API_PERS",
            model="GigaChat:latest"
        )



        # Load the prompt for text rewriting
        prompt = load_prompt("prompts/content/text_rewrite.yaml")

        # Compose the chat chain
        chat_chain = prompt | chat

        # Define the input data
        input_data = {
            "text": "смешное хокку про IT",
            "style": "шуточное хокку"
        }

        # Invoke the chain to get the rewritten content
        content = chat_chain.invoke(input_data).content

        logger.info(content)
        return content

    except Exception as e:
        logger.error(f"An error occurred during GigaChat interaction: {e}")
        # Handle the error appropriately, e.g., return a default value or re-raise the exception.
        return "Error during GigaChat interaction. Please check logs for details."
