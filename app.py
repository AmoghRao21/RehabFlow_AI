# ============================================================
# app.py — RehabFlow AI Main Application
# Offline AI-Powered Home Rehabilitation Planner
# MedGemma Impact Challenge 2026
# ============================================================

import os
import gradio as gr
from datetime import datetime
from PIL import Image

from model_utils import load_medgemma, run_medgemma
from prompts import (
    INITIAL_PLAN_SYSTEM_PROMPT,
    INITIAL_PLAN_USER_TEMPLATE,
    PROGRESS_UPDATE_PROMPT,
    PDF_SUMMARY_PROMPT,
    DEMO_PLANS,
)
from utils import (
    save_plan,
    load_plan,
    get_all_plans,
    get_plan_choices,
    add_progress_update,
    save_plan_as_pdf,
    format_all_plans_display,
)


# ── CSS ────────────────────────────────────────────────────────

CUSTOM_CSS = """
/* Root variables */
:root {
    --rehab-blue: #2B6CB0;
    --rehab-blue-light: #EBF4FF;
    --rehab-green: #38A169;
    --rehab-green-light: #F0FFF4;
    --rehab-orange: #DD6B20;
    --rehab-gradient: linear-gradient(135deg, #2B6CB0, #38A169);
}

/* Global overrides */
.gradio-container {
    max-width: 1100px !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

/* Header banner */
.app-header {
    background: linear-gradient(135deg, #1a365d 0%, #2B6CB0 40%, #38A169 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 16px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 24px rgba(43, 108, 176, 0.25);
}
.app-header h1 {
    margin: 0 0 6px 0;
    font-size: 2em;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.app-header p {
    margin: 0;
    opacity: 0.9;
    font-size: 1.05em;
}

/* Disclaimer */
.disclaimer-banner {
    background: linear-gradient(90deg, #FFF5F5, #FFFAF0);
    border: 1px solid #FC8181;
    border-left: 4px solid #E53E3E;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 14px;
    font-size: 0.88em;
    color: #742A2A;
    line-height: 1.5;
}

/* Status badges */
.status-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 600;
    margin: 2px;
}
.badge-demo {
    background: #FEFCBF;
    color: #744210;
    border: 1px solid #ECC94B;
}
.badge-online {
    background: #C6F6D5;
    color: #22543D;
    border: 1px solid #48BB78;
}
.badge-offline {
    background: #FED7E2;
    color: #702459;
    border: 1px solid #ED64A6;
}

/* Tab styling */
.tab-nav button {
    font-weight: 600 !important;
    font-size: 0.95em !important;
    padding: 10px 20px !important;
}
.tab-nav button.selected {
    border-bottom: 3px solid #2B6CB0 !important;
    color: #2B6CB0 !important;
}

/* Cards */
.plan-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.plan-card:hover {
    border-color: #2B6CB0;
    box-shadow: 0 4px 12px rgba(43, 108, 176, 0.12);
}

/* Buttons */
.primary-btn {
    background: linear-gradient(135deg, #2B6CB0, #2C5282) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(43, 108, 176, 0.3) !important;
}
.primary-btn:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(43, 108, 176, 0.4) !important;
}

.success-btn {
    background: linear-gradient(135deg, #38A169, #2F855A) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(56, 161, 105, 0.3) !important;
}

/* Example buttons */
.example-btn {
    background: #EBF4FF !important;
    border: 1px solid #BEE3F8 !important;
    border-radius: 8px !important;
    color: #2B6CB0 !important;
    font-size: 0.85em !important;
    padding: 6px 14px !important;
    transition: all 0.2s ease !important;
}
.example-btn:hover {
    background: #BEE3F8 !important;
    transform: translateY(-1px) !important;
}

/* Plan output */
.plan-output {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 20px;
    background: #FAFCFF;
    max-height: 600px;
    overflow-y: auto;
}

/* Footer */
.app-footer {
    text-align: center;
    padding: 12px;
    color: #A0AEC0;
    font-size: 0.82em;
    margin-top: 10px;
}
"""


# ── Global State ───────────────────────────────────────────────

MODEL_STATE = {"processor": None, "model": None, "loaded": False, "demo_mode": True}

