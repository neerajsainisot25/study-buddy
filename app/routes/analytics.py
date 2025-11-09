"""Analytics routes blueprint"""
from flask import Blueprint, request, jsonify, session as flask_session
from app.services.storage import storage
from app.services.database import db_service, Quiz, QuizAttempt, ChatMessage, CalendarEvent, User
from sqlalchemy import func as sql_func
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import time
import uuid
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__)

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in flask_session:
        flask_session['session_id'] = str(uuid.uuid4())
    return flask_session['session_id']

@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard"""
    try:
        session_id = get_session_id()
        
        # Time-based calculations
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Initialize default values
        quiz_data = {
            'total_attempts': 0,
            'total_quizzes': 0,
            'today_attempts': 0,
            'week_attempts': 0,
            'average_score': 0,
            'today_avg_score': 0,
            'by_difficulty': {},
            'by_type': {},
            'recent_attempts': [],
            'by_topic': {}
        }
        chat_data = {
            'total_queries': 0,
            'today_queries': 0,
            'week_queries': 0,
            'active_sessions': 1
        }
        event_data = {
            'total_events': 0,
            'upcoming_events': 0
        }
        daily_stats = []
        recent_activity = []
        recent_chats = []
        
        if db_service.is_available():
            db_session = None
            try:
                db_session = db_service.get_session()
                
                # Quiz Analytics from Database
                quiz_attempts = db_session.query(QuizAttempt).filter_by(session_id=session_id).all()
                quizzes = db_session.query(Quiz).filter_by(session_id=session_id).all()
                
                quiz_data['total_attempts'] = len(quiz_attempts)
                quiz_data['total_quizzes'] = len(quizzes)
                
                today_attempts = [a for a in quiz_attempts if a.created_at >= today_start]
                week_attempts = [a for a in quiz_attempts if a.created_at >= week_start]
                
                quiz_data['today_attempts'] = len(today_attempts)
                quiz_data['week_attempts'] = len(week_attempts)
                
                if quiz_attempts:
                    quiz_data['average_score'] = round(sum(a.score for a in quiz_attempts) / len(quiz_attempts), 1)
                if today_attempts:
                    quiz_data['today_avg_score'] = round(sum(a.score for a in today_attempts) / len(today_attempts), 1)
                
                # Quiz by difficulty and type
                for quiz in quizzes:
                    diff = quiz.difficulty or 'unknown'
                    quiz_data['by_difficulty'][diff] = quiz_data['by_difficulty'].get(diff, 0) + 1
                    
                    qtype = quiz.quiz_type or 'unknown'
                    quiz_data['by_type'][qtype] = quiz_data['by_type'].get(qtype, 0) + 1
                
                # Quiz by topic performance
                topic_performance = {}
                for attempt in quiz_attempts:
                    topic = attempt.topic or 'Unknown'
                    if topic not in topic_performance:
                        topic_performance[topic] = {'count': 0, 'total_score': 0, 'scores': []}
                    topic_performance[topic]['count'] += 1
                    topic_performance[topic]['total_score'] += attempt.score
                    topic_performance[topic]['scores'].append(attempt.score)
                
                for topic in topic_performance:
                    topic_performance[topic]['avg_score'] = round(
                        topic_performance[topic]['total_score'] / topic_performance[topic]['count'], 1
                    )
                
                quiz_data['by_topic'] = topic_performance
                
                # Recent quiz attempts
                quiz_data['recent_attempts'] = [{
                    'quiz_id': a.quiz_id,
                    'topic': a.topic,
                    'score': a.score,
                    'correct': a.correct,
                    'total': a.total,
                    'time_taken': a.time_taken,
                    'timestamp': a.created_at.timestamp()
                } for a in sorted(quiz_attempts, key=lambda x: x.created_at, reverse=True)[:10]]
                
                # Chat Analytics
                chat_messages = db_session.query(ChatMessage).filter_by(session_id=session_id).all()
                user_messages = [m for m in chat_messages if m.role == 'user']
                
                chat_data['total_queries'] = len(user_messages)
                chat_data['today_queries'] = len([m for m in user_messages if m.created_at >= today_start])
                chat_data['week_queries'] = len([m for m in user_messages if m.created_at >= week_start])
                
                # Recent chat sessions (last 3 user messages)
                recent_chats = [{
                    'question': m.content[:100] + '...' if len(m.content) > 100 else m.content,
                    'timestamp': m.created_at.timestamp(),
                    'time_ago': format_time_ago(m.created_at.timestamp())
                } for m in sorted(user_messages, key=lambda x: x.created_at, reverse=True)[:3]]
                
                # Event Analytics
                events = db_session.query(CalendarEvent).filter_by(session_id=session_id).all()
                event_data['total_events'] = len(events)
                
                # Upcoming events (next 7 days)
                upcoming = [e for e in events if datetime.strptime(e.date, '%Y-%m-%d').date() >= now.date()]
                event_data['upcoming_events'] = len(upcoming)
                
                # Daily performance trends (last 7 days)
                for i in range(7):
                    day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
                    day_end = day_start + timedelta(days=1)
                    day_attempts = [a for a in quiz_attempts if day_start <= a.created_at < day_end]
                    
                    daily_stats.append({
                        'date': day_start.strftime('%Y-%m-%d'),
                        'quizzes': len(day_attempts),
                        'avg_score': round(sum(a.score for a in day_attempts) / len(day_attempts), 1) if day_attempts else 0
                    })
                
                # Recent activity
                for attempt in quiz_attempts[-5:]:
                    recent_activity.append({
                        'type': 'quiz',
                        'title': attempt.topic or 'Quiz',
                        'score': attempt.score,
                        'timestamp': attempt.created_at.timestamp(),
                        'time_ago': format_time_ago(attempt.created_at.timestamp())
                    })
                
            except SQLAlchemyError as e:
                logger.error(f"Database error in dashboard analytics: {e}")
            finally:
                if db_session:
                    db_service.close_session(db_session)
        
        # Fallback to memory storage if database not available
        else:
            quiz_attempts = getattr(storage, '_quiz_attempts', [])
            quiz_storage = getattr(storage, '_quiz_storage', [])
            
            quiz_data['total_attempts'] = len(quiz_attempts)
            quiz_data['total_quizzes'] = len(quiz_storage)
            
            if quiz_attempts:
                quiz_data['average_score'] = round(sum(a['score'] for a in quiz_attempts) / len(quiz_attempts), 1)
        
        return jsonify({
            'quiz': quiz_data,
            'chat': chat_data,
            'events': event_data,
            'tasks': {
                'completed': {
                    'quizzes': quiz_data['total_attempts'],
                    'events': event_data['total_events'],
                    'chats': chat_data['total_queries']
                },
                'total': quiz_data['total_attempts'] + event_data['total_events'] + chat_data['total_queries']
            },
            'activity': {
                'recent': recent_activity,
                'recent_chats': recent_chats,
                'last_updated': time.time()
            },
            'trends': {
                'daily': daily_stats
            }
        })
    except Exception as e:
        logger.error(f"Error in dashboard analytics: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/quiz', methods=['GET'])
def get_quiz_analytics():
    """Get detailed quiz analytics"""
    try:
        session_id = get_session_id()
        
        # Detailed statistics
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        
        # Initialize default values
        score_ranges = {'0-50': 0, '51-70': 0, '71-85': 0, '86-100': 0}
        topic_performance = {}
        summary = {
            'total_attempts': 0,
            'total_quizzes': 0,
            'average_score': 0,
            'today_attempts': 0,
            'week_attempts': 0
        }
        recent_attempts = []
        
        if db_service.is_available():
            db_session = None
            try:
                db_session = db_service.get_session()
                
                quiz_attempts = db_session.query(QuizAttempt).filter_by(session_id=session_id).all()
                quizzes = db_session.query(Quiz).filter_by(session_id=session_id).all()
                
                # Score distribution
                for attempt in quiz_attempts:
                    score = attempt.score
                    if score <= 50:
                        score_ranges['0-50'] += 1
                    elif score <= 70:
                        score_ranges['51-70'] += 1
                    elif score <= 85:
                        score_ranges['71-85'] += 1
                    else:
                        score_ranges['86-100'] += 1
                
                # Topic performance
                for attempt in quiz_attempts:
                    topic = attempt.topic or 'Unknown'
                    if topic not in topic_performance:
                        topic_performance[topic] = {'count': 0, 'total_score': 0}
                    topic_performance[topic]['count'] += 1
                    topic_performance[topic]['total_score'] += attempt.score
                
                for topic in topic_performance:
                    topic_performance[topic]['avg_score'] = round(
                        topic_performance[topic]['total_score'] / topic_performance[topic]['count'], 1
                    )
                
                # Summary
                summary['total_attempts'] = len(quiz_attempts)
                summary['total_quizzes'] = len(quizzes)
                summary['average_score'] = round(sum(a.score for a in quiz_attempts) / len(quiz_attempts), 1) if quiz_attempts else 0
                summary['today_attempts'] = len([a for a in quiz_attempts if a.created_at >= today_start])
                summary['week_attempts'] = len([a for a in quiz_attempts if a.created_at >= week_start])
                
                # Recent attempts
                recent_attempts = [{
                    'quiz_id': a.quiz_id,
                    'topic': a.topic,
                    'score': a.score,
                    'correct': a.correct,
                    'total': a.total,
                    'time_taken': a.time_taken,
                    'timestamp': a.created_at.timestamp()
                } for a in sorted(quiz_attempts, key=lambda x: x.created_at, reverse=True)[:20]]
                
            except SQLAlchemyError as e:
                logger.error(f"Database error in quiz analytics: {e}")
            finally:
                if db_session:
                    db_service.close_session(db_session)
        
        return jsonify({
            'summary': summary,
            'score_distribution': score_ranges,
            'topic_performance': topic_performance,
            'recent_attempts': recent_attempts
        })
    except Exception as e:
        logger.error(f"Error in quiz analytics: {e}")
        return jsonify({"error": str(e)}), 500

def format_time_ago(timestamp):
    """Format timestamp as time ago string"""
    if not timestamp:
        return "Unknown"
    
    seconds = time.time() - timestamp
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)}h ago"
    else:
        return f"{int(seconds / 86400)}d ago"

