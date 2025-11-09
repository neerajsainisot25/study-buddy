"""Storage service for managing application data with database support"""
import json
import os
from typing import Dict, List, Any, Optional
from app.config import Config
from app.services.database import db_service, ChatMessage, Quiz, QuizAttempt, CalendarEvent
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """Service for managing data storage with database fallback"""
    
    def __init__(self):
        self.storage_type = Config.STORAGE_TYPE
        self.storage_file = Config.STORAGE_FILE
        self._memory_storage = {
            'conversations': {},
            'events': {},
            'quizzes': [],
            'quiz_attempts': []
        }
        self._load_from_file()
    
    def _load_from_file(self):
        """Load data from file if storage type is file"""
        if self.storage_type == 'file' and os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self._memory_storage = json.load(f)
            except Exception as e:
                logger.error(f"Error loading storage file: {e}")
    
    def _save_to_file(self):
        """Save data to file if storage type is file"""
        if self.storage_type == 'file':
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            try:
                with open(self.storage_file, 'w') as f:
                    json.dump(self._memory_storage, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving storage file: {e}")
    
    def get_conversation(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        if db_service.is_available():
            session = None
            try:
                session = db_service.get_session()
                messages = session.query(ChatMessage).filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
                return [{"role": msg.role, "content": msg.content} for msg in messages]
            except SQLAlchemyError as e:
                logger.error(f"Database error in get_conversation: {e}")
            finally:
                if session:
                    db_service.close_session(session)
        
        return self._memory_storage['conversations'].get(session_id, [])
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation history"""
        if db_service.is_available():
            session = None
            try:
                session = db_service.get_session()
                message = ChatMessage(session_id=session_id, role=role, content=content)
                session.add(message)
                session.commit()
                return
            except SQLAlchemyError as e:
                logger.error(f"Database error in add_message: {e}")
                if session:
                    session.rollback()
            finally:
                if session:
                    db_service.close_session(session)
        
        if session_id not in self._memory_storage['conversations']:
            self._memory_storage['conversations'][session_id] = []
        
        self._memory_storage['conversations'][session_id].append({
            "role": role,
            "content": content
        })
        self._save_to_file()
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if db_service.is_available():
            session = None
            try:
                session = db_service.get_session()
                session.query(ChatMessage).filter_by(session_id=session_id).delete()
                session.commit()
                return
            except SQLAlchemyError as e:
                logger.error(f"Database error in clear_conversation: {e}")
                if session:
                    session.rollback()
            finally:
                if session:
                    db_service.close_session(session)
        
        if session_id in self._memory_storage['conversations']:
            self._memory_storage['conversations'][session_id] = []
            self._save_to_file()
    
    def get_events(self, session_id: str, date: str) -> List[Dict[str, Any]]:
        """Get events for a specific date"""
        if db_service.is_available():
            session = None
            try:
                session = db_service.get_session()
                events = session.query(CalendarEvent).filter_by(session_id=session_id, date=date).all()
                return [{
                    'id': evt.id,
                    'title': evt.title,
                    'description': evt.description,
                    'date': evt.date,
                    'time': evt.time,
                    'type': evt.type,
                    'priority': evt.priority
                } for evt in events]
            except SQLAlchemyError as e:
                logger.error(f"Database error in get_events: {e}")
            finally:
                if session:
                    db_service.close_session(session)
        
        return self._memory_storage['events'].get(date, [])
    
    def add_event(self, session_id: str, date: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add an event"""
        if db_service.is_available():
            session = None
            try:
                session = db_service.get_session()
                new_event = CalendarEvent(
                    session_id=session_id,
                    title=event.get('title', ''),
                    description=event.get('description', ''),
                    date=date,
                    time=event.get('time', ''),
                    type=event.get('type', ''),
                    priority=event.get('priority', '')
                )
                session.add(new_event)
                session.commit()
                
                return {
                    'id': new_event.id,
                    'title': new_event.title,
                    'description': new_event.description,
                    'date': new_event.date,
                    'time': new_event.time,
                    'type': new_event.type,
                    'priority': new_event.priority
                }
            except SQLAlchemyError as e:
                logger.error(f"Database error in add_event: {e}")
                if session:
                    session.rollback()
            finally:
                if session:
                    db_service.close_session(session)
        
        if date not in self._memory_storage['events']:
            self._memory_storage['events'][date] = []
        
        event['id'] = len(self._memory_storage['events'][date])
        self._memory_storage['events'][date].append(event)
        self._save_to_file()
        return event
    
    def delete_event(self, session_id: str, date: str, event_id: Any) -> bool:
        """Delete an event"""
        if db_service.is_available():
            session = None
            try:
                session = db_service.get_session()
                event = session.query(CalendarEvent).filter_by(session_id=session_id, id=event_id).first()
                if event:
                    session.delete(event)
                    session.commit()
                    return True
                return False
            except SQLAlchemyError as e:
                logger.error(f"Database error in delete_event: {e}")
                if session:
                    session.rollback()
                return False
            finally:
                if session:
                    db_service.close_session(session)
        
        if date in self._memory_storage['events'] and isinstance(event_id, int) and event_id < len(self._memory_storage['events'][date]):
            self._memory_storage['events'][date].pop(event_id)
            for i, evt in enumerate(self._memory_storage['events'][date]):
                evt['id'] = i
            self._save_to_file()
            return True
        return False

storage = StorageService()
