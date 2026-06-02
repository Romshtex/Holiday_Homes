from dotenv import load_dotenv
import os

load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
