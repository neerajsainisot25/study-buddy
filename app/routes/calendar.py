"""Calendar routes blueprint"""
from flask import Blueprint, request, jsonify
from app.services.llm_service import LLMService
from app.services.storage import storage

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/events', methods=['GET'])
def get_events():
    """Get all events for a date"""
    date = request.args.get('date', '').strip()
    if not date:
        return jsonify({"error": "Date is required"}), 400
    
    events = storage.get_events(date)
    return jsonify({"events": events})

@calendar_bp.route('/events', methods=['POST'])
def add_event():
    """Add a new event"""
    data = request.json or {}
    date = data.get('date', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    time = data.get('time', '').strip()

    if not date or not title:
        return jsonify({"error": "Date and title are required"}), 400

    event = {
        "title": title,
        "description": description,
        "time": time
    }
    
    added_event = storage.add_event(date, event)
    return jsonify({"event": added_event, "status": "added"})

@calendar_bp.route('/events/<date>/<event_id>', methods=['DELETE'])
def delete_event(date, event_id):
    """Delete an event"""
    if storage.delete_event(date, event_id):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Event not found"}), 404

@calendar_bp.route('/suggest', methods=['POST'])
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

@calendar_bp.route('/upcoming', methods=['GET'])
def get_upcoming_events():
    """Get upcoming events for the next 7 days"""
    try:
        from datetime import datetime, timedelta
        
        all_events = storage._memory_storage.get('events', {})
        upcoming = []
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        
        for date_str, events in all_events.items():
            try:
                event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if today <= event_date <= week_end:
                    for event in events:
                        upcoming.append({
                            "date": date_str,
                            "title": event.get('title', ''),
                            "description": event.get('description', ''),
                            "time": event.get('time', '')
                        })
            except ValueError:
                continue
        
        # Sort by date
        upcoming.sort(key=lambda x: x['date'])
        
        return jsonify({
            "events": upcoming,
            "count": len(upcoming),
            "next_event": upcoming[0] if upcoming else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

