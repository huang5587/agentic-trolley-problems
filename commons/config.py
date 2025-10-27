import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_BASE_URL = "https://openrouter.ai/api/v1"
MODELS = [
    "google/gemini-2.5-flash",
    "openai/gpt-5-mini",
    "anthropic/claude-sonnet-4.5",
]


# ASSISTED_MODEL = "openai/gpt-5"
ASSISTED_MODEL = "google/gemini-2.5-flash"

UNASSISTED_MODEL = "google/gemini-2.5-pro"
GAME_URL = "https://neal.fun/absurd-trolley-problems/"
