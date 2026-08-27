from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os


# ---------------------------------------
# Load environment variables
# ---------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(
    ROOT_DIR / ".env"
)


# ---------------------------------------
# Gemini LLM
# ---------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)