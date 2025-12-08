"""
Configuration module for loading environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# TextBee SMS Configuration
TEXTBEE_API_KEY = os.getenv("TEXTBEE_API_KEY", "")
TEXTBEE_DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID", "")

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Parse multiple chat IDs if provided
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", TELEGRAM_CHAT_ID).split(",") if os.getenv("TELEGRAM_CHAT_IDS") or TELEGRAM_CHAT_ID else []
TELEGRAM_CHAT_IDS = [cid.strip() for cid in TELEGRAM_CHAT_IDS if cid.strip()]

def get_config():
    """Return configuration dictionary"""
    return {
        "textbee_api_key": TEXTBEE_API_KEY,
        "textbee_device_id": TEXTBEE_DEVICE_ID,
        "telegram_bot_token": TELEGRAM_BOT_TOKEN,
        "telegram_chat_ids": TELEGRAM_CHAT_IDS
    }
