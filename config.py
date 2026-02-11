import os
from dotenv import load_dotenv

load_dotenv()

# Strategy Thresholds (in milliseconds)
LATENCY_THRESHOLD_FAST = 300  # Below this = Deep Reasoning allowed
LATENCY_THRESHOLD_POOR = 1000 # Above this = Panic Mode (Fastest possible)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = "AIzaSyBGtEpc4YyD2dLob2_fMEZ0l1VdCGzexy8"
MISTRAL_API_KEY = "hdl7dvGQzeEhwH4wgf8Vkj8ASAQzMS7I"