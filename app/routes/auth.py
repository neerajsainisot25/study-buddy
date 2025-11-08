"""Authentication routes for Supabase integration"""
from flask import Blueprint, request, jsonify, session
from app.services.supabase_service import supabase_service
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "No authorization token provided"}), 401
        
        access_token = auth_header.replace('Bearer ', '')
        user = supabase_service.get_user(access_token)
        
        if not user:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        request.user = user
        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check if Supabase auth is available"""
    return jsonify({
        "available": supabase_service.is_available(),
        "configured": supabase_service.is_available()
    })

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Sign up a new user"""
    if not supabase_service.is_available():
        return jsonify({"error": "Authentication not configured"}), 503
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400
    
    try:
        result = supabase_service.sign_up(
            email=email,
            password=password,
            metadata={"name": name}
        )
        
        return jsonify({
            "success": True,
            "user": result['user'],
            "session": result['session']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/signin', methods=['POST'])
def signin():
    """Sign in an existing user"""
    if not supabase_service.is_available():
        return jsonify({"error": "Authentication not configured"}), 503
    
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    try:
        result = supabase_service.sign_in(email=email, password=password)
        
        return jsonify({
            "success": True,
            "user": result['user'],
            "session": result['session']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/signout', methods=['POST'])
@require_auth
def signout():
    """Sign out the current user"""
    auth_header = request.headers.get('Authorization', '')
    access_token = auth_header.replace('Bearer ', '')
    
    try:
        supabase_service.sign_out(access_token)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info"""
    return jsonify({
        "success": True,
        "user": request.user
    })

@auth_bp.route('/update-profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    data = request.json
    auth_header = request.headers.get('Authorization', '')
    access_token = auth_header.replace('Bearer ', '')
    
    try:
        # Update user metadata
        updates = {}
        if 'name' in data:
            updates['data'] = {'name': data['name']}
        
        if 'email' in data:
            updates['email'] = data['email']
        
        if 'password' in data:
            if len(data['password']) < 8:
                return jsonify({"error": "Password must be at least 8 characters"}), 400
            updates['password'] = data['password']
        
        if not updates:
            return jsonify({"error": "No valid updates provided"}), 400
        
        # Use the client to update user
        supabase_service.client.auth.set_session(access_token, "")
        result = supabase_service.client.auth.update_user(updates)
        
        return jsonify({
            "success": True,
            "user": result.user.model_dump() if result.user else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
