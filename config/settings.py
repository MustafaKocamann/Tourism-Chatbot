import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY", "")
CURRENCYAPI_KEY = os.getenv("CURRENCYAPI_KEY", "")

# LLM Settings
LLM_MODEL = "llama3.2:3b"
LLM_TEMPERATURE = 0.7

# Database
DATABASE_PATH = "data/users.db"

# PDF Settings
PDF_OUTPUT_DIR = "outputs"

# Session Settings
SESSION_TIMEOUT = 3600  # 1 hour

# Cache Settings
CACHE_EXPIRY = 1800  # 30 minutes