EXAMPLE_INPUTS = {
    "🦵 Knee Osteoarthritis": {
        "patient_name": "Sarah M.",
        "condition": "Knee Osteoarthritis",
        "symptoms": "Bilateral knee pain, worse going down stairs. Morning stiffness ~20 minutes. Crepitus on flexion. Pain increases after walking >15 minutes. Difficulty squatting to pick up objects.",
        "pain_level": 6,
    },
    "🤷 Frozen Shoulder": {
        "patient_name": "James T.",
        "condition": "Frozen Shoulder",
        "symptoms": "Progressive loss of left shoulder range of motion over 3 months. Cannot reach overhead or behind back. Night pain disrupting sleep. Pain at end-range external rotation. Difficulty dressing and reaching for seatbelt.",
        "pain_level": 7,
    },
    "🔙 Lumbar Disc Herniation": {
        "patient_name": "Priya K.",
        "condition": "Lumbar Disc Herniation",
        "symptoms": "Lower back pain radiating to left buttock and posterior thigh. Worse with sitting >20 min and forward bending. Pain centralizes with extension. Coughing/sneezing increases symptoms. No below-knee symptoms.",
        "pain_level": 7,
    },
    "🏃 Post-ACL Reconstruction": {
        "patient_name": "David R.",
        "condition": "Post-ACL Reconstruction",
        "symptoms": "Week 6 post-op ACL reconstruction (hamstring autograft). Knee stiffness, 5° extension deficit, flexion to 110°. Significant quad weakness and atrophy. Antalgic gait. Cleared for closed-chain exercises by surgeon.",
        "pain_level": 4,
    },
}

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "examples")


# ── Helper Functions ───────────────────────────────────────────


def get_status_html():
    """Return status badge HTML based on model state."""
    if MODEL_STATE["loaded"]:
        return '<span class="status-badge badge-online">🟢 MedGemma Loaded</span>'
    else:
        return '<span class="status-badge badge-demo">🟡 Demo Mode — Using Sample Plans</span>'


def try_load_model(progress=gr.Progress()):
    """Attempt to load MedGemma. Returns status message."""
    if MODEL_STATE["loaded"]:
        return "✅ Model already loaded!", get_status_html()
    
    progress(0.1, desc="Initializing MedGemma 1.5-4b-it...")
    processor, model = load_medgemma()
    
    if processor is not None and model is not None:
        MODEL_STATE["processor"] = processor
        MODEL_STATE["model"] = model
        MODEL_STATE["loaded"] = True
        MODEL_STATE["demo_mode"] = False
        progress(1.0, desc="Model loaded!")
        return "✅ MedGemma loaded successfully! GPU inference ready.", get_status_html()
    else:
        MODEL_STATE["demo_mode"] = True
        progress(1.0, desc="Using demo mode")
        return "⚠️ Model not available. Using Demo Mode with pre-built plans.", get_status_html()


def generate_plan(patient_name, condition, symptoms, pain_level, image, progress=gr.Progress()):
    """Generate a rehab plan using MedGemma or demo mode."""
    if not condition or not symptoms:
        return "❌ Please fill in at least the **Condition** and **Symptoms** fields.", gr.update()

    patient_name = patient_name or "Anonymous"
    progress(0.1, desc="Preparing clinical assessment...")

    # Build the prompt
    image_description = "Patient uploaded a clinical image for visual assessment." if image else "No image provided"
    
    user_prompt = INITIAL_PLAN_USER_TEMPLATE.format(
        patient_name=patient_name,
        condition=condition,
        symptoms=symptoms,
        pain_level=int(pain_level),
        image_description=image_description,
    )
    full_prompt = INITIAL_PLAN_SYSTEM_PROMPT + "\n\n" + user_prompt

    # Try model inference
    plan_text = None
    if MODEL_STATE["loaded"] and not MODEL_STATE["demo_mode"]:
        progress(0.3, desc="Running MedGemma inference (this may take 30-60s)...")
        pil_image = Image.open(image) if image else None
        plan_text = run_medgemma(
            MODEL_STATE["processor"],
            MODEL_STATE["model"],
            full_prompt,
            image=pil_image,
            max_tokens=1200,
        )

    # Fallback to demo plans
    if plan_text is None:
        progress(0.5, desc="Using demo mode...")
        # Find closest matching demo plan
        condition_lower = condition.lower()
        plan_text = None
        for key, demo in DEMO_PLANS.items():
            if any(word in condition_lower for word in key.lower().split()):
                plan_text = demo
                break
        if plan_text is None:
            # Default to most common
            plan_text = list(DEMO_PLANS.values())[0]
        plan_text = f"> 🟡 **Demo Mode** — This plan was generated from pre-built templates.\n> Load MedGemma for personalized AI-generated plans.\n\n{plan_text}"

    progress(0.9, desc="Formatting plan...")

    # Store in session for saving
    plan_dict = {
        "patient_name": patient_name,
        "condition": condition,
        "symptoms": symptoms,
        "pain_level": int(pain_level),
        "plan_text": plan_text,
        "created_at": datetime.now().isoformat(),
        "has_image": image is not None,
    }

    progress(1.0, desc="Plan ready!")
    return plan_text, plan_dict


