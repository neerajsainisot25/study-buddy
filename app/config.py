import os

class Config:
    """Application configuration"""
    # API Configuration
    API_KEY = os.getenv('OPENROUTER_API_KEY', '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')
    API_URL = 'https://openrouter.ai/api/v1/chat/completions'
    MODEL = 'openai/gpt-3.5-turbo'
    
    # App Configuration
    APP_NAME = 'Unified AI App'
    APP_URL = os.getenv('APP_URL', 'http://localhost:5001')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))  # Changed from 5000 to avoid macOS AirPlay conflict
    
    # Storage Configuration
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'memory')  # 'memory' or 'file'
    STORAGE_FILE = os.getenv('STORAGE_FILE', 'data/storage.json')

