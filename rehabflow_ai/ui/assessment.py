"""
Patient assessment UI for RehabFlow AI.
Initial patient evaluation and data collection.
"""
import gradio as gr
from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


def create_assessment_interface() -> gr.Blocks:
    """
    Create patient assessment interface.
    
    Returns:
        Gradio Blocks interface
    """
    logger.info("Creating assessment interface")
    
    with gr.Blocks() as assessment:
        gr.Markdown("# 📋 Patient Assessment")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Patient Information")
                patient_name = gr.Textbox(label="Full Name", placeholder="John Doe")
                patient_age = gr.Number(label="Age", minimum=0, maximum=120)
                patient_gender = gr.Dropdown(
                    label="Gender",
                    choices=["Male", "Female", "Other", "Prefer not to say"]
                )
                
            with gr.Column():
                gr.Markdown("### Medical History")
                medical_history = gr.Textbox(
                    label="Medical History",
                    placeholder="Previous injuries, conditions, surgeries...",
                    lines=5
                )
        
        gr.Markdown("### Current Condition")
        condition = gr.Textbox(
            label="Primary Concern",
            placeholder="Describe the main issue..."
        )
        
        symptoms = gr.CheckboxGroup(
            label="Symptoms",
            choices=[
                "Pain",
                "Stiffness",
                "Limited Range of Motion",
                "Weakness",
                "Swelling",
                "Numbness",
                "Other"
            ]
        )
        
        pain_level = gr.Slider(
            label="Pain Level (0-10)",
            minimum=0,
            maximum=10,
            step=1,
            value=0
        )
        
        with gr.Row():
            submit_btn = gr.Button("Submit Assessment", variant="primary")
            clear_btn = gr.Button("Clear Form")
        
        output = gr.Textbox(label="Assessment Status", interactive=False)
        
        # Event handlers (placeholders)
        submit_btn.click(
            fn=process_assessment,
            inputs=[patient_name, patient_age, condition],
            outputs=output
        )
    
    logger.info("Assessment interface created")
    return assessment


def process_assessment(name: str, age: float, condition: str) -> str:
    """
    Process patient assessment data.
    
    Args:
        name: Patient name
        age: Patient age
        condition: Primary condition
        
    Returns:
        Status message
    """
    logger.info(f"Processing assessment for: {name}")
    return f"Assessment received for {name}. AI analysis pending..."
