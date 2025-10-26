from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os
import sys

scripts_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(scripts_path, '..')
sys.path.insert(0, project_root)
from config.provider import TelegramConfig

load_dotenv()

channel_id = input('Please enter channel ID: ')


def main():
    telegram_config = TelegramConfig()
    with TelegramClient(
        telegram_config.telegram_api_session_name,
        telegram_config.telegram_api_id,
        telegram_config.telegram_api_hash
    ) as client:
        participants = client.get_participants(int(channel_id))
        details = [{"username": o.username, "id": o.id} for o in participants]
        for d in details:
            print(d)


if __name__ == "__main__":
    main()
