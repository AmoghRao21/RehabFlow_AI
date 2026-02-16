"""
RehabFlow AI - Main Application Entry Point
AI-Powered Physiotherapy Management System

Production-grade Gradio application with:
- Modular screen loading
- Concurrency-safe execution
- Async support preparation
- Graceful error handling
- Health monitoring
"""
import sys
import asyncio
import signal
from typing import Optional
from contextlib import asynccontextmanager

import gradio as gr

from utils.logger import get_logger
from utils.config import Config
from ui import (
    create_home_interface,
    create_assessment_interface,
    create_session_interface,
    create_plan_interface,
    create_progress_interface,
    create_report_interface
)
from core.database import db
from core.concurrency import concurrency_manager

# Initialize logger
logger = get_logger(__name__)

# Global app reference for graceful shutdown
_app_instance: Optional[gr.Blocks] = None


class AppLifecycle:
    """Manages application lifecycle and resources."""
    
    def __init__(self):
        self.is_initialized = False
        self.is_running = False
    
    def startup(self) -> None:
        """Initialize application resources."""
        if self.is_initialized:
            logger.warning("Application already initialized")
            return
        
        logger.info("=" * 60)
        logger.info("Starting RehabFlow AI")
        logger.info("=" * 60)
        
        try:
            # Validate configuration
            logger.info("Validating configuration...")
            Config.validate()
            logger.info("✓ Configuration validated")
            
            # Initialize database
            logger.info("Initializing database...")
            db.create_tables()
            logger.info("✓ Database initialized")
            
            # Mark as initialized
            self.is_initialized = True
            logger.info("✓ Application startup complete")
            
        except Exception as e:
            logger.error(f"Startup failed: {e}", exc_info=True)
            raise
    
    def shutdown(self) -> None:
        """Cleanup application resources."""
        if not self.is_initialized:
            return
        
        logger.info("=" * 60)
        logger.info("Shutting down RehabFlow AI")
        logger.info("=" * 60)
        
        try:
            # Close database connections
            logger.info("Closing database connections...")
            db.close()
            logger.info("✓ Database closed")
            
            # Shutdown concurrency manager
            logger.info("Shutting down concurrency manager...")
            concurrency_manager.shutdown(wait=True)
            logger.info("✓ Concurrency manager shut down")
            
            # Mark as not initialized
            self.is_initialized = False
            self.is_running = False
            logger.info("✓ Application shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}", exc_info=True)


# Global lifecycle manager
lifecycle = AppLifecycle()


def create_app() -> gr.Blocks:
    """
    Create the main Gradio application with modular screen loading.
    
    Features:
    - Modular UI components from ui module
    - Blocks API for flexibility
    - Concurrency-safe operations
    - Production-ready error handling
    
    Returns:
        Gradio Blocks application instance
    """
    global _app_instance
    
    logger.info("Creating Gradio application interface...")
    
    # Create main application with Blocks API
    with gr.Blocks(
        title="RehabFlow AI - Physiotherapy Management",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
        ),
        css="""
        .gradio-container {
            max-width: 1400px !important;
            margin: auto;
        }
        .main-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        """,
        analytics_enabled=False,  # Disable analytics for privacy
    ) as app:
        
        # Header
        with gr.Row():
            gr.Markdown(
                """
                <div class="main-header">
                    <h1>🏥 RehabFlow AI</h1>
                    <p>Medical-Grade AI-Powered Physiotherapy Management System</p>
                </div>
                """,
                elem_classes="header"
            )
        
        # Main content tabs - modular screen loading
        with gr.Tabs() as tabs:
            # Home screen
            with gr.Tab("🏠 Home", id="home"):
                logger.debug("Loading Home interface...")
                create_home_interface()
            
            # Assessment screen
            with gr.Tab("📋 Assessment", id="assessment"):
                logger.debug("Loading Assessment interface...")
                create_assessment_interface()
            
            # Treatment Plans screen
            with gr.Tab("📝 Treatment Plans", id="plans"):
                logger.debug("Loading Treatment Plans interface...")
                create_plan_interface()
            
            # Sessions screen
            with gr.Tab("💪 Sessions", id="sessions"):
                logger.debug("Loading Sessions interface...")
                create_session_interface()
            
            # Progress screen
            with gr.Tab("📊 Progress", id="progress"):
                logger.debug("Loading Progress interface...")
                create_progress_interface()
            
            # Reports screen
            with gr.Tab("📄 Reports", id="reports"):
                logger.debug("Loading Reports interface...")
                create_report_interface()
        
        # Footer
        with gr.Row():
            gr.Markdown(
                """
                <div class="footer">
                    <strong>RehabFlow AI v0.1.0</strong><br>
                    Production-Grade Physiotherapy Management | Powered by Google MedGemma<br>
                    <small>Medical-grade security • Thread-safe operations • AI-powered insights</small>
                </div>
                """,
                elem_classes="footer"
            )
    
    _app_instance = app
    logger.info("✓ Gradio application interface created successfully")
    return app


def handle_shutdown(signum, frame):
    """Handle graceful shutdown on signals."""
    logger.info(f"Received shutdown signal ({signum})")
    lifecycle.shutdown()
    sys.exit(0)


async def run_async():
    """
    Async entry point for future async operations.
    Currently wraps synchronous operations.
    """
    logger.info("Running in async mode (preparation for future async features)")
    
    # Run in executor to avoid blocking
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, main)


def main():
    """
    Main application entry point.
    
    Provides:
    - Application lifecycle management
    - Graceful shutdown handling
    - Production-grade error handling
    - Concurrency-safe execution
    """
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        # Startup phase
        lifecycle.startup()
        
        # Create application
        logger.info("Building application interface...")
        app = create_app()
        
        # Launch configuration
        launch_config = {
            "server_name": Config.GRADIO_SERVER_NAME,
            "server_port": Config.GRADIO_SERVER_PORT,
            "share": Config.GRADIO_SHARE,
            "show_error": True,
            "quiet": False,
            "prevent_thread_lock": False,  # For production stability
        }
        
        logger.info(f"Launching Gradio server...")
        logger.info(f"  → Server: {launch_config['server_name']}:{launch_config['server_port']}")
        logger.info(f"  → Share: {launch_config['share']}")
        logger.info(f"  → Max Workers: {Config.MAX_WORKERS}")
        logger.info("=" * 60)
        
        # Mark as running
        lifecycle.is_running = True
        
        # Launch application (blocking)
        app.launch(**launch_config)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
    finally:
        # Shutdown phase
        lifecycle.shutdown()


if __name__ == "__main__":
    main()

