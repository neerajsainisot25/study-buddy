"""Analytics routes with Supabase integration"""
from flask import Blueprint, request, jsonify
from app.services.supabase_service import supabase_service
from app.middleware.auth import require_auth
from datetime import datetime, timedelta

analytics_supabase_bp = Blueprint('analytics_supabase', __name__)

@analytics_supabase_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard from Supabase"""
    user_id = request.user_id
    
    try:
        if not supabase_service.is_available():
            return jsonify({"error": "Database not available"}), 500
        
        # Get all user data
        quiz_attempts_response = supabase_service.client.table('quiz_attempts').select('*').eq('user_id', user_id).execute()
        quizzes_response = supabase_service.client.table('quizzes').select('*').eq('user_id', user_id).execute()
        events_response = supabase_service.client.table('events').select('*').eq('user_id', user_id).execute()
        conversations_response = supabase_service.client.table('conversations').select('*').eq('user_id', user_id).execute()
        messages_response = supabase_service.client.table('messages').select('*').eq('user_id', user_id).eq('role', 'user').execute()
        
        quiz_attempts = quiz_attempts_response.data if quiz_attempts_response.data else []
        quizzes = quizzes_response.data if quizzes_response.data else []
        events = events_response.data if events_response.data else []
        conversations = conversations_response.data if conversations_response.data else []
        user_messages = messages_response.data if messages_response.data else []
        
        # Time-based calculations
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Quiz statistics
        total_quiz_attempts = len(quiz_attempts)
        today_quiz_attempts = [a for a in quiz_attempts if datetime.fromisoformat(a.get('created_at', '').replace('Z', '+00:00')) >= today_start]
        week_quiz_attempts = [a for a in quiz_attempts if datetime.fromisoformat(a.get('created_at', '').replace('Z', '+00:00')) >= week_start]
        
        quiz_avg_score = sum(a.get('score', 0) for a in quiz_attempts) / len(quiz_attempts) if quiz_attempts else 0
        today_avg_score = sum(a.get('score', 0) for a in today_quiz_attempts) / len(today_quiz_attempts) if today_quiz_attempts else 0
        
        # Quiz by difficulty
        quiz_by_difficulty = {}
        for quiz in quizzes:
            diff = quiz.get('difficulty', 'unknown')
            quiz_by_difficulty[diff] = quiz_by_difficulty.get(diff, 0) + 1
        
        # Quiz by type
        quiz_by_type = {}
        for quiz in quizzes:
            qtype = quiz.get('quiz_type', 'unknown')
            quiz_by_type[qtype] = quiz_by_type.get(qtype, 0) + 1
        
        # Chat statistics
        total_queries = len(user_messages)
        today_queries = len([m for m in user_messages if datetime.fromisoformat(m.get('created_at', '').replace('Z', '+00:00')) >= today_start])
        week_queries = len([m for m in user_messages if datetime.fromisoformat(m.get('created_at', '').replace('Z', '+00:00')) >= week_start])
        
        # Task completion
        completed_tasks = {
            'quizzes': total_quiz_attempts,
            'events': len(events),
            'chats': len(conversations)
        }
        
        # Recent activity
        recent_quiz_attempts = sorted(quiz_attempts, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        recent_activity = []
        for attempt in recent_quiz_attempts:
            created_at = datetime.fromisoformat(attempt.get('created_at', '').replace('Z', '+00:00'))
            time_ago = format_time_ago(created_at)
            recent_activity.append({
                'type': 'quiz',
                'title': attempt.get('topic', 'Quiz'),
                'score': attempt.get('score', 0),
                'timestamp': attempt.get('created_at', ''),
                'time_ago': time_ago
            })
        
        # Performance trends (last 7 days)
        daily_stats = {}
        for i in range(7):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_attempts = [a for a in quiz_attempts if day_start <= datetime.fromisoformat(a.get('created_at', '').replace('Z', '+00:00')) < day_end]
            date_str = day.strftime('%Y-%m-%d')
            daily_stats[date_str] = {
                'date': date_str,
                'quizzes': len(day_attempts),
                'avg_score': sum(a.get('score', 0) for a in day_attempts) / len(day_attempts) if day_attempts else 0
            }
        
        return jsonify({
            'quiz': {
                'total_attempts': total_quiz_attempts,
                'total_quizzes': len(quizzes),
                'today_attempts': len(today_quiz_attempts),
                'week_attempts': len(week_quiz_attempts),
                'average_score': round(quiz_avg_score, 1),
                'today_avg_score': round(today_avg_score, 1),
                'by_difficulty': quiz_by_difficulty,
                'by_type': quiz_by_type,
                'recent_attempts': recent_quiz_attempts[:10]
            },
            'chat': {
                'total_queries': total_queries,
                'today_queries': today_queries,
                'week_queries': week_queries,
                'active_sessions': len(conversations)
            },
            'tasks': {
                'completed': completed_tasks,
                'total': sum(completed_tasks.values())
            },
            'activity': {
                'recent': recent_activity,
                'last_updated': now.isoformat()
            },
            'trends': {
                'daily': list(daily_stats.values())
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def format_time_ago(dt):
    """Format datetime as time ago string"""
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
    delta = now - dt
    
    seconds = delta.total_seconds()
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds / 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)}h ago"
    else:
        return f"{int(seconds / 86400)}d ago"
