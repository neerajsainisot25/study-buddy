"""Database service using SQLAlchemy with PostgreSQL"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), default='Student')
    email = Column(String(255))
    grade = Column(String(50))
    bio = Column(Text)
    weekly_goal = Column(Integer, default=20)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Quiz(Base):
    __tablename__ = 'quizzes'
    
    id = Column(Integer, primary_key=True)
    quiz_id = Column(String(255), unique=True, nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    topic = Column(String(500), nullable=False)
    num_questions = Column(Integer, nullable=False)
    quiz_type = Column(String(50), default='multiple_choice')
    difficulty = Column(String(50), default='intermediate')
    source_material = Column(String(50), default='general')
    questions = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class QuizAttempt(Base):
    __tablename__ = 'quiz_attempts'
    
    id = Column(Integer, primary_key=True)
    quiz_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    score = Column(Float, nullable=False)
    correct = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    time_taken = Column(Integer)
    topic = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    date = Column(String(50), nullable=False, index=True)
    time = Column(String(50))
    type = Column(String(50))
    priority = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalyticsData(Base):
    __tablename__ = 'analytics_data'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseService:
    """Database service for PostgreSQL operations"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database connection"""
        try:
            # Use Supabase connection URL with proper pooler configuration
            supabase_password = os.getenv('SUPABASE_PASSWORD')
            
            if not supabase_password:
                logger.warning("SUPABASE_PASSWORD not found, database features will be disabled")
                return
            
            # Use pooler connection for production with pgbouncer
            database_url = f"postgresql://postgres.wjtyfgibnylvlgeusrxf:{supabase_password}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"
            
            # Set pool configuration for better connection management
            self.engine = create_engine(
                database_url, 
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                echo=False
            )
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            
            # Don't create_all on Supabase - tables are managed by Prisma
            # Just verify connection
            from sqlalchemy import text
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Connected to Supabase database successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Supabase database: {e}")
            self.engine = None
            self.Session = None
    
    def is_available(self):
        """Check if database is available"""
        return self.engine is not None and self.Session is not None
    
    def get_session(self):
        """Get database session"""
        if not self.is_available():
            raise Exception("Database not available")
        return self.Session()
    
    def close_session(self, session):
        """Close database session"""
        try:
            session.close()
        except Exception as e:
            logger.error(f"Error closing session: {e}")

db_service = DatabaseService()
