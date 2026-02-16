"""
Session engine for managing physiotherapy sessions.
Handles session lifecycle and progress tracking.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class SessionEngine:
    """Manages physiotherapy session state and execution."""
    
    def __init__(self):
        """Initialize session engine."""
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        logger.info("SessionEngine initialized")
    
    def create_session(
        self, 
        patient_id: str, 
        plan_id: str, 
        session_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new physiotherapy session.
        
        Args:
            patient_id: Patient identifier
            plan_id: Treatment plan identifier
            session_data: Optional session metadata
            
        Returns:
            Session ID
        """
        session_id = f"session_{patient_id}_{datetime.now().timestamp()}"
        
        self.active_sessions[session_id] = {
            "session_id": session_id,
            "patient_id": patient_id,
            "plan_id": plan_id,
            "start_time": datetime.now(),
            "status": "active",
            "data": session_data or {},
            "exercises_completed": [],
            "progress": 0.0
        }
        
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def update_session(
        self, 
        session_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            updates: Dictionary of updates
            
        Returns:
            Success status
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session not found: {session_id}")
            return False
        
        self.active_sessions[session_id].update(updates)
        logger.info(f"Updated session: {session_id}")
        return True
    
    def complete_session(self, session_id: str) -> bool:
        """
        Mark session as completed.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Success status
        """
        if session_id not in self.active_sessions:
            logger.error(f"Session not found: {session_id}")
            return False
        
        self.active_sessions[session_id]["status"] = "completed"
        self.active_sessions[session_id]["end_time"] = datetime.now()
        logger.info(f"Completed session: {session_id}")
        return True
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None
        """
        return self.active_sessions.get(session_id)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all active sessions.
        
        Returns:
            List of active session data
        """
        return [
            session for session in self.active_sessions.values()
            if session["status"] == "active"
        ]


# Global session engine instance
session_engine = SessionEngine()
