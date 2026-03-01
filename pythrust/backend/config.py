import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = "mixtral-8x7b-32768"

MAX_RETRIES = 2
TEMPERATURE = 0.2
MAX_PROMPT_LENGTH = 2000