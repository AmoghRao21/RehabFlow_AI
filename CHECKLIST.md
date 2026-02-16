# RehabFlow AI — Complete 8‑Day Execution Checklist

This document defines the **complete execution plan**, task split, dependencies, and deliverables for building RehabFlow AI using **Python, Gradio, and MedGemma**.

Team:

* **Amogha (You)** — Product Architect, UI/UX Lead, AI Logic Lead, Integration Lead
* **Muneer** — Infrastructure Lead, MedGemma Integration, Database, Concurrency, Security

---

# 0. Project Initialization (Both — Mandatory First Step)

## Objective

Establish foundation before development begins.

## Checklist

* [ ] Create root project folder

```
rehabflow_ai/
│
├── app.py
├── requirements.txt
├── README.md
│
├── ui/
├── ai/
├── core/
├── security/
├── assets/
├── data/
```

* [ ] Create Python virtual environment

```
python -m venv venv
source venv/bin/activate   (Linux/Mac)
venv\\Scripts\\activate  (Windows)
```

* [ ] Install dependencies

```
pip install gradio
pip install torch transformers accelerate
pip install pillow opencv-python
pip install reportlab
pip install pyttsx3
pip install sqlalchemy
pip install python-dotenv
```

* [ ] Verify Gradio works

```
python -c "import gradio as gr; print('Gradio OK')"
```

---

# Folder Ownership

## Amogha Owns

```
app.py
ui/
ai/prompt_builder.py
ai/plan_generator.py
core/session_engine.py
```

## Muneer Owns

```
ai/medgemma.py
ai/image_analysis.py
core/database.py
core/concurrency.py
core/report_generator.py
security/sanitizer.py
```

---

# Day 1 — UI Foundation + MedGemma Setup

## Amogha Tasks (UI Foundation)

### Task A1.1 — Create Home Screen

File: `ui/home.py`

Checklist:

* [ ] Create Gradio layout
* [ ] Add buttons:

  * [ ] Start Recovery
  * [ ] Continue Session
  * [ ] View Progress
  * [ ] Export Report

Deliverable: Functional home screen

Dependency: None

---

### Task A1.2 — Create Navigation Controller

File: `app.py`

Checklist:

* [ ] Create screen routing system
* [ ] Connect home screen

Deliverable: App launches successfully

Dependency: A1.1 complete

---

### Task A1.3 — Apply UI Styling

Checklist:

* [ ] Large fonts
* [ ] Clean layout
* [ ] Accessible buttons

Deliverable: Product‑quality UI feel

Dependency: A1.2 complete

---

## Muneer Tasks (MedGemma Setup)

### Task M1.1 — Install and Load MedGemma

File: `ai/medgemma.py`

Checklist:

* [ ] Install MedGemma
* [ ] Load model successfully

Deliverable: Model loads without errors

Dependency: Project initialization complete

---

### Task M1.2 — Test Basic Inference

Checklist:

* [ ] Send test prompt
* [ ] Receive response

Deliverable: Inference working

Dependency: M1.1 complete

---

# Day 2 — Assessment System

## Amogha Tasks

### Task A2.1 — Build Assessment UI

File: `ui/assessment.py`

Checklist:

* [ ] Pain location input
* [ ] Pain level slider
* [ ] Diet preference selector
* [ ] Lifestyle questions
* [ ] Psychometric questions

Deliverable: Assessment form working

Dependency: Navigation system complete

---

### Task A2.2 — Add Image Upload

Checklist:

* [ ] Add Gradio image upload component
* [ ] Display preview

Deliverable: Image upload working

Dependency: Assessment UI complete

---

### Task A2.3 — Return Structured Data

Checklist:

* [ ] Convert input to dictionary

Example:

```
{
 pain_level: 5,
 diet: veg,
 lifestyle: desk_job
}
```

Deliverable: Structured data returned

Dependency: Assessment form complete

---

## Muneer Tasks

### Task M2.1 — Create MedGemma Interface Function

File: `ai/medgemma.py`

Function:

```
def generate_response(prompt):
    pass
```

Deliverable: Callable inference function

Dependency: MedGemma installed

---

# Day 3 — Exercise Session Engine

## Amogha Tasks

### Task A3.1 — Build Session Screen

