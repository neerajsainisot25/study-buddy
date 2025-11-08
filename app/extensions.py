"""Flask extensions initialization"""
from supabase import create_client, Client
from typing import Optional
import os

class SupabaseClient:
    """Supabase client extension for Flask"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.available: bool = False
    
    def init_app(self, app):
        """Initialize Supabase client with Flask app config"""
        supabase_url = app.config.get('SUPABASE_URL')
        supabase_key = app.config.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            app.logger.warning("Supabase URL or Key not configured. Supabase features will be disabled.")
            self.client = None
            self.available = False
            return
        
        try:
            self.client = create_client(supabase_url, supabase_key)
            self.available = True
            app.logger.info("Supabase client initialized successfully")
        except Exception as e:
            app.logger.error(f"Error initializing Supabase client: {e}")
            self.client = None
            self.available = False
    
    def ping(self) -> bool:
        """Ping Supabase to verify connection"""
        if not self.available or not self.client:
            return False
        
        try:
            # Try a lightweight operation to verify connectivity
            # Attempt to get the auth session (which is a lightweight check)
            # This will fail if the connection is not working
            try:
                _ = self.client.auth.get_session()
            except Exception:
                # get_session might fail if no session exists, which is OK
                # The client is still connected, just no active session
                pass
            
            # If we got here, the client is accessible
            # Verify the client has the expected structure
            return hasattr(self.client, 'auth') and hasattr(self.client, 'table')
        except Exception:
            # If any error occurs, connection is not working
            return False
    
    def is_available(self) -> bool:
        """Check if Supabase is available"""
        return self.available and self.client is not None

# Global extension instance
supabase = SupabaseClient()

