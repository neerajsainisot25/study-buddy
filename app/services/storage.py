"""Storage service for managing application data"""
import json
import os
from typing import Dict, List, Any, Optional
from app.config import Config
from app.services.supabase_service import supabase_service

class StorageService:
    """Service for managing data storage"""
    
    def __init__(self):
        self.storage_type = Config.STORAGE_TYPE
        self.storage_file = Config.STORAGE_FILE
        self._memory_storage = {
            'conversations': {},
            'events': {}
        }
        # Disable Supabase for now - using memory storage only
        self.use_supabase = False
        self._load_from_file()
    
    def _load_from_file(self):
        """Load data from file if storage type is file"""
        if self.storage_type == 'file' and os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self._memory_storage = json.load(f)
            except Exception as e:
                print(f"Error loading storage file: {e}")
    
    def _save_to_file(self):
        """Save data to file if storage type is file"""
        if self.storage_type == 'file':
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            try:
                with open(self.storage_file, 'w') as f:
                    json.dump(self._memory_storage, f, indent=2)
            except Exception as e:
                print(f"Error saving storage file: {e}")
    
    # Conversation methods
    def get_conversation(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        return self._memory_storage['conversations'].get(session_id, [])
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation history"""
        if session_id not in self._memory_storage['conversations']:
            self._memory_storage['conversations'][session_id] = []
        
        self._memory_storage['conversations'][session_id].append({
            "role": role,
            "content": content
        })
        self._save_to_file()
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self._memory_storage['conversations']:
            self._memory_storage['conversations'][session_id] = []
            self._save_to_file()
    
    # Event methods
    def get_events(self, date: str) -> List[Dict[str, Any]]:
        """Get events for a specific date"""
        return self._memory_storage['events'].get(date, [])
    
    def add_event(self, date: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add an event"""
        if date not in self._memory_storage['events']:
            self._memory_storage['events'][date] = []
        
        event['id'] = len(self._memory_storage['events'][date])
        self._memory_storage['events'][date].append(event)
        self._save_to_file()
        return event
    
    def delete_event(self, date: str, event_id: Any) -> bool:
        """Delete an event"""
        if date in self._memory_storage['events'] and isinstance(event_id, int) and event_id < len(self._memory_storage['events'][date]):
            deleted = self._memory_storage['events'][date].pop(event_id)
            # Reindex events
            for i, event in enumerate(self._memory_storage['events'][date]):
                event['id'] = i
            self._save_to_file()
            return True
        return False

# Global storage instance
storage = StorageService()

