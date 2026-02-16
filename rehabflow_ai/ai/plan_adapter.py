"""
Plan adapter for converting AI-generated plans to structured format.
Ensures consistency and validation of treatment plans.
"""
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class PlanAdapter:
    """Adapts and validates AI-generated plans."""
    
    def __init__(self):
        """Initialize plan adapter."""
        logger.info("PlanAdapter initialized")
    
    def adapt_plan(self, raw_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt raw AI plan to standardized format.
        
        Args:
            raw_plan: Raw plan data from AI
            
        Returns:
            Standardized plan
        """
        logger.info("Adapting plan to standard format")
        
        adapted = {
            "plan_id": raw_plan.get("plan_id"),
            "patient_id": raw_plan.get("patient_id"),
            "exercises": self._standardize_exercises(
                raw_plan.get("exercises", [])
            ),
            "schedule": self._standardize_schedule(
                raw_plan.get("schedule", {})
            ),
            "goals": raw_plan.get("goals", []),
            "metadata": {
                "created_from": "ai_generation",
                "version": "1.0"
            }
        }
        
        logger.info(f"Plan adapted: {adapted['plan_id']}")
        return adapted
    
    def validate_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Validate plan structure and content.
        
        Args:
            plan: Plan to validate
            
        Returns:
            Validation status
        """
        logger.info(f"Validating plan: {plan.get('plan_id')}")
        
        required_fields = ["plan_id", "patient_id", "exercises", "schedule"]
        
        for field in required_fields:
            if field not in plan:
                logger.error(f"Missing required field: {field}")
                return False
        
        if not plan.get("exercises"):
            logger.error("Plan must contain at least one exercise")
            return False
        
        logger.info("Plan validation successful")
        return True
    
    def merge_plans(
        self, 
        base_plan: Dict[str, Any], 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge plan updates with base plan.
        
        Args:
            base_plan: Original plan
            updates: Plan updates
            
        Returns:
            Merged plan
        """
        logger.info("Merging plan updates")
        
        merged = base_plan.copy()
        merged.update(updates)
        
        return merged
    
    def _standardize_exercises(
        self, 
        exercises: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Standardize exercise format.
        
        Args:
            exercises: Raw exercise data
            
        Returns:
            Standardized exercises
        """
        standardized = []
        
        for ex in exercises:
            standardized.append({
                "exercise_id": ex.get("exercise_id", ""),
                "name": ex.get("name", ""),
                "sets": ex.get("sets", 3),
                "reps": ex.get("reps", 10),
                "duration_seconds": ex.get("duration_seconds", 0),
                "instructions": ex.get("instructions", ""),
                "difficulty": ex.get("difficulty", "beginner")
            })
        
        return standardized
    
    def _standardize_schedule(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize schedule format.
        
        Args:
            schedule: Raw schedule data
            
        Returns:
            Standardized schedule
        """
        return {
            "frequency": schedule.get("frequency", "3 times per week"),
            "session_duration_minutes": schedule.get("session_duration_minutes", 30),
            "rest_days": schedule.get("rest_days", []),
            "start_date": schedule.get("start_date", ""),
            "end_date": schedule.get("end_date", "")
        }


# Global plan adapter instance
plan_adapter = PlanAdapter()
