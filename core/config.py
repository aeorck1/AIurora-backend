import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Aura Wellness API"
    VERSION: str = "1.0.0"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # Safety
    CRISIS_HOTLINE_NG: str = "08092106493" # MANI (Mentally Aware Nigeria Initiative)

# Create a single instance to be imported anywhere in your app
settings = Settings()

# Fast fail: If the API key is missing, crash the app immediately on startup
if not settings.GEMINI_API_KEY:
    raise ValueError("🚨 GEMINI_API_KEY is missing! Check your .env file.")