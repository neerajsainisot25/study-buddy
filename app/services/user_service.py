"""User service for managing user data"""
from app.services.database import db_service, User
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Service for user operations"""
    
    @staticmethod
    def get_or_create_user(session_id):
        """Get existing user or create new one"""
        if not db_service.is_available():
            return {
                'session_id': session_id,
                'name': 'Student',
                'email': 'student@studymate.app',
                'grade': 'Not Set',
                'bio': 'Welcome to StudyMate!',
                'weekly_goal': 20
            }
        
        session = None
        try:
            session = db_service.get_session()
            user = session.query(User).filter_by(session_id=session_id).first()
            
            if not user:
                user = User(
                    session_id=session_id,
                    name='Student',
                    email='',
                    grade='Not Set',
                    bio='Welcome to StudyMate!',
                    weekly_goal=20
                )
                session.add(user)
                session.commit()
            
            return {
                'session_id': user.session_id,
                'name': user.name,
                'email': user.email,
                'grade': user.grade,
                'bio': user.bio,
                'weekly_goal': user.weekly_goal
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create_user: {e}")
            if session:
                session.rollback()
            return {
                'session_id': session_id,
                'name': 'Student',
                'email': '',
                'grade': 'Not Set',
                'bio': 'Welcome to StudyMate!',
                'weekly_goal': 20
            }
        finally:
            if session:
                db_service.close_session(session)
    
    @staticmethod
    def update_user(session_id, data):
        """Update user information"""
        if not db_service.is_available():
            return True
        
        session = None
        try:
            session = db_service.get_session()
            user = session.query(User).filter_by(session_id=session_id).first()
            
            if not user:
                user = User(session_id=session_id)
                session.add(user)
            
            if 'name' in data:
                user.name = data['name']
            if 'email' in data:
                user.email = data['email']
            if 'grade' in data:
                user.grade = data['grade']
            if 'bio' in data:
                user.bio = data['bio']
            if 'weekly_goal' in data:
                user.weekly_goal = data['weekly_goal']
            
            session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database error in update_user: {e}")
            if session:
                session.rollback()
            return False
        finally:
            if session:
                db_service.close_session(session)

user_service = UserService()
