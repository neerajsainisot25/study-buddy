"""Profile routes blueprint"""
from flask import Blueprint, request, jsonify, session as flask_session
from app.services.user_service import user_service
from app.services.database import db_service, QuizAttempt
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
import logging
import uuid

logger = logging.getLogger(__name__)

profile_bp = Blueprint('profile', __name__)

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in flask_session:
        flask_session['session_id'] = str(uuid.uuid4())
    return flask_session['session_id']

@profile_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        session_id = get_session_id()
        user_data = user_service.get_or_create_user(session_id)
        
        stats = {
            'days_active': 0,
            'total_quizzes': 0,
            'study_hours': 0,
            'avg_score': 0
        }
        
        if db_service.is_available():
            db_session = None
            try:
                db_session = db_service.get_session()
                
                total_quizzes = db_session.query(func.count(QuizAttempt.id)).filter_by(session_id=session_id).scalar() or 0
                avg_score = db_session.query(func.avg(QuizAttempt.score)).filter_by(session_id=session_id).scalar() or 0
                
                stats['total_quizzes'] = total_quizzes
                stats['avg_score'] = round(avg_score, 1)
                
            except SQLAlchemyError as e:
                logger.error(f"Database error in get_profile: {e}")
            finally:
                if db_session:
                    db_service.close_session(db_session)
        
        return jsonify({
            **user_data,
            **stats
        })
    except Exception as e:
        logger.error(f"Error in get_profile: {e}")
        return jsonify({"error": str(e)}), 500

@profile_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        session_id = get_session_id()
        data = request.json or {}
        
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'email' in data:
            update_data['email'] = data['email']
        if 'grade' in data:
            update_data['grade'] = data['grade']
        if 'bio' in data:
            update_data['bio'] = data['bio']
        if 'weekly_goal' in data:
            update_data['weekly_goal'] = int(data['weekly_goal'])
        
        success = user_service.update_user(session_id, update_data)
        
        if success:
            return jsonify({"success": True, "message": "Profile updated successfully"})
        else:
            return jsonify({"error": "Failed to update profile"}), 500
    except Exception as e:
        logger.error(f"Error in update_profile: {e}")
        return jsonify({"error": str(e)}), 500