File: `ui/session.py`

Checklist:

* [ ] Display exercise name
* [ ] Display instructions
* [ ] Display image

Deliverable: Session screen visible

Dependency: Navigation complete

---

### Task A3.2 — Build Timer Engine

File: `core/session_engine.py`

Checklist:

* [ ] Countdown timer function
* [ ] Start button
* [ ] Stop button

Deliverable: Timer works

Dependency: Session UI complete

---

### Task A3.3 — Exercise Progression Logic

Checklist:

* [ ] Move from exercise 1 → exercise 2
* [ ] Track completion

Deliverable: Session flow working

Dependency: Timer working

---

## Muneer Tasks

### Task M3.1 — Build Image Processing Pipeline

File: `ai/image_analysis.py`

Checklist:

* [ ] Validate image
* [ ] Preprocess image
* [ ] Return processed image

Deliverable: Image pipeline working

Dependency: MedGemma integration complete

---

# Day 4 — Plan Generation System

## Amogha Tasks

### Task A4.1 — Build Prompt Builder

File: `ai/prompt_builder.py`

Checklist:

* [ ] Convert assessment → prompt

Deliverable: Prompt generator working

Dependency: Assessment complete

---

### Task A4.2 — Build Plan Generator

File: `ai/plan_generator.py`

Checklist:

* [ ] Convert MedGemma output → structured plan

Deliverable: Structured plan object

Dependency: Prompt builder complete

---

## Muneer Tasks

### Task M4.1 — Optimize MedGemma Inference

Checklist:

* [ ] Reduce inference latency
* [ ] Improve memory handling

Deliverable: Faster plan generation

Dependency: MedGemma working

---

# Day 5 — Database Integration

## Muneer Tasks

### Task M5.1 — Create Database Layer

File: `core/database.py`

Checklist:

* [ ] save_user()
* [ ] save_plan()
* [ ] save_progress()
* [ ] load_plan()

Deliverable: Database working

Dependency: None

---

## Amogha Tasks

### Task A5.1 — Connect UI to Plan Generator

Checklist:

* [ ] Assessment → Plan generation
* [ ] Plan → Display UI

Deliverable: End‑to‑end plan generation working

Dependency: Plan generator complete

---

# Day 6 — Progress Tracking + Report System

## Muneer Tasks

### Task M6.1 — Build Report Generator

File: `core/report_generator.py`

Checklist:

* [ ] Generate PDF report

Deliverable: Exportable report

Dependency: Database complete

---

## Amogha Tasks

### Task A6.1 — Build Progress Dashboard

File: `ui/progress.py`

Checklist:

* [ ] Show pain trends
* [ ] Show completion rate

Deliverable: Progress visible

Dependency: Database ready

---

# Day 7 — Security + Concurrency

## Muneer Tasks

### Task M7.1 — Input Sanitization

File: `security/sanitizer.py`

Checklist:

* [ ] Validate inputs
* [ ] Validate images

Deliverable: Secure inputs

Dependency: Image pipeline complete

---

### Task M7.2 — Concurrency System

File: `core/concurrency.py`

Checklist:

* [ ] Thread pool executor
* [ ] Async plan generation

Deliverable: Concurrent execution working

Dependency: Plan generator complete

---

# Day 8 — Integration + Polish

## Both Tasks

Checklist:

* [ ] Connect all modules
* [ ] Fix bugs
* [ ] Optimize performance
* [ ] Improve UI clarity
* [ ] Test full workflow

---

# Final Demo Flow Checklist

Must work end‑to‑end:

* [ ] Assessment completed
* [ ] Image uploaded
* [ ] Plan generated
* [ ] Session started
* [ ] Timer works
* [ ] Progress tracked
* [ ] Report exported

---

# Success Criteria

RehabFlow AI is considered complete when:

* UI feels like production product
* MedGemma generates plans reliably
* Exercise session works with timers
* Progress tracking works
* Report export works
* No crashes

---

# Architecture Authority

Amogha owns:

* Product architecture
* UI
* Plan logic
* Integration

Muneer owns:

* Model integration
* Infrastructure
* Database
* Security
* Concurrency

---

This checklist is optimized for **maximum hackathon success and execution speed**.

Follow sequentially and strictly respect dependencies.
