"""
Production-Grade Supabase Authentication UI for RehabFlow AI

This module provides a complete authentication interface optimized for elderly users.
Supports Login, Registration, and Forgot Password flows using Supabase.

Author: RehabFlow AI Team
"""

import gradio as gr
from typing import Callable, Optional, Dict, Any
import re

# Import Supabase client functions
# Note: supabase_client.py will be implemented by infrastructure team
try:
    from core.supabase_client import sign_up, sign_in, reset_password
except ImportError:
    # Placeholder for development - will be replaced with real implementation
    def sign_up(name: str, age: int, email: str, password: str) -> Dict[str, Any]:
        """Placeholder - will be implemented in core.supabase_client"""
        raise NotImplementedError("Supabase client not yet implemented")
    
    def sign_in(email: str, password: str) -> Dict[str, Any]:
        """Placeholder - will be implemented in core.supabase_client"""
        raise NotImplementedError("Supabase client not yet implemented")
    
    def reset_password(email: str) -> Dict[str, Any]:
        """Placeholder - will be implemented in core.supabase_client"""
        raise NotImplementedError("Supabase client not yet implemented")


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_email(email: str) -> tuple[bool, str]:
    """
    Validates email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email is required"
    
    # Basic email regex pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email.strip()):
        return False, "Please enter a valid email address"
    
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validates password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    return True, ""


def validate_name(name: str) -> tuple[bool, str]:
    """
    Validates name field.
    
    Args:
        name: Name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Name is required"
    
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    return True, ""


