import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    # API Configuration
    API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    API_URL = os.getenv('LLM_URL', 'https://openrouter.ai/api/v1/chat/completions')
    MODEL = 'minimax/minimax-m2:free'  # Free model from OpenRouter
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    
    # Embedding Configuration
    EMBED_DIM = int(os.getenv('EMBED_DIM', 1536))
    
    # App Configuration
    APP_NAME = 'StudyMate - Academic Assistant'
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Storage Configuration
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'memory')  # 'memory' or 'file'
    STORAGE_FILE = os.getenv('STORAGE_FILE', 'data/storage.json')

