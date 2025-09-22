from enum import Enum


class TrolleyProblemDecision(Enum):
    Pull_lever = "Pull the lever"
    Do_nothing = "Do nothing"


MODELS = [
    "moonshotai/kimi-vl-a3b-thinking:free",
    "openrouter/sonoma-dusk-alpha",
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "openrouter/sonoma-sky-alpha",
]

URL = "https://neal.fun/absurd-trolley-problems/"
