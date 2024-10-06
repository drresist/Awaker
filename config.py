import os
from dotenv import load_dotenv


load_dotenv()

OW_API = os.getenv("OW_API")
TG_BOT_API = os.getenv("TG_BOT_API", "None")
CHAT_ID = os.getenv("CHAT_ID", "None")
PG_HOST = os.getenv("PG_HOST")
PG_DB = os.getenv("PG_DB")
PG_USER = os.getenv("PG_USER")
PG_PASS = os.getenv("PG_PASS")
