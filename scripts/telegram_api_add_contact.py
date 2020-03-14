from telethon import TelegramClient, sync
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

telegram_config = TelegramConfig()
telegram_client = TelegramClient(telegram_config.telegram_api_session_name, telegram_config.telegram_api_id, telegram_config.telegram_api_hash).start()

contact = InputPhoneContact(client_id = 0, phone = phone_number, first_name=name, last_name='')
result = telegram_client(ImportContactsRequest([contact]))
print(result.users[0].username)
