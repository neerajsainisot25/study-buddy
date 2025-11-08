"""Analytics routes blueprint"""
from flask import Blueprint, request, jsonify
from app.services.storage import storage
from datetime import datetime, timedelta
import time

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard"""
    try:
        # Quiz Analytics
        quiz_attempts = getattr(storage, '_quiz_attempts', [])
        quiz_storage = getattr(storage, '_quiz_storage', [])
        
        # Chat Analytics
        all_conversations = storage._memory_storage.get('conversations', {})
        user_messages = []
        for session_id, messages in all_conversations.items():
            user_messages.extend([m for m in messages if m.get('role') == 'user'])
        
        # Event Analytics
        all_events = storage._memory_storage.get('events', {})
        total_events = sum(len(events) for events in all_events.values())
        
        # Time-based calculations
        now = time.time()
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        week_start = (datetime.now() - timedelta(days=7)).timestamp()
        month_start = (datetime.now() - timedelta(days=30)).timestamp()
        
        # Quiz statistics
        total_quiz_attempts = len(quiz_attempts)
        today_quiz_attempts = [a for a in quiz_attempts if a.get('timestamp', 0) >= today_start]
        week_quiz_attempts = [a for a in quiz_attempts if a.get('timestamp', 0) >= week_start]
        
        quiz_avg_score = sum(a['score'] for a in quiz_attempts) / len(quiz_attempts) if quiz_attempts else 0
        today_avg_score = sum(a['score'] for a in today_quiz_attempts) / len(today_quiz_attempts) if today_quiz_attempts else 0
        
        # Quiz by difficulty
        quiz_by_difficulty = {}
        for quiz in quiz_storage:
            diff = quiz.get('difficulty', 'unknown')
            quiz_by_difficulty[diff] = quiz_by_difficulty.get(diff, 0) + 1
        
        # Quiz by type
        quiz_by_type = {}
        for quiz in quiz_storage:
            qtype = quiz.get('quiz_type', 'unknown')
            quiz_by_type[qtype] = quiz_by_type.get(qtype, 0) + 1
        
        # Chat statistics
        total_queries = len(user_messages)
        today_queries = len([m for m in user_messages if True])  # Simplified - would need timestamps
        week_queries = total_queries  # Simplified
        
        # Task completion (quizzes + events)
        completed_tasks = {
            'quizzes': total_quiz_attempts,
            'events': total_events,
            'chats': len(all_conversations)
        }
        
        # Recent activity
        recent_quiz_attempts = sorted(quiz_attempts, key=lambda x: x.get('timestamp', 0), reverse=True)[:5]
        recent_activity = []
        for attempt in recent_quiz_attempts:
            recent_activity.append({
                'type': 'quiz',
                'title': attempt.get('topic', 'Quiz'),
                'score': attempt.get('score', 0),
                'timestamp': attempt.get('timestamp', 0),
                'time_ago': format_time_ago(attempt.get('timestamp', 0))
            })
        
        # Performance trends (last 7 days)
        daily_stats = {}
        for i in range(7):
            day_start = (datetime.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
            day_end = day_start + 86400
            day_attempts = [a for a in quiz_attempts if day_start <= a.get('timestamp', 0) < day_end]
            date_str = datetime.fromtimestamp(day_start).strftime('%Y-%m-%d')
            daily_stats[date_str] = {
                'date': date_str,
                'quizzes': len(day_attempts),
                'avg_score': sum(a['score'] for a in day_attempts) / len(day_attempts) if day_attempts else 0
            }
        
        return jsonify({
            'quiz': {
                'total_attempts': total_quiz_attempts,
                'total_quizzes': len(quiz_storage),
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
                'active_sessions': len(all_conversations)
            },
            'tasks': {
                'completed': completed_tasks,
                'total': sum(completed_tasks.values())
            },
            'activity': {
                'recent': recent_activity,
                'last_updated': now
            },
            'trends': {
                'daily': list(daily_stats.values())
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/quiz', methods=['GET'])
def get_quiz_analytics():
    """Get detailed quiz analytics"""
    try:
        quiz_attempts = getattr(storage, '_quiz_attempts', [])
        quiz_storage = getattr(storage, '_quiz_storage', [])
        
        # Detailed statistics
        now = time.time()
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        week_start = (datetime.now() - timedelta(days=7)).timestamp()
        
        # Score distribution
        score_ranges = {
            '0-50': 0,
            '51-70': 0,
            '71-85': 0,
            '86-100': 0
        }
        
        for attempt in quiz_attempts:
            score = attempt.get('score', 0)
            if score <= 50:
                score_ranges['0-50'] += 1
            elif score <= 70:
                score_ranges['51-70'] += 1
            elif score <= 85:
                score_ranges['71-85'] += 1
            else:
                score_ranges['86-100'] += 1
        
        # Topic performance
        topic_performance = {}
        for attempt in quiz_attempts:
            topic = attempt.get('topic', 'Unknown')
            if topic not in topic_performance:
                topic_performance[topic] = {'count': 0, 'total_score': 0}
            topic_performance[topic]['count'] += 1
            topic_performance[topic]['total_score'] += attempt.get('score', 0)
        
        for topic in topic_performance:
            topic_performance[topic]['avg_score'] = round(
                topic_performance[topic]['total_score'] / topic_performance[topic]['count'], 1
            )
        
        return jsonify({
            'summary': {
                'total_attempts': len(quiz_attempts),
                'total_quizzes': len(quiz_storage),
                'average_score': round(sum(a['score'] for a in quiz_attempts) / len(quiz_attempts), 1) if quiz_attempts else 0,
                'today_attempts': len([a for a in quiz_attempts if a.get('timestamp', 0) >= today_start]),
                'week_attempts': len([a for a in quiz_attempts if a.get('timestamp', 0) >= week_start])
            },
            'score_distribution': score_ranges,
            'topic_performance': topic_performance,
            'recent_attempts': sorted(quiz_attempts, key=lambda x: x.get('timestamp', 0), reverse=True)[:20]
        })
    except Exception as e:
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

