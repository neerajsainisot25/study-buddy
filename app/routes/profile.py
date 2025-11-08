"""Profile management routes"""
from flask import Blueprint, request, jsonify
from app.services.supabase_service import supabase_service
from app.routes.auth import require_auth

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        user = request.user
        
        # Get additional profile data from database if needed
        # For now, return user metadata
        profile_data = {
            "id": user.get('id'),
            "email": user.get('email'),
            "name": user.get('user_metadata', {}).get('name', ''),
            "avatar_url": user.get('user_metadata', {}).get('avatar_url', ''),
            "created_at": user.get('created_at'),
            "email_confirmed": user.get('email_confirmed_at') is not None
        }
        
        return jsonify({
            "success": True,
            "profile": profile_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@profile_bp.route('/upload-avatar', methods=['POST'])
@require_auth
def upload_avatar():
    """Upload user avatar"""
    if not supabase_service.is_available():
        return jsonify({"error": "Storage not configured"}), 503
    
    if 'avatar' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return jsonify({"error": "Invalid file type. Only images allowed."}), 400
    
    # Validate file size (max 5MB)
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:
        return jsonify({"error": "File too large. Maximum size is 5MB."}), 400
    
    try:
        user_id = request.user.get('id')
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        file_path = f"avatars/{user_id}.{file_ext}"
        
        # Upload to Supabase storage
        file_data = file.read()
        result = supabase_service.upload_file(
            bucket='avatars',
            path=file_path,
            file_data=file_data,
            content_type=file.content_type
        )
        
        # Get public URL
        avatar_url = supabase_service.get_file_url('avatars', file_path)
        
        # Update user metadata with avatar URL
        auth_header = request.headers.get('Authorization', '')
        access_token = auth_header.replace('Bearer ', '')
        
        supabase_service.client.auth.set_session(access_token, "")
        supabase_service.client.auth.update_user({
            "data": {"avatar_url": avatar_url}
        })
        
        return jsonify({
            "success": True,
            "avatar_url": avatar_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@profile_bp.route('/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get user statistics"""
    try:
        user_id = request.user.get('id')
        
        # Get user statistics from Supabase
        # For now, return mock data - you can enhance this
        stats = {
            "total_quizzes": 0,
            "average_score": 0,
            "total_chat_sessions": 0,
            "total_events": 0,
            "study_streak": 0,
            "total_study_hours": 0
        }
        
        # You can query actual data from Supabase tables here
        # Example: Get quiz count
        # quizzes = supabase_service.client.table('quizzes').select('*').eq('user_id', user_id).execute()
        # stats['total_quizzes'] = len(quizzes.data) if quizzes.data else 0
        
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
