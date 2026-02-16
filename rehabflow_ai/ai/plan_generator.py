"""
Treatment plan generator using AI.
Creates personalized rehabilitation plans.
"""
from typing import Dict, Any, List, Optional
from ai.medgemma import medgemma_model
from ai.prompt_builder import prompt_builder
from utils.logger import get_logger

logger = get_logger(__name__)


class PlanGenerator:
    """Generates personalized treatment plans using AI."""
    
    def __init__(self):
        """Initialize plan generator."""
        logger.info("PlanGenerator initialized")
    
    def generate_plan(
        self, 
        patient_data: Dict[str, Any],
        assessment: str,
        goals: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive treatment plan.
        
        Args:
            patient_data: Patient information
            assessment: Medical assessment
            goals: Treatment goals
            
        Returns:
            Treatment plan data
        """
        logger.info(f"Generating plan for patient: {patient_data.get('patient_id')}")
        
        # Build prompt
        prompt = prompt_builder.build_plan_generation_prompt(assessment, goals)
        
        # Generate plan using AI
        ai_response = medgemma_model.generate(prompt)
        
        # Structure the plan
        plan = {
            "plan_id": f"plan_{patient_data.get('patient_id')}",
            "patient_id": patient_data.get("patient_id"),
            "assessment": assessment,
            "goals": goals,
            "ai_recommendations": ai_response,
            "exercises": self._extract_exercises(ai_response),
            "schedule": self._create_schedule(),
            "duration_weeks": 8,
            "status": "active"
        }
        
        logger.info(f"Plan generated: {plan['plan_id']}")
        return plan
    
    def update_plan(
        self, 
        plan_id: str, 
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update plan based on progress.
        
        Args:
            plan_id: Plan identifier
            progress_data: Progress information
            
        Returns:
            Updated plan
        """
        logger.info(f"Updating plan: {plan_id}")
        
        # Placeholder for plan update logic
        updated_plan = {
            "plan_id": plan_id,
            "updated": True,
            "modifications": []
        }
        
        return updated_plan
    
    def _extract_exercises(self, ai_response: str) -> List[Dict[str, Any]]:
        """
        Extract exercises from AI response.
        
        Args:
            ai_response: AI generated text
            
        Returns:
            List of exercises
        """
        # Placeholder extraction logic
        return [
            {
                "exercise_id": "ex_001",
                "name": "Exercise 1",
                "sets": 3,
                "reps": 10,
                "instructions": "Placeholder instructions"
            }
        ]
    
    def _create_schedule(self) -> Dict[str, Any]:
        """
        Create exercise schedule.
        
        Returns:
            Schedule information
        """
        return {
            "frequency": "3 times per week",
            "session_duration_minutes": 30,
            "rest_days": ["Sunday"]
        }


# Global plan generator instance
plan_generator = PlanGenerator()
