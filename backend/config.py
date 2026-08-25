import os
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

# CORS configuration: Allow specific origins or fallback to wildcard
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if raw_origins == "*":
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

# Server configuration
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

