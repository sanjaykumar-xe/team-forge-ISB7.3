import os
from dotenv import load_dotenv

load_dotenv()

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# No API key needed for search — the Web Search Agent uses the free,
# keyless `ddgs` (DuckDuckGo) library. If the team switches to a paid
# provider later (Tavily, Serper, Brave, etc.), add its key loading here.
