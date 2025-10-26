from telethon.sync import TelegramClient
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest
from dotenv import load_dotenv
import os
import sys

scripts_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(scripts_path, '..')
sys.path.insert(0, project_root)
from config.provider import TelegramConfig

load_dotenv()

phone_number = input('Please enter phone number: ')
name = input('Please enter name: ')

def main():
    telegram_config = TelegramConfig()
    with TelegramClient(
        telegram_config.telegram_api_session_name,
        telegram_config.telegram_api_id,
        telegram_config.telegram_api_hash
    ) as client:
        contact = InputPhoneContact(client_id=0, phone=phone_number, first_name=name, last_name='')
        result = client(ImportContactsRequest([contact]))
        print(result.users[0].username)


if __name__ == "__main__":
    main()
