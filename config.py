import os
# from envparse import env
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()


ADMIN_ID = os.environ.get('ADMIN_ID')
TOKEN = os.environ.get('BOT_TOKEN')

DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('POSTGRES_HOST')
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
