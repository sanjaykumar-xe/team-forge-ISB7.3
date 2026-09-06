import os
import json
from dotenv import load_dotenv
from tavily import TavilyClient

# Ensure .env is loaded from backend or root directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
api_key = os.environ.get("TAVILY_API_KEY", "")

print(f"Loaded TAVILY_API_KEY: {api_key[:12]}...{api_key[-4:] if len(api_key) > 16 else ''}")

client = TavilyClient(api_key=api_key)
response = client.search(
    query="eco friendly zero waste cleaning subscription box",
    max_results=2
)

print("\n--- RAW TAVILY RESPONSE ---")
print(json.dumps(response, indent=2))