def validate_age(age: str) -> tuple[bool, str]:
    """
    Validates age field.
    
    Args:
        age: Age to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not age or not str(age).strip():
        return False, "Age is required"
    
    try:
        age_int = int(age)
        if age_int < 18 or age_int > 120:
            return False, "Age must be between 18 and 120"
        return True, ""
    except ValueError:
        return False, "Please enter a valid age"


# ============================================================================
# AUTHENTICATION HANDLERS
# ============================================================================

def handle_login(email: str, password: str, on_auth_success: Callable) -> str:
    """
    Handles login authentication.
    
    Args:
        email: User email
        password: User password
        on_auth_success: Callback function to call on successful authentication
        
    Returns:
        Status message to display to user
    """
    try:
        # Validate inputs
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return f"❌ {email_error}"
        
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return f"❌ {password_error}"
        
        # Attempt sign in
        user = sign_in(email.strip(), password)
        
        # Call success callback
        if user:
            on_auth_success(user)
            return "✅ Login successful! Redirecting..."
        else:
            return "❌ Login failed. Please check your credentials."
            
    except NotImplementedError:
        return "⚠️ Authentication system is being configured. Please try again soon."
    except Exception as e:
        error_msg = str(e).lower()
        if "invalid" in error_msg or "credentials" in error_msg:
            return "❌ Invalid email or password. Please try again."
        elif "network" in error_msg or "connection" in error_msg:
            return "❌ Connection error. Please check your internet and try again."
        else:
            return f"❌ Login error: {str(e)}"


def handle_register(
    name: str, 
    age: str, 
    email: str, 
    password: str, 
    confirm_password: str
) -> str:
    """
    Handles user registration.
    
    Args:
        name: User's full name
        age: User's age
        email: User's email
        password: User's password
        confirm_password: Password confirmation
        
    Returns:
        Status message to display to user
    """
    try:
        # Validate name
        name_valid, name_error = validate_name(name)
        if not name_valid:
            return f"❌ {name_error}"
        
        # Validate age
        age_valid, age_error = validate_age(age)
        if not age_valid:
            return f"❌ {age_error}"
        
        # Validate email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return f"❌ {email_error}"
        
        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return f"❌ {password_error}"
        
        # Validate password match
        if password != confirm_password:
            return "❌ Passwords do not match. Please try again."
        
        # Attempt registration
        result = sign_up(name.strip(), int(age), email.strip(), password)
        
        if result:
            return "✅ Registration successful! Please login with your credentials."
        else:
            return "❌ Registration failed. Please try again."
            
    except NotImplementedError:
        return "⚠️ Authentication system is being configured. Please try again soon."
    except Exception as e:
        error_msg = str(e).lower()
        if "already exists" in error_msg or "duplicate" in error_msg:
            return "❌ This email is already registered. Please login or use a different email."
        elif "network" in error_msg or "connection" in error_msg:
            return "❌ Connection error. Please check your internet and try again."
        else:
            return f"❌ Registration error: {str(e)}"


def handle_forgot_password(email: str) -> str:
    """
    Handles forgot password request.
    
    Args:
        email: User's email address
        
    Returns:
        Status message to display to user
    """
    try:
        # Validate email
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return f"❌ {email_error}"
        
        # Attempt password reset
        result = reset_password(email.strip())
        
        if result:
            return "✅ Password reset email sent. Please check your inbox."
        else:
            return "❌ Password reset failed. Please try again."
            
    except NotImplementedError:
        return "⚠️ Authentication system is being configured. Please try again soon."
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            return "❌ Email not found. Please check your email or register a new account."
        elif "network" in error_msg or "connection" in error_msg:
            return "❌ Connection error. Please check your internet and try again."
        else:
            return f"❌ Password reset error: {str(e)}"


# ============================================================================
# MAIN AUTHENTICATION UI
# ============================================================================

def render_auth(on_auth_success: Callable[[Dict[str, Any]], None]) -> gr.Blocks:
    """
    Renders the complete authentication UI with Login, Register, and Forgot Password tabs.
    
    Optimized for elderly users with:
    - Large, readable fonts
    - Clear spacing and layout
    - Simple, intuitive navigation
    - Professional medical UI styling
    
    Args:
        on_auth_success: Callback function called when login succeeds.
                        Receives user object as parameter.
    
    Returns:
        Gradio Blocks component containing the full authentication UI
    """
    
    # Custom CSS for elderly-friendly UI
    custom_css = """
    .auth-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .auth-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .auth-subtitle {
        font-size: 1.25rem;
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    .large-input input {
        font-size: 1.25rem !important;
        padding: 1rem !important;
    }
    
    .large-button {
        font-size: 1.5rem !important;
        padding: 1.25rem 2rem !important;
        font-weight: 600 !important;
    }
    
    .status-message {
        font-size: 1.25rem !important;
        padding: 1rem !important;
        text-align: center !important;
        font-weight: 500 !important;
    }
    
    .tab-nav button {
        font-size: 1.25rem !important;
        padding: 1rem !important;
    }
    """
    
    with gr.Blocks(css=custom_css, title="RehabFlow AI - Authentication") as auth_ui:
        
        # Header
        with gr.Row():
            with gr.Column():
                gr.Markdown(
                    "<h1 class='auth-title'>🏥 RehabFlow AI</h1>",
                    elem_classes="auth-title"
                )
                gr.Markdown(
                    "<p class='auth-subtitle'>Your Personal Rehabilitation Companion</p>",
                    elem_classes="auth-subtitle"
                )
        
        # Authentication Tabs
        with gr.Tabs(elem_classes="tab-nav") as tabs:
            
            # ===== LOGIN TAB =====
            with gr.Tab("🔐 Login", id="login"):
                with gr.Column(elem_classes="auth-container"):
                    gr.Markdown("## Welcome Back")
                    gr.Markdown("Please enter your credentials to continue")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            login_email = gr.Textbox(
                                label="Email Address",
                                placeholder="your.email@example.com",
                                type="email",
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            login_password = gr.Textbox(
                                label="Password",
                                placeholder="Enter your password",
                                type="password",
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            login_btn = gr.Button(
                                "Login",
                                variant="primary",
                                size="lg",
                                elem_classes="large-button"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            login_status = gr.Textbox(
                                label="Status",
                                interactive=False,
                                elem_classes="status-message"
                            )
                    
                    # Login button click handler
                    login_btn.click(
                        fn=lambda email, password: handle_login(email, password, on_auth_success),
                        inputs=[login_email, login_password],
                        outputs=login_status
                    )
            
            # ===== REGISTER TAB =====
            with gr.Tab("📝 Register", id="register"):
                with gr.Column(elem_classes="auth-container"):
                    gr.Markdown("## Create New Account")
                    gr.Markdown("Join RehabFlow AI to start your recovery journey")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            register_name = gr.Textbox(
                                label="Full Name",
                                placeholder="Enter your full name",
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            register_age = gr.Number(
                                label="Age",
                                placeholder="Enter your age",
                                minimum=18,
                                maximum=120,
                                precision=0,
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            register_email = gr.Textbox(
                                label="Email Address",
                                placeholder="your.email@example.com",
                                type="email",
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            register_password = gr.Textbox(
                                label="Password",
                                placeholder="Create a password (min. 8 characters)",
                                type="password",
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            register_confirm = gr.Textbox(
                                label="Confirm Password",
                                placeholder="Re-enter your password",
                                type="password",
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            register_btn = gr.Button(
                                "Create Account",
                                variant="primary",
                                size="lg",
                                elem_classes="large-button"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            register_status = gr.Textbox(
                                label="Status",
                                interactive=False,
                                elem_classes="status-message"
                            )
                    
                    # Register button click handler
                    register_btn.click(
                        fn=handle_register,
                        inputs=[
                            register_name,
                            register_age,
                            register_email,
                            register_password,
                            register_confirm
                        ],
                        outputs=register_status
                    )
            
            # ===== FORGOT PASSWORD TAB =====
            with gr.Tab("🔑 Forgot Password", id="forgot"):
                with gr.Column(elem_classes="auth-container"):
                    gr.Markdown("## Reset Your Password")
                    gr.Markdown("Enter your email to receive password reset instructions")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            forgot_email = gr.Textbox(
                                label="Email Address",
                                placeholder="your.email@example.com",
                                type="email",
                                elem_classes="large-input"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            forgot_btn = gr.Button(
                                "Send Reset Email",
                                variant="primary",
                                size="lg",
                                elem_classes="large-button"
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            forgot_status = gr.Textbox(
                                label="Status",
                                interactive=False,
                                elem_classes="status-message"
                            )
                    
                    # Forgot password button click handler
                    forgot_btn.click(
                        fn=handle_forgot_password,
                        inputs=forgot_email,
                        outputs=forgot_status
                    )
        
        # Footer
        with gr.Row():
            with gr.Column():
                gr.Markdown(
                    "<p style='text-align: center; color: #9ca3af; font-size: 1rem; margin-top: 2rem;'>"
                    "🔒 Your data is secure and protected | RehabFlow AI © 2026"
                    "</p>"
                )
    
    return auth_ui


# ============================================================================
# DEMO / TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Demo mode for testing the authentication UI.
    """
    
    def demo_auth_success(user):
        """Demo callback for successful authentication."""
        print(f"✅ Authentication successful for user: {user}")
    
    # Launch the authentication UI
    demo_ui = render_auth(on_auth_success=demo_auth_success)
    demo_ui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
