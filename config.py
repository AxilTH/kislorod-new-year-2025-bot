import os, time, pytz
from pathlib import Path

def set_timezone():
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()

env_path = Path(__file__).parent / '.env'
try:
	from dotenv import load_dotenv
	if env_path.exists():
		load_dotenv(env_path)
except Exception:
	pass

TOKEN = os.getenv('TOKEN')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')
DEFAULT_DB_URL = os.getenv('DEFAULT_DB_URL')
TARGET_DB_URL = os.getenv('TARGET_DB_URL')

if not TARGET_DB_URL:
	pg_user = os.getenv('POSTGRES_USER')
	pg_password = os.getenv('POSTGRES_PASSWORD')
	pg_host = os.getenv('POSTGRES_HOST')
	pg_port = os.getenv('POSTGRES_PORT')
	pg_db = os.getenv('POSTGRES_DB')
	TARGET_DB_URL = f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
REGISTER_CODE = os.getenv('REGISTER_CODE')