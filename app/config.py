import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gold_purchases.db")
APP_NAME = "Simplify Money Gold AI"

# fallback price if live fetch fails (per gram, 24K, INR)
FALLBACK_GOLD_PRICE = 15200.0
