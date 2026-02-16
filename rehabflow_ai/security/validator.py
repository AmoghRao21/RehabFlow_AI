"""
Input validation for medical data.
Validates data integrity and business rules.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class Validator:
    """Validates inputs against business rules and constraints."""
    
    def __init__(self):
        """Initialize validator."""
        logger.info("Validator initialized")
    
    def validate_patient_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate patient data.
        
        Args:
            data: Patient data dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        required = ["patient_id", "name", "age"]
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Age validation
        age = data.get("age")
        if age is not None:
            if not isinstance(age, (int, float)) or age < 0 or age > 120:
                errors.append("Age must be between 0 and 120")
        
        is_valid = len(errors) == 0
        logger.info(f"Patient data validation: {'passed' if is_valid else 'failed'}")
        
        return is_valid, errors
    
    def validate_session_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate session data.
        
        Args:
            data: Session data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        required = ["patient_id", "plan_id"]
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        is_valid = len(errors) == 0
        logger.info(f"Session data validation: {'passed' if is_valid else 'failed'}")
        
        return is_valid, errors
    
    def validate_exercise_data(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate exercise data.
        
        Args:
            data: Exercise data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        if "name" not in data or not data["name"]:
            errors.append("Exercise name is required")
        
        # Validate sets and reps
        sets = data.get("sets")
        if sets is not None and (not isinstance(sets, int) or sets < 1 or sets > 100):
            errors.append("Sets must be between 1 and 100")
        
        reps = data.get("reps")
        if reps is not None and (not isinstance(reps, int) or reps < 1 or reps > 1000):
            errors.append("Reps must be between 1 and 1000")
        
        is_valid = len(errors) == 0
        logger.info(f"Exercise validation: {'passed' if is_valid else 'failed'}")
        
        return is_valid, errors
    
    def validate_date_range(
        self, 
        start_date: str, 
        end_date: str
    ) -> tuple[bool, List[str]]:
        """
        Validate date range.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            
            if start > end:
                errors.append("Start date must be before end date")
            
        except ValueError as e:
            errors.append(f"Invalid date format: {e}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_plan(self, plan: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate treatment plan.
        
        Args:
            plan: Plan data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Required fields
        required = ["plan_id", "patient_id", "exercises"]
        for field in required:
            if field not in plan:
                errors.append(f"Missing required field: {field}")
        
        # Validate exercises
        exercises = plan.get("exercises", [])
        if not exercises:
            errors.append("Plan must contain at least one exercise")
        
        for i, exercise in enumerate(exercises):
            ex_valid, ex_errors = self.validate_exercise_data(exercise)
            if not ex_valid:
                errors.extend([f"Exercise {i+1}: {err}" for err in ex_errors])
        
        is_valid = len(errors) == 0
        logger.info(f"Plan validation: {'passed' if is_valid else 'failed'}")
        
        return is_valid, errors


# Global validator instance
validator = Validator()
