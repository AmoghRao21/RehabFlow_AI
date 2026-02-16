# ============================================================
# utils.py — PDF Export, Plan Storage, and Helpers
# RehabFlow AI — MedGemma Impact Challenge 2026
# ============================================================

import json
import os
import re
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

PLANS_DIR = Path(__file__).parent / "plans"
PLANS_DIR.mkdir(exist_ok=True)


# ── PDF Generation ─────────────────────────────────────────────


class RehabPDF(FPDF):
    """Custom PDF with professional medical styling."""

    def header(self):
        # Teal header bar
        self.set_fill_color(43, 108, 176)  # #2B6CB0
        self.rect(0, 0, 210, 20, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 12, _strip_to_latin1("RehabFlow AI -- Rehabilitation Plan"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(220, 230, 255)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 6, "AI-Generated - For Educational Use Only - Not Medical Advice", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}  |  Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  rehabflow-ai", align="C")

    def chapter_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(43, 108, 176)
        self.cell(0, 10, _strip_to_latin1(title), new_x="LMARGIN", new_y="NEXT")
        # Underline
        self.set_draw_color(56, 161, 105)
        self.line(self.l_margin, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, _strip_to_latin1(text))
        self.ln(2)

    def warning_box(self, text: str):
        self.set_fill_color(255, 243, 224)
        self.set_draw_color(221, 107, 32)
        x = self.get_x()
        y = self.get_y()
        self.rect(x, y, 190, 18, "DF")
        self.set_xy(x + 3, y + 2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(180, 80, 0)
        self.cell(0, 5, "(!!) IMPORTANT DISCLAIMER", new_x="LMARGIN", new_y="NEXT")
        self.set_x(x + 3)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 70, 0)
        self.multi_cell(184, 4, _strip_to_latin1(text))
        self.ln(5)


def _strip_to_latin1(text: str) -> str:
    """Remove all characters that can't be encoded in latin-1 (required by built-in PDF fonts)."""
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        "\u2014": "--", "\u2013": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u2022": "*",
        "\u2265": ">=", "\u2264": "<=", "\u00b0": " degrees",
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Strip everything outside latin-1 range
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def _clean_markdown_for_pdf(text: str) -> str:
    """Strip markdown formatting for plain-text PDF rendering."""
    # Remove blockquote markers
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    # Remove headers (##, ###, etc.)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    # Remove all emoji and non-ASCII symbols
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    # Remove markdown table pipes and alignment dashes
    text = re.sub(r"\|?-{3,}\|?", "", text)
    # Clean up extra whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def save_plan_as_pdf(plan_dict: dict, filename: str = None) -> str:
    """
    Generate a professional PDF from a plan dictionary.
    
    Args:
        plan_dict: Must contain 'condition', 'plan_text', and optionally
                   'patient_name', 'pain_level', 'created_at'.
        filename: Optional override for the output filename.
    
    Returns:
        Absolute path to the generated PDF file.
    """
    if filename is None:
        safe_name = re.sub(r"[^\w\-]", "_", plan_dict.get("condition", "plan"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"RehabPlan_{safe_name}_{timestamp}.pdf"

    filepath = PLANS_DIR / filename
    pdf = RehabPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Patient info box
    pdf.set_fill_color(240, 247, 255)
    pdf.set_draw_color(43, 108, 176)
    y_start = pdf.get_y()
    pdf.rect(10, y_start, 190, 22, "DF")
    pdf.set_xy(15, y_start + 2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(43, 108, 176)
    patient = _strip_to_latin1(plan_dict.get("patient_name", "Anonymous"))
    pdf.cell(90, 6, f"Patient: {patient}", new_x="RIGHT")
    pdf.cell(90, 6, f"Pain Level: {plan_dict.get('pain_level', 'N/A')}/10", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(15)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    condition = _strip_to_latin1(plan_dict.get("condition", "N/A"))
    pdf.cell(90, 6, f"Condition: {condition}", new_x="RIGHT")
    created = _strip_to_latin1(plan_dict.get("created_at", datetime.now().strftime("%Y-%m-%d"))[:16])
    pdf.cell(90, 6, f"Created: {created}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # Disclaimer
    pdf.warning_box(
        "This plan is AI-generated for educational purposes only. "
        "It is NOT a substitute for professional medical advice. "
        "Consult a qualified healthcare provider before starting any rehabilitation program."
    )

    # Plan content
    plan_text = plan_dict.get("plan_text", "No plan content available.")
    cleaned = _clean_markdown_for_pdf(plan_text)

    # Split into sections by heading-like lines
    sections = re.split(r"\n(?=[A-Z][\w\s&]+\n|[A-Z][\w\s&:]+$)", cleaned, flags=re.MULTILINE)

    for section in sections:
        lines = section.strip().split("\n", 1)
        if len(lines) == 2 and len(lines[0]) < 60:
            pdf.chapter_title(lines[0].strip())
            pdf.body_text(lines[1].strip())
        elif section.strip():
            pdf.body_text(section.strip())

    pdf.output(str(filepath))
    return str(filepath.absolute())


# ── Plan Storage (JSON) ────────────────────────────────────────


def save_plan(plan_dict: dict) -> str:
    """Save a plan to disk as JSON. Returns the plan ID."""
    plan_id = plan_dict.get("id", datetime.now().strftime("%Y%m%d_%H%M%S"))
    plan_dict["id"] = plan_id
    plan_dict.setdefault("created_at", datetime.now().isoformat())
    plan_dict.setdefault("updates", [])

    filepath = PLANS_DIR / f"{plan_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(plan_dict, f, indent=2, ensure_ascii=False)
    
    return plan_id


def load_plan(plan_id: str) -> dict | None:
    """Load a single plan by ID."""
    filepath = PLANS_DIR / f"{plan_id}.json"
    if not filepath.exists():
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_plans() -> list[dict]:
    """Return all saved plans, sorted by creation date (newest first)."""
    plans = []
    for f in PLANS_DIR.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                plan = json.load(fh)
                plans.append(plan)
        except (json.JSONDecodeError, IOError):
            continue
    plans.sort(key=lambda p: p.get("created_at", ""), reverse=True)
    return plans


def get_plan_choices() -> list[tuple[str, str]]:
    """Return list of (display_label, plan_id) tuples for Gradio dropdowns."""
    plans = get_all_plans()
    choices = []
    for p in plans:
        label = f"{p.get('condition', 'Unknown')} — {p.get('patient_name', 'Anonymous')} ({p.get('created_at', '')[:10]})"
        choices.append((label, p["id"]))
    return choices


def add_progress_update(plan_id: str, update: dict) -> dict | None:
    """Add a daily progress update to an existing plan."""
    plan = load_plan(plan_id)
    if plan is None:
        return None
    update["timestamp"] = datetime.now().isoformat()
    plan.setdefault("updates", []).append(update)
    save_plan(plan)
    return plan


def delete_plan(plan_id: str) -> bool:
    """Delete a plan by ID."""
    filepath = PLANS_DIR / f"{plan_id}.json"
    if filepath.exists():
        filepath.unlink()
        return True
    return False


# ── Formatting Helpers ─────────────────────────────────────────


def format_plan_card(plan: dict) -> str:
    """Format a plan as a pretty markdown card for display."""
    name = plan.get("patient_name", "Anonymous")
    condition = plan.get("condition", "Unknown Condition")
    pain = plan.get("pain_level", "?")
    created = plan.get("created_at", "Unknown date")[:10]
    updates = len(plan.get("updates", []))

    return f"""### 📋 {condition}
**Patient:** {name} · **Pain:** {pain}/10 · **Created:** {created} · **Updates:** {updates}

---"""


def format_all_plans_display() -> str:
    """Format all plans as a scrollable markdown list."""
    plans = get_all_plans()
    if not plans:
        return "### 📭 No Saved Plans\n\nCreate your first rehabilitation plan in the **Create New Plan** tab!"
    
    header = f"## 📚 Your Rehabilitation Plans ({len(plans)} total)\n\n"
    cards = "\n".join(format_plan_card(p) for p in plans)
    return header + cards
