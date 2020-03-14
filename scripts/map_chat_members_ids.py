from telethon import TelegramClient, sync
from dotenv import load_dotenv
import os
import sys

scripts_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(scripts_path, '..')
sys.path.insert(0, project_root)
from config.provider import TelegramConfig

load_dotenv()

channel_id = input('Please enter channel ID: ')

telegram_config = TelegramConfig()
telegram_client = TelegramClient(telegram_config.telegram_api_session_name, telegram_config.telegram_api_id, telegram_config.telegram_api_hash).start()

participants = telegram_client.get_participants(int(channel_id))
details = [{"username": o.username, "id": o.id } for o in participants]
for d in details:
  print(d)
