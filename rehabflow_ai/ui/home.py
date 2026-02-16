"""
Home screen UI for RehabFlow AI.
Main dashboard and navigation.
"""
import gradio as gr
from utils.logger import get_logger

logger = get_logger(__name__)


def create_home_interface() -> gr.Blocks:
    """
    Create the home screen interface.
    
    Returns:
        Gradio Blocks interface
    """
    logger.info("Creating home interface")
    
    with gr.Blocks() as home:
        gr.Markdown("# 🏥 RehabFlow AI")
        gr.Markdown("### AI-Powered Physiotherapy Management System")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Quick Start")
                gr.Button("📋 New Assessment", variant="primary", size="lg")
                gr.Button("💪 Start Session", size="lg")
                gr.Button("📊 View Progress", size="lg")
            
            with gr.Column():
                gr.Markdown("## Recent Activity")
                gr.Markdown("No recent sessions")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### System Status")
                status_text = gr.Textbox(
                    value="✅ All systems operational",
                    label="Status",
                    interactive=False
                )
            
            with gr.Column():
                gr.Markdown("### Statistics")
                gr.Markdown("- Total Patients: 0")
                gr.Markdown("- Active Plans: 0")
                gr.Markdown("- Sessions Today: 0")
    
    logger.info("Home interface created")
    return home


def get_system_status() -> str:
    """
    Get system status information.
    
    Returns:
        Status string
    """
    return "✅ All systems operational"
