import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-for-placifly-dev')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
