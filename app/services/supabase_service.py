"""Supabase service for database, auth, and storage operations"""
from supabase import create_client, Client
from app.config import Config
from typing import Optional, Dict, List, Any
import json

class SupabaseService:
    """Service for Supabase operations"""
    
    def __init__(self):
        # Check if Supabase config exists
        supabase_url = getattr(Config, 'SUPABASE_URL', None)
        supabase_key = getattr(Config, 'SUPABASE_KEY', None)
        
        if not supabase_url or not supabase_key:
            self.client = None
            self.service_client = None
            self.available = False
        else:
            try:
                # Initialize Supabase client (simplified for compatibility)
                self.client: Client = create_client(supabase_url, supabase_key)
                self.available = True
                
                # Try to initialize service client (optional, for admin operations)
                # Service client is only needed for admin operations that bypass RLS
                self.service_client: Optional[Client] = None
                supabase_service_key = getattr(Config, 'SUPABASE_SERVICE_KEY', None)
                if supabase_service_key and supabase_service_key.strip():
                    try:
                        self.service_client = create_client(supabase_url, supabase_service_key)
                    except Exception:
                        # Service key is optional, silently fail - main client still works
                        self.service_client = None
            except Exception as e:
                print(f"Error initializing Supabase: {e}")
                import traceback
                traceback.print_exc()
                self.client = None
                self.service_client = None
                self.available = False
    
    def is_available(self) -> bool:
        """Check if Supabase is configured and available"""
        return self.available and self.client is not None
    
    # ==================== AUTHENTICATION ====================
    
    def sign_up(self, email: str, password: str, metadata: Dict = None) -> Dict:
        """Sign up a new user"""
        if not self.is_available():
            raise Exception("Supabase not configured")
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            return {
                "user": response.user.model_dump() if response.user else None,
                "session": response.session.model_dump() if response.session else None
            }
        except Exception as e:
            raise Exception(f"Sign up error: {str(e)}")
    
    def sign_in(self, email: str, password: str) -> Dict:
        """Sign in a user"""
        if not self.is_available():
            raise Exception("Supabase not configured")
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "user": response.user.model_dump(),
                "session": response.session.model_dump()
            }
        except Exception as e:
            raise Exception(f"Sign in error: {str(e)}")
    
    def sign_out(self, access_token: str) -> bool:
        """Sign out a user"""
        if not self.is_available():
            return False
        
        try:
            # Set the session for the client
            self.client.auth.set_session(access_token, "")
            self.client.auth.sign_out()
            return True
        except Exception as e:
            print(f"Sign out error: {e}")
            return False
    
    def get_user(self, access_token: str) -> Optional[Dict]:
        """Get user from access token"""
        if not self.is_available():
            return None
        
        try:
            self.client.auth.set_session(access_token, "")
            user = self.client.auth.get_user()
            return user.user.model_dump() if user.user else None
        except Exception as e:
            print(f"Get user error: {e}")
            return None
    
    def verify_token(self, access_token: str) -> Optional[Dict]:
        """Verify and get user from access token"""
        return self.get_user(access_token)
    
    # ==================== DATABASE OPERATIONS ====================
    
    def get_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        if not self.is_available():
            return []
        
        try:
            response = self.client.table('conversations').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return [dict(row) for row in response.data] if response.data else []
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def get_conversation_messages(self, conversation_id: str, user_id: str) -> List[Dict]:
        """Get messages for a conversation"""
        if not self.is_available():
            return []
        
        try:
            response = self.client.table('messages').select('*').eq('conversation_id', conversation_id).eq('user_id', user_id).order('created_at').execute()
            return [dict(row) for row in response.data] if response.data else []
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def get_or_create_conversation(self, user_id: str, session_id: str, title: str = None) -> str:
        """Get existing conversation or create a new one, returns conversation_id"""
        if not self.is_available():
            return session_id
        
        try:
            # Try to find existing conversation by checking if session_id is a valid UUID
            # If it's a UUID, use it as conversation_id
            # Otherwise, create a new conversation
            import uuid as uuid_lib
            try:
                # Check if session_id is already a valid UUID
                conv_uuid = uuid_lib.UUID(session_id)
                # Verify this conversation exists and belongs to user
                response = self.client.table('conversations').select('id').eq('id', str(conv_uuid)).eq('user_id', user_id).limit(1).execute()
                if response.data:
                    return str(conv_uuid)
            except (ValueError, AttributeError):
                # session_id is not a UUID, create new conversation
                pass
            
            # Create a new conversation
            conversation = self.create_conversation(user_id, title or f"Conversation {session_id[:8]}")
            return conversation.get('id', session_id)
        except Exception as e:
            print(f"Error getting/creating conversation: {e}")
            # Fallback: if we can't create conversation, return session_id
            # The storage service will handle fallback to memory
            return session_id
    
    def save_message(self, user_id: str, conversation_id: str, role: str, content: str) -> Dict:
        """Save a message"""
        if not self.is_available():
            raise Exception("Supabase not configured")
        
        try:
            # Use service client if available to bypass RLS for server-side operations
            client = self.service_client if self.service_client else self.client
            
            data = {
                'user_id': user_id,
                'conversation_id': conversation_id,
                'role': role,
                'content': content
            }
            response = client.table('messages').insert(data).execute()
            return dict(response.data[0]) if response.data else {}
        except Exception as e:
            raise Exception(f"Error saving message: {str(e)}")
    
    def create_conversation(self, user_id: str, title: str = None) -> Dict:
        """Create a new conversation"""
        if not self.is_available():
            raise Exception("Supabase not configured")
        
        try:
            # Use service client if available to bypass RLS for server-side operations
            client = self.service_client if self.service_client else self.client
            
            data = {
                'user_id': user_id,
                'title': title or 'New Conversation'
            }
            response = client.table('conversations').insert(data).execute()
            return dict(response.data[0]) if response.data else {}
        except Exception as e:
            raise Exception(f"Error creating conversation: {str(e)}")
    
    def get_events(self, user_id: str, date: str = None) -> List[Dict]:
        """Get events for a user, optionally filtered by date"""
        if not self.is_available():
            return []
        
        try:
            query = self.client.table('events').select('*').eq('user_id', user_id)
            if date:
                query = query.eq('date', date)
            response = query.order('date').order('time').execute()
            return [dict(row) for row in response.data] if response.data else []
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def save_event(self, user_id: str, event: Dict) -> Dict:
        """Save an event"""
        if not self.is_available():
            raise Exception("Supabase not configured")
        
        try:
            # Use service client if available to bypass RLS for server-side operations
            client = self.service_client if self.service_client else self.client
            
            event['user_id'] = user_id
            response = client.table('events').insert(event).execute()
            return dict(response.data[0]) if response.data else {}
        except Exception as e:
            raise Exception(f"Error saving event: {str(e)}")
    
    def delete_event(self, user_id: str, event_id: str) -> bool:
        """Delete an event"""
        if not self.is_available():
            return False
        
        try:
            self.client.table('events').delete().eq('id', event_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    # ==================== STORAGE OPERATIONS ====================
    
    def upload_file(self, bucket: str, path: str, file_data: bytes, content_type: str = None) -> Dict:
        """Upload a file to Supabase storage"""
        if not self.is_available():
            raise Exception("Supabase not configured")
        
        try:
            response = self.client.storage.from_(bucket).upload(path, file_data, file_options={"content-type": content_type})
            return response
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")
    
    def get_file_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file"""
        if not self.is_available():
            raise Exception("Supabase not configured")
        
        try:
            response = self.client.storage.from_(bucket).get_public_url(path)
            return response
        except Exception as e:
            raise Exception(f"Error getting file URL: {str(e)}")
    
    def delete_file(self, bucket: str, path: str) -> bool:
        """Delete a file from storage"""
        if not self.is_available():
            return False
        
        try:
            self.client.storage.from_(bucket).remove([path])
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

# Global Supabase service instance
supabase_service = SupabaseService()

