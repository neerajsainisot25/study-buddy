"""Calendar routes with Supabase integration"""
from flask import Blueprint, request, jsonify
from app.services.supabase_service import supabase_service
from app.services.llm_service import LLMService
from app.middleware.auth import require_auth
from datetime import datetime, timedelta

calendar_supabase_bp = Blueprint('calendar_supabase', __name__)

@calendar_supabase_bp.route('/events', methods=['GET'])
@require_auth
def get_events():
    """Get all events for a date"""
    date = request.args.get('date', '').strip()
    user_id = request.user_id
    
    if not date:
        return jsonify({"error": "Date is required"}), 400
    
    try:
        events = supabase_service.get_events(user_id, date)
        return jsonify({"events": events})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calendar_supabase_bp.route('/events', methods=['POST'])
@require_auth
def add_event():
    """Add a new event"""
    data = request.json or {}
    date = data.get('date', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    time = data.get('time', '').strip()
    
    user_id = request.user_id
    
    if not date or not title:
        return jsonify({"error": "Date and title are required"}), 400
    
    try:
        event = {
            "date": date,
            "title": title,
            "description": description,
            "time": time
        }
        
        saved_event = supabase_service.save_event(user_id, event)
        return jsonify({"event": saved_event, "status": "added"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calendar_supabase_bp.route('/events/<event_id>', methods=['DELETE'])
@require_auth
def delete_event(event_id):
    """Delete an event"""
    user_id = request.user_id
    
    try:
        if supabase_service.delete_event(user_id, event_id):
            return jsonify({"status": "deleted"})
        return jsonify({"error": "Event not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calendar_supabase_bp.route('/upcoming', methods=['GET'])
@require_auth
def get_upcoming_events():
    """Get upcoming events for the next 7 days"""
    user_id = request.user_id
    
    try:
        if not supabase_service.is_available():
            return jsonify({"error": "Database not available"}), 500
        
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        
        # Get all events for user in next 7 days
        response = supabase_service.client.table('events').select('*').eq('user_id', user_id).gte('date', str(today)).lte('date', str(week_end)).order('date').order('time').execute()
        
        upcoming = response.data if response.data else []
        
        return jsonify({
            "events": upcoming,
            "count": len(upcoming),
            "next_event": upcoming[0] if upcoming else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@calendar_supabase_bp.route('/suggest', methods=['POST'])
@require_auth
def suggest_event():
    """Use AI to suggest event details"""
    data = request.json or {}
    description = data.get('description', '').strip()
    
    if not description:
        return jsonify({"error": "Description is required"}), 400
    
    try:
        prompt = f"""Based on this description: "{description}", suggest a calendar event with:
1. A concise title (max 50 characters)
2. A brief description (max 200 characters)
3. A suggested time (format: HH:MM)

Return ONLY a JSON object with this structure:
{{
    "title": "Event title",
    "description": "Event description",
    "time": "HH:MM"
}}"""
        
        content = LLMService.call_llm([{"role": "user", "content": prompt}])
        suggestion = LLMService.extract_json(content, json_type='object')
        
        return jsonify({"suggestion": suggestion})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
