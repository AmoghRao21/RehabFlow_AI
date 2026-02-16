"""
Prompt builder for constructing medical prompts for MedGemma.
Formats patient data and context into proper prompts.
"""
from typing import Dict, Any, Optional, List
from utils.logger import get_logger

logger = get_logger(__name__)


class PromptBuilder:
    """Constructs structured prompts for medical AI model."""
    
    def __init__(self):
        """Initialize prompt builder."""
        logger.info("PromptBuilder initialized")
    
    def build_assessment_prompt(
        self, 
        patient_data: Dict[str, Any],
        symptoms: List[str]
    ) -> str:
        """
        Build prompt for patient assessment.
        
        Args:
            patient_data: Patient information
            symptoms: List of symptoms
            
        Returns:
            Formatted prompt
        """
        logger.info("Building assessment prompt")
        
        prompt = f"""As a medical AI assistant specializing in physiotherapy, 
please assess the following patient:

Patient Information:
- Age: {patient_data.get('age', 'N/A')}
- Gender: {patient_data.get('gender', 'N/A')}
- Medical History: {patient_data.get('medical_history', 'None provided')}

Reported Symptoms:
{self._format_list(symptoms)}

Please provide:
1. Initial assessment
2. Recommended exercises
3. Precautions
"""
        return prompt.strip()
    
    def build_plan_generation_prompt(
        self, 
        assessment: str,
        patient_goals: List[str]
    ) -> str:
        """
        Build prompt for treatment plan generation.
        
        Args:
            assessment: Initial assessment
            patient_goals: Patient's rehabilitation goals
            
        Returns:
            Formatted prompt
        """
        logger.info("Building plan generation prompt")
        
        prompt = f"""Based on the following assessment, generate a personalized 
physiotherapy treatment plan:

Assessment:
{assessment}

Patient Goals:
{self._format_list(patient_goals)}

Please provide a structured treatment plan including:
1. Exercise program
2. Frequency and duration
3. Progress milestones
4. Expected outcomes
"""
        return prompt.strip()
    
    def build_progress_analysis_prompt(
        self, 
        session_history: List[Dict[str, Any]]
    ) -> str:
        """
        Build prompt for progress analysis.
        
        Args:
            session_history: List of previous sessions
            
        Returns:
            Formatted prompt
        """
        logger.info("Building progress analysis prompt")
        
        prompt = f"""Analyze the patient's progress based on the following session history:

Number of sessions completed: {len(session_history)}

Session Summary:
{self._format_session_history(session_history)}

Please provide:
1. Progress assessment
2. Areas of improvement
3. Recommendations for next steps
"""
        return prompt.strip()
    
    def build_exercise_recommendation_prompt(
        self, 
        condition: str,
        difficulty_level: str = "beginner"
    ) -> str:
        """
        Build prompt for exercise recommendations.
        
        Args:
            condition: Medical condition
            difficulty_level: Exercise difficulty
            
        Returns:
            Formatted prompt
        """
        logger.info(f"Building exercise prompt for {condition}")
        
        prompt = f"""Recommend appropriate physiotherapy exercises for:

Condition: {condition}
Difficulty Level: {difficulty_level}

Please provide:
1. List of safe and effective exercises
2. Instructions for each exercise
3. Sets and repetitions
4. Safety precautions
"""
        return prompt.strip()
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items with bullets."""
        return "\n".join([f"- {item}" for item in items])
    
    def _format_session_history(self, sessions: List[Dict[str, Any]]) -> str:
        """Format session history."""
        if not sessions:
            return "No sessions recorded"
        
        formatted = []
        for i, session in enumerate(sessions, 1):
            formatted.append(f"Session {i}: {session.get('summary', 'No summary')}")
        
        return "\n".join(formatted)


# Global prompt builder instance
prompt_builder = PromptBuilder()
