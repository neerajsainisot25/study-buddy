"""Authentication routes blueprint"""
from flask import Blueprint, request, jsonify
from app.services.supabase_service import supabase_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    full_name = data.get('full_name', '').strip()
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    try:
        result = supabase_service.sign_up(
            email=email,
            password=password,
            metadata={"full_name": full_name}
        )
        
        return jsonify({
            "message": "Sign up successful! Please check your email to verify your account.",
            "user": result.get('user'),
            "session": result.get('session')
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login a user"""
    data = request.json or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    try:
        result = supabase_service.sign_in(email=email, password=password)
        
        return jsonify({
            "message": "Login successful",
            "user": result.get('user'),
            "session": result.get('session')
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout a user"""
    auth_header = request.headers.get('Authorization', '')
    access_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
    
    if not access_token:
        return jsonify({"error": "No token provided"}), 400
    
    try:
        supabase_service.sign_out(access_token)
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/user', methods=['GET'])
def get_current_user():
    """Get current user from token"""
    auth_header = request.headers.get('Authorization', '')
    access_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
    
    if not access_token:
        return jsonify({"error": "No token provided"}), 401
    
    try:
        user = supabase_service.get_user(access_token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        return jsonify({"user": user}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile with stats"""
    auth_header = request.headers.get('Authorization', '')
    access_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
    
    if not access_token:
        return jsonify({"error": "No token provided"}), 401
    
    try:
        user = supabase_service.get_user(access_token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = user.get('id')
        
        # Get profile from database
        if supabase_service.is_available():
            profile_response = supabase_service.client.table('profiles').select('*').eq('id', user_id).single().execute()
            profile = profile_response.data if profile_response.data else {}
            
            # Get user stats
            quiz_attempts = supabase_service.client.table('quiz_attempts').select('*').eq('user_id', user_id).execute()
            quizzes = supabase_service.client.table('quizzes').select('*').eq('user_id', user_id).execute()
            events = supabase_service.client.table('events').select('*').eq('user_id', user_id).execute()
            
            total_quizzes = len(quizzes.data) if quizzes.data else 0
            total_attempts = len(quiz_attempts.data) if quiz_attempts.data else 0
            avg_score = sum(a.get('score', 0) for a in quiz_attempts.data) / len(quiz_attempts.data) if quiz_attempts.data else 0
            total_events = len(events.data) if events.data else 0
            
            return jsonify({
                "profile": profile,
                "stats": {
                    "total_quizzes": total_quizzes,
                    "total_attempts": total_attempts,
                    "average_score": round(avg_score, 1),
                    "total_events": total_events,
                    "study_streak": profile.get('study_streak', 0),
                    "total_study_hours": float(profile.get('total_study_hours', 0))
                }
            }), 200
        else:
            return jsonify({"error": "Database not available"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    auth_header = request.headers.get('Authorization', '')
    access_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
    
    if not access_token:
        return jsonify({"error": "No token provided"}), 401
    
    data = request.json or {}
    
    try:
        user = supabase_service.get_user(access_token)
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        user_id = user.get('id')
        
        # Update profile
        update_data = {}
        if 'full_name' in data:
            update_data['full_name'] = data['full_name']
        if 'avatar_url' in data:
            update_data['avatar_url'] = data['avatar_url']
        if 'study_streak' in data:
            update_data['study_streak'] = data['study_streak']
        if 'total_study_hours' in data:
            update_data['total_study_hours'] = data['total_study_hours']
        
        if update_data and supabase_service.is_available():
            response = supabase_service.client.table('profiles').update(update_data).eq('id', user_id).execute()
            return jsonify({
                "message": "Profile updated successfully",
                "profile": response.data[0] if response.data else {}
            }), 200
        else:
            return jsonify({"error": "No valid fields to update"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
