"""Routes module - imports all blueprints"""
from app.routes.chat import chat_bp
from app.routes.quiz import quiz_bp
from app.routes.calendar import calendar_bp
from app.routes.rag import rag_bp
from app.routes.analytics import analytics_bp

__all__ = ['chat_bp', 'quiz_bp', 'calendar_bp', 'rag_bp', 'analytics_bp']

