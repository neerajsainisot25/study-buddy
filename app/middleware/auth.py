"""Authentication middleware"""
from functools import wraps
from flask import request, jsonify
from app.services.supabase_service import supabase_service

def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        access_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        
        if not access_token:
            return jsonify({"error": "Authentication required"}), 401
        
        try:
            user = supabase_service.get_user(access_token)
            if not user:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            # Add user to request context
            request.user = user
            request.user_id = user.get('id')
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication - adds user to request if available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        access_token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
        
        try:
            if access_token:
                user = supabase_service.get_user(access_token)
                if user:
                    request.user = user
                    request.user_id = user.get('id')
        except Exception:
            pass
        
        # Continue even if no auth or invalid token
        if not hasattr(request, 'user'):
            request.user = None
            request.user_id = None
        
        return f(*args, **kwargs)
    
    return decorated_function
