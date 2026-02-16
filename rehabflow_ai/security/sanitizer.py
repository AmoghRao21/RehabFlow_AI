"""
Input sanitization for medical data.
Ensures all user inputs are safe and properly formatted.
"""
import re
from typing import Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class Sanitizer:
    """Sanitizes user inputs for security and data integrity."""
    
    def __init__(self):
        """Initialize sanitizer."""
        logger.info("Sanitizer initialized")
    
    def sanitize_text(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitize text input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            logger.warning(f"Non-string input received: {type(text)}")
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>{}]', '', text)
        
        # Trim to max length
        sanitized = sanitized[:max_length]
        
        # Strip whitespace
        sanitized = sanitized.strip()
        
        logger.debug(f"Text sanitized: {len(text)} -> {len(sanitized)} chars")
        return sanitized
    
    def sanitize_number(
        self, 
        value: Any, 
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> Optional[float]:
        """
        Sanitize numeric input.
        
        Args:
            value: Input value
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Sanitized number or None
        """
        try:
            num = float(value)
            
            if min_value is not None and num < min_value:
                logger.warning(f"Value {num} below minimum {min_value}")
                return min_value
            
            if max_value is not None and num > max_value:
                logger.warning(f"Value {num} above maximum {max_value}")
                return max_value
            
            return num
            
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid numeric value: {value} - {e}")
            return None
    
    def sanitize_email(self, email: str) -> Optional[str]:
        """
        Sanitize and validate email address.
        
        Args:
            email: Email address
            
        Returns:
            Sanitized email or None
        """
        if not isinstance(email, str):
            return None
        
        email = email.strip().lower()
        
        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            logger.debug(f"Email sanitized: {email}")
            return email
        
        logger.warning(f"Invalid email format: {email}")
        return None
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file operations.
        
        Args:
            filename: Input filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[/\\:*?"<>|]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        sanitized = sanitized[:255]
        
        logger.debug(f"Filename sanitized: {filename} -> {sanitized}")
        return sanitized
    
    def sanitize_dict(self, data: dict, allowed_keys: list) -> dict:
        """
        Sanitize dictionary by filtering allowed keys.
        
        Args:
            data: Input dictionary
            allowed_keys: List of allowed keys
            
        Returns:
            Filtered dictionary
        """
        if not isinstance(data, dict):
            logger.error("Input is not a dictionary")
            return {}
        
        sanitized = {
            k: v for k, v in data.items() 
            if k in allowed_keys
        }
        
        logger.debug(f"Dict sanitized: {len(data)} -> {len(sanitized)} keys")
        return sanitized


# Global sanitizer instance
sanitizer = Sanitizer()
