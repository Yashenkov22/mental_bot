import os

from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()


ADMIN_IDS = set(map(int, os.environ.get('ADMIN_ID').split()))
TOKEN = os.environ.get('BOT_TOKEN')
SECRET_WORD = os.environ.get('SECRET_WORD')

NGROK_PUBLIC_URL = os.environ.get('NGROK_PUBLIC_URL')

DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')


db_url = URL.create(
        'postgresql+asyncpg',
        username=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
