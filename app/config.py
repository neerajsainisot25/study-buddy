import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    # API Configuration
    API_KEY = os.getenv('OPENROUTER_API_KEY', '')
    API_URL = os.getenv('LLM_URL', 'https://openrouter.ai/api/v1/chat/completions')
    MODEL = 'minimax/minimax-m2:free'
    
    # Embedding Configuration
    EMBED_DIM = int(os.getenv('EMBED_DIM', 1536))
    
    # App Configuration
    APP_NAME = 'StudyMate - Academic Assistant'
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Storage Configuration
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'memory')
    STORAGE_FILE = os.getenv('STORAGE_FILE', 'data/storage.json')
    
    # Supabase Database Configuration
    SUPABASE_PASSWORD = os.getenv('SUPABASE_PASSWORD', '')
    DATABASE_URL = f"postgresql://postgres.wjtyfgibnylvlgeusrxf:{SUPABASE_PASSWORD}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?pgbouncer=true"
    DIRECT_URL = f"postgresql://postgres.wjtyfgibnylvlgeusrxf:{SUPABASE_PASSWORD}@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"