def save_current_plan(plan_dict):
    """Save the currently displayed plan."""
    if not plan_dict:
        return "❌ No plan to save. Generate a plan first.", gr.update()
    
    plan_id = save_plan(plan_dict)
    choices = get_plan_choices()
    return f"✅ Plan saved! ID: `{plan_id}`", gr.update(choices=choices)


def update_plan_with_progress(plan_id, today_pain, progress_notes, voice_input, progress=gr.Progress()):
    """Adapt a plan based on daily progress check-in."""
    if not plan_id:
        return "❌ Please select a saved plan first."

    plan = load_plan(plan_id)
    if plan is None:
        return "❌ Plan not found."

    # Combine voice + text notes
    notes = progress_notes or ""
    if voice_input:
        try:
            import whisper
            whisper_model = whisper.load_model("tiny")
            result = whisper_model.transcribe(voice_input)
            voice_text = result.get("text", "")
            notes = f"{notes}\n[Voice note]: {voice_text}".strip()
        except Exception as e:
            notes = f"{notes}\n[Voice input could not be transcribed: {e}]".strip()

    if not notes:
        notes = "No specific notes provided."

    progress(0.2, desc="Analyzing progress...")

    # Calculate days elapsed
    try:
        created = datetime.fromisoformat(plan["created_at"])
        days = (datetime.now() - created).days
    except (ValueError, KeyError):
        days = len(plan.get("updates", [])) + 1

    update_prompt = PROGRESS_UPDATE_PROMPT.format(
        current_plan_summary=plan.get("plan_text", "")[:1500],
        today_pain=int(today_pain),
        original_pain=plan.get("pain_level", "?"),
        progress_notes=notes,
        days_elapsed=days,
    )

    # Try model inference
    updated_text = None
    if MODEL_STATE["loaded"] and not MODEL_STATE["demo_mode"]:
        progress(0.4, desc="Running MedGemma inference...")
        updated_text = run_medgemma(
            MODEL_STATE["processor"],
            MODEL_STATE["model"],
            INITIAL_PLAN_SYSTEM_PROMPT + "\n\n" + update_prompt,
            max_tokens=1000,
        )

    if updated_text is None:
        progress(0.6, desc="Generating demo update...")
        pain_diff = int(today_pain) - plan.get("pain_level", 5)
        if pain_diff < -1:
            assessment = "Great progress! Pain has decreased significantly."
            adjustment = "Progress to next difficulty level. Increase reps by 2 per set."
        elif pain_diff > 1:
            assessment = "Pain has increased. We need to regress the program."
            adjustment = "Reduce intensity. Drop back to previous week's exercises. Add more rest days."
        else:
            assessment = "Steady progress. Pain levels are stable."
            adjustment = "Maintain current program. Focus on form quality."

        updated_text = f"""> 🟡 **Demo Mode** — Progress update generated from templates.

#### 📊 Progress Assessment
{assessment}
- **Original Pain:** {plan.get('pain_level', '?')}/10
- **Today's Pain:** {int(today_pain)}/10
- **Days Elapsed:** {days}
- **Patient Notes:** {notes}

#### 🔄 Plan Adjustments
{adjustment}

| Change | Previous | Updated | Reason |
|--------|----------|---------|--------|
| Intensity | Current level | {'Decreased' if pain_diff > 1 else 'Increased' if pain_diff < -1 else 'Maintained'} | Pain {'increased' if pain_diff > 1 else 'decreased' if pain_diff < -1 else 'stable'} |
| Rest days | As prescribed | {'Add 1 extra' if pain_diff > 1 else 'Can reduce by 1' if pain_diff < -2 else 'Keep same'} | Based on recovery |

#### ⚠️ Watch For
- Pain exceeding 7/10 during any exercise
- New symptoms (numbness, tingling, weakness)
- Swelling that doesn't resolve within 24 hours

#### 💬 Patient Guidance
{'Take it easy — your body needs more time to adapt. Focus on pain-free movements only.' if pain_diff > 1 else 'Excellent work! Your body is responding well. Keep up the consistency.' if pain_diff < -1 else 'You are on track. Stay consistent with your exercises and tracking.'}

#### ⚕️ Disclaimer
> This adaptation is AI-generated for educational purposes only. Consult your healthcare provider before making changes to your rehabilitation program.
"""

    # Save the update
    add_progress_update(plan_id, {
        "pain_level": int(today_pain),
        "notes": notes,
        "updated_plan": updated_text,
    })

    progress(1.0, desc="Update complete!")
    return updated_text


