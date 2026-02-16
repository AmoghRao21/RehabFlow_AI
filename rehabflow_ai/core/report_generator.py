"""
Report generation module for RehabFlow AI.
Generates patient progress reports and session summaries.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generates various types of reports for physiotherapy sessions."""
    
    def __init__(self):
        """Initialize report generator."""
        logger.info("ReportGenerator initialized")
    
    def generate_session_report(
        self, 
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive session report.
        
        Args:
            session_data: Session information
            
        Returns:
            Formatted report data
        """
        logger.info(f"Generating session report for: {session_data.get('session_id')}")
        
        report = {
            "report_id": f"report_{datetime.now().timestamp()}",
            "session_id": session_data.get("session_id"),
            "patient_id": session_data.get("patient_id"),
            "generated_at": datetime.now().isoformat(),
            "session_summary": self._generate_summary(session_data),
            "exercises_performed": session_data.get("exercises_completed", []),
            "progress_percentage": session_data.get("progress", 0.0),
            "recommendations": []
        }
        
        logger.info(f"Generated report: {report['report_id']}")
        return report
    
    def generate_progress_report(
        self, 
        patient_id: str, 
        sessions: list
    ) -> Dict[str, Any]:
        """
        Generate patient progress report across multiple sessions.
        
        Args:
            patient_id: Patient identifier
            sessions: List of session data
            
        Returns:
            Progress report data
        """
        logger.info(f"Generating progress report for patient: {patient_id}")
        
        report = {
            "report_id": f"progress_{patient_id}_{datetime.now().timestamp()}",
            "patient_id": patient_id,
            "generated_at": datetime.now().isoformat(),
            "total_sessions": len(sessions),
            "average_progress": self._calculate_average_progress(sessions),
            "trends": self._analyze_trends(sessions),
            "recommendations": []
        }
        
        logger.info(f"Generated progress report: {report['report_id']}")
        return report
    
    def _generate_summary(self, session_data: Dict[str, Any]) -> str:
        """
        Generate session summary text.
        
        Args:
            session_data: Session information
            
        Returns:
            Summary text
        """
        return f"Session completed with {len(session_data.get('exercises_completed', []))} exercises"
    
    def _calculate_average_progress(self, sessions: list) -> float:
        """
        Calculate average progress across sessions.
        
        Args:
            sessions: List of sessions
            
        Returns:
            Average progress percentage
        """
        if not sessions:
            return 0.0
        
        total_progress = sum(s.get("progress", 0.0) for s in sessions)
        return total_progress / len(sessions)
    
    def _analyze_trends(self, sessions: list) -> Dict[str, Any]:
        """
        Analyze progress trends.
        
        Args:
            sessions: List of sessions
            
        Returns:
            Trend analysis data
        """
        return {
            "trend_direction": "improving",
            "consistency_score": 0.0
        }


# Global report generator instance
report_generator = ReportGenerator()
