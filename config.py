import os
from pathlib import Path

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
REGISTER_CODE = os.getenv('REGISTER_CODE')