def view_plan_detail(plan_id):
    """Load and display a plan's full details."""
    if not plan_id:
        return "Select a plan to view details.", None
    plan = load_plan(plan_id)
    if plan is None:
        return "Plan not found.", None
    
    # Format with metadata header
    header = f"""## 📋 {plan.get('condition', 'Rehabilitation Plan')}
**Patient:** {plan.get('patient_name', 'Anonymous')} · **Created:** {plan.get('created_at', '')[:10]} · **Initial Pain:** {plan.get('pain_level', '?')}/10
**Updates:** {len(plan.get('updates', []))}

---

"""
    full_text = header + plan.get("plan_text", "No plan content.")

    # Show updates if any
    updates = plan.get("updates", [])
    if updates:
        full_text += "\n\n---\n\n## 📝 Progress Updates\n"
        for i, u in enumerate(updates, 1):
            full_text += f"\n### Update {i} — {u.get('timestamp', '')[:10]} (Pain: {u.get('pain_level', '?')}/10)\n"
            full_text += u.get("updated_plan", u.get("notes", "")) + "\n"

    return full_text, plan


def download_pdf(plan_dict):
    """Generate and return PDF for download."""
    if not plan_dict:
        return None
    try:
        path = save_plan_as_pdf(plan_dict)
        return path
    except Exception as e:
        print(f"[RehabFlow] PDF error: {e}")
        return None


def refresh_plans_list():
    """Refresh the plans display and dropdown."""
    display = format_all_plans_display()
    choices = get_plan_choices()
    return display, gr.update(choices=choices)


def fill_example(example_name):
    """Auto-fill form with example data."""
    data = EXAMPLE_INPUTS.get(example_name, {})
    # Try to load corresponding example image
    condition_to_image = {
        "🦵 Knee Osteoarthritis": "knee_pain.jpg",
        "🤷 Frozen Shoulder": "shoulder_impingement.jpg",
        "🔙 Lumbar Disc Herniation": "low_back_pain.jpg",
        "🏃 Post-ACL Reconstruction": "post_acl.jpg",
    }
    img_path = os.path.join(ASSETS_DIR, condition_to_image.get(example_name, ""))
    img = img_path if os.path.exists(img_path) else None
    
    return (
        data.get("patient_name", ""),
        data.get("condition", ""),
        data.get("symptoms", ""),
        data.get("pain_level", 5),
        img,
    )


# ── Build UI ───────────────────────────────────────────────────

