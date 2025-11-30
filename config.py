import os, time, pytz
from pathlib import Path

def set_timezone():
    os.environ['TZ'] = 'Europe/Moscow'  # Замените на ваш часовой пояс
    time.tzset()

# Try to load variables from a .env file if python-dotenv is installed.
# This import is optional: if python-dotenv is not available we still
# read environment variables via os.getenv with sensible defaults.
env_path = Path(__file__).parent / '.env'
try:
	from dotenv import load_dotenv
	if env_path.exists():
		load_dotenv(env_path)
except Exception:
	# dotenv not installed or failed to load — continue using os.environ
	pass

# Application settings (read from env with defaults)
TOKEN = os.getenv('TOKEN')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')
DEFAULT_DB_URL = os.getenv('DEFAULT_DB_URL')
TARGET_DB_URL = os.getenv('TARGET_DB_URL')

# If TARGET_DB_URL is not provided, try to build it from postgres env vars
if not TARGET_DB_URL:
	pg_user = os.getenv('POSTGRES_USER') or os.getenv('POSTGRES_USER', 'postgres')
	pg_password = os.getenv('POSTGRES_PASSWORD') or os.getenv('POSTGRES_PASSWORD', 'postgres')
	pg_host = os.getenv('POSTGRES_HOST', '127.0.0.1')
	pg_port = os.getenv('POSTGRES_PORT', '5432')
	pg_db = os.getenv('POSTGRES_DB', 'kislorod')
	TARGET_DB_URL = f"postgresql+asyncpg://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
REGISTER_CODE = os.getenv('REGISTER_CODE')