import os
from dotenv import load_dotenv

load_dotenv()

# Strategy Thresholds (in milliseconds)
LATENCY_THRESHOLD_FAST = 300  # Below this = Deep Reasoning allowed
LATENCY_THRESHOLD_POOR = 1000 # Above this = Panic Mode (Fastest possible)

MISTRAL_API_KEY = "your_mistral_api_key_here"