def create_app():
    with gr.Blocks(
        theme=gr.themes.Soft(
            primary_hue=gr.themes.colors.blue,
            secondary_hue=gr.themes.colors.green,
            neutral_hue=gr.themes.colors.gray,
            font=gr.themes.GoogleFont("Inter"),
        ),
        css=CUSTOM_CSS,
        title="RehabFlow AI — Home Rehabilitation Planner",
    ) as app:

        # -- Session state
        current_plan_state = gr.State(value=None)
        viewing_plan_state = gr.State(value=None)

        # -- Header
        gr.HTML("""
        <div class="app-header">
            <h1>🏥 RehabFlow AI</h1>
            <p>Offline AI-Powered Home Rehabilitation Planner for Musculoskeletal Conditions</p>
            <p style="font-size: 0.85em; opacity: 0.75; margin-top: 6px;">Powered by MedGemma 1.5-4b-it · Built for the MedGemma Impact Challenge</p>
        </div>
        """)

        # -- Status row
        with gr.Row():
            with gr.Column(scale=3):
                status_html = gr.HTML(value=get_status_html())
            with gr.Column(scale=1, min_width=200):
                load_model_btn = gr.Button("🚀 Load MedGemma", elem_classes=["primary-btn"], size="sm")
            with gr.Column(scale=1, min_width=200):
                model_status_text = gr.Textbox(
                    value="Demo Mode active" if MODEL_STATE["demo_mode"] else "Model loaded",
                    label="Status",
                    interactive=False,
                    max_lines=1,
                )

        load_model_btn.click(
            fn=try_load_model,
            outputs=[model_status_text, status_html],
        )

        # -- Tabs
        with gr.Tabs() as tabs:

            # =====================================================
            # TAB 1: Create New Rehab Plan
            # =====================================================
            with gr.Tab("🩺 Create New Plan", id="create_plan"):
                gr.HTML("""<div class="disclaimer-banner">
                    <strong>⚕️ Medical Disclaimer:</strong> This tool generates exercise plans for 
                    <strong>educational purposes only</strong>. It is NOT a substitute for professional 
                    medical advice, diagnosis, or treatment. Always consult a qualified healthcare 
                    provider before starting any rehabilitation program. If you experience severe pain 
                    or concerning symptoms, seek immediate medical attention.
                </div>""")

                # Example buttons row
                gr.Markdown("### ⚡ Quick Start — Load an Example Case")
                with gr.Row():
                    ex_btn_knee = gr.Button("🦵 Knee Osteoarthritis", elem_classes=["example-btn"], size="sm")
                    ex_btn_shoulder = gr.Button("🤷 Frozen Shoulder", elem_classes=["example-btn"], size="sm")
                    ex_btn_back = gr.Button("🔙 Lumbar Disc Herniation", elem_classes=["example-btn"], size="sm")
                    ex_btn_acl = gr.Button("🏃 Post-ACL Reconstruction", elem_classes=["example-btn"], size="sm")

                gr.Markdown("---")

                with gr.Row():
                    with gr.Column(scale=1):
                        patient_name = gr.Textbox(
                            label="Patient Name (optional)",
                            placeholder="e.g., Sarah M.",
                            max_lines=1,
                        )
                        condition = gr.Dropdown(
                            label="Condition",
                            choices=[
                                "Knee Osteoarthritis",
                                "Frozen Shoulder",
                                "Lumbar Disc Herniation",
                                "Post-ACL Reconstruction",
                                "Rotator Cuff Tendinopathy",
                                "Plantar Fasciitis",
                                "Tennis Elbow",
                                "Ankle Sprain (Grade I-II)",
                                "Cervical Spondylosis",
                                "Hip Bursitis",
                            ],
                            allow_custom_value=True,
                            info="Select from common conditions or type your own",
                        )
                        symptoms = gr.Textbox(
                            label="Symptoms & History",
                            placeholder="Describe your symptoms in detail: location, duration, what makes it better/worse, previous treatments...",
                            lines=5,
                        )
                        pain_level = gr.Slider(
                            label="Current Pain Level",
                            minimum=0,
                            maximum=10,
                            step=1,
                            value=5,
                            info="0 = No pain · 10 = Worst pain imaginable",
                        )

                    with gr.Column(scale=1):
                        image_upload = gr.Image(
                            label="Upload Image (optional)",
                            type="filepath",
                            height=250,
                        )
                        gr.Markdown(
                            "*Upload a photo of the affected area for visual assessment. "
                            "This helps the AI provide more specific guidance.*"
                        )
                        with gr.Row():
                            generate_btn = gr.Button(
                                "🧠 Generate Rehab Plan",
                                variant="primary",
                                elem_classes=["primary-btn"],
                                size="lg",
                            )
                            save_btn = gr.Button(
                                "💾 Save Plan",
                                variant="secondary",
                                elem_classes=["success-btn"],
                                size="lg",
                            )
                        save_status = gr.Markdown("")

                gr.Markdown("### 📋 Your Personalized Rehabilitation Plan")
                plan_output = gr.Markdown(
                    value="*Your AI-generated rehabilitation plan will appear here after you click **Generate Rehab Plan**.*",
                    elem_classes=["plan-output"],
                )

                # Wire example buttons
                example_outputs = [patient_name, condition, symptoms, pain_level, image_upload]
                ex_btn_knee.click(fn=fill_example, inputs=[gr.State("🦵 Knee Osteoarthritis")], outputs=example_outputs)
                ex_btn_shoulder.click(fn=fill_example, inputs=[gr.State("🤷 Frozen Shoulder")], outputs=example_outputs)
                ex_btn_back.click(fn=fill_example, inputs=[gr.State("🔙 Lumbar Disc Herniation")], outputs=example_outputs)
                ex_btn_acl.click(fn=fill_example, inputs=[gr.State("🏃 Post-ACL Reconstruction")], outputs=example_outputs)

                # Wire generate
                generate_btn.click(
                    fn=generate_plan,
                    inputs=[patient_name, condition, symptoms, pain_level, image_upload],
                    outputs=[plan_output, current_plan_state],
                )

                # Wire save
                save_btn.click(
                    fn=save_current_plan,
                    inputs=[current_plan_state],
                    outputs=[save_status, gr.State()],  # dummy state for choices update
                )

            # =====================================================
            # TAB 2: Log Daily Progress
            # =====================================================
            with gr.Tab("📊 Log Daily Progress", id="progress"):
                gr.HTML("""<div class="disclaimer-banner">
                    <strong>⚕️ Medical Disclaimer:</strong> Progress tracking is for educational purposes only. 
                    Any AI-generated modifications to your plan should be reviewed by a healthcare professional.
                    Stop exercises immediately if you experience sudden severe pain.
                </div>""")

                with gr.Row():
                    with gr.Column(scale=1):
                        progress_plan_dropdown = gr.Dropdown(
                            label="Select Your Plan",
                            choices=get_plan_choices(),
                            info="Choose a saved plan to update",
                        )
                        refresh_btn = gr.Button("🔄 Refresh Plans List", size="sm")
                        today_pain = gr.Slider(
                            label="Today's Pain Level",
                            minimum=0,
                            maximum=10,
                            step=1,
                            value=5,
                            info="How does your pain feel today?",
                        )
                        progress_notes = gr.Textbox(
                            label="How are you feeling? (Text)",
                            placeholder="Describe any changes, improvements, or concerns...",
                            lines=4,
                        )
                        voice_input = gr.Audio(
                            label="Or record a voice note 🎙️",
                            sources=["microphone"],
                            type="filepath",
                        )
                        update_btn = gr.Button(
                            "🔄 Update My Plan",
                            variant="primary",
                            elem_classes=["primary-btn"],
                            size="lg",
                        )

                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Updated Rehabilitation Plan")
                        progress_output = gr.Markdown(
                            value="*Your adapted plan will appear here after you submit a progress update.*",
                            elem_classes=["plan-output"],
                        )

                # Wire refresh
                def refresh_dropdown():
                    return gr.update(choices=get_plan_choices())
                
                refresh_btn.click(fn=refresh_dropdown, outputs=[progress_plan_dropdown])

                # Wire update
                update_btn.click(
                    fn=update_plan_with_progress,
                    inputs=[progress_plan_dropdown, today_pain, progress_notes, voice_input],
                    outputs=[progress_output],
                )

            # =====================================================
            # TAB 3: My Plans
            # =====================================================
            with gr.Tab("📚 My Plans", id="my_plans"):
                gr.HTML("""<div class="disclaimer-banner">
                    <strong>⚕️ Medical Disclaimer:</strong> Saved plans are for reference only. 
                    Always consult your healthcare provider before following any rehabilitation program.
                </div>""")

                with gr.Row():
                    refresh_plans_btn = gr.Button("🔄 Refresh", size="sm")
                    download_pdf_btn = gr.Button("📄 Download PDF", elem_classes=["success-btn"], size="sm")

                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Saved Plans")
                        plans_display = gr.Markdown(
                            value=format_all_plans_display(),
                        )
                        plan_selector = gr.Dropdown(
                            label="Select Plan to View",
                            choices=get_plan_choices(),
                        )

                    with gr.Column(scale=2):
                        gr.Markdown("### Plan Details")
                        plan_detail_view = gr.Markdown(
                            value="*Select a plan from the left to view its full details.*",
                            elem_classes=["plan-output"],
                        )

                pdf_download = gr.File(label="Download", visible=True)

                # Wire events
                refresh_plans_btn.click(
                    fn=refresh_plans_list,
                    outputs=[plans_display, plan_selector],
                )

                plan_selector.change(
                    fn=view_plan_detail,
                    inputs=[plan_selector],
                    outputs=[plan_detail_view, viewing_plan_state],
                )

                download_pdf_btn.click(
                    fn=download_pdf,
                    inputs=[viewing_plan_state],
                    outputs=[pdf_download],
                )

        # -- Footer
        gr.HTML("""
        <div class="app-footer">
            <strong>RehabFlow AI</strong> · Built for the MedGemma Impact Challenge · 
            Powered by MedGemma 1.5-4b-it · Not for clinical use<br>
            © 2026 · Made with ❤️ for accessible rehabilitation
        </div>
        """)

    return app


# ── Launch ─────────────────────────────────────────────────────

if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
