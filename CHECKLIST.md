# RehabFlow AI — Complete Execution Checklist (Flow-First, Production-Grade)

This checklist follows the **true production user flow order**, starting from Authentication and proceeding step-by-step through the full RehabFlow AI lifecycle.

This replaces the previous module-first checklist.

Team:

* **Amogha** — Product Architect, UI/UX Lead, AI Logic Lead, Integration Lead
* **Muneer** — Infrastructure Lead, MedGemma Integration, Database, Concurrency, Security

Environment:

* Python managed via **uv**
* UI built using **Gradio**
* AI powered by **MedGemma via Transformers**
* Database: **SQLite via SQLAlchemy**

---

# Phase 0 — Foundation (Already Completed ✅)

## Objective

Initialize production-grade project using uv.

## Completed Tasks

* [x] uv project initialized
* [x] Dependencies installed via uv
* [x] Folder structure created
* [x] Gradio base app runs
* [x] app.py entrypoint working

No further action required.

---

# Phase 1 — Authentication System (START HERE)

## Why This Comes First

Everything depends on user identity:

* Plans
* Progress
* Reports
* Sessions
* Diet plans

All must link to user_id.

---

## Amogha Tasks — Auth UI

File:

```
ui/auth.py
```

Checklist:

* [ ] Create Login screen

* [ ] Create Register screen

* [ ] Add fields:

  * [ ] Name
  * [ ] Age
  * [ ] Email or Phone
  * [ ] Password
  * [ ] Confirm Password

* [ ] Create Tabs:

  * [ ] Login tab
  * [ ] Register tab

* [ ] Return structured login data

Deliverable:

Working Auth UI

Dependency:

Phase 0 complete

---

## Muneer Tasks — Auth Database Layer

File:

```
core/database.py
```

Checklist:

* [ ] Create User table

Fields:

```
id
name
age
email
password_hash
created_at
```

* [ ] Implement:

```
create_user()
get_user_by_email()
verify_user()
```

* [ ] Use bcrypt password hashing

Deliverable:

Secure user storage

Dependency:

Phase 0 complete

---

# Phase 2 — Session Management System

## Objective

Maintain logged-in user state.

---

## Amogha Tasks

File:

```
core/session_engine.py
```

Checklist:

* [ ] Create user session object
* [ ] Store current_user_id
* [ ] Enable persistent session

Deliverable:

User session maintained

Dependency:

Phase 1 complete

---

## Muneer Tasks

File:

```
security/sanitizer.py
```

Checklist:

* [ ] Validate login inputs
* [ ] Validate registration inputs

Deliverable:

Secure authentication inputs

Dependency:

Phase 1 complete

---

# Phase 3 — Medical Intake & Assessment System

## Objective

Collect medical and lifestyle data.

---

## Amogha Tasks

File:

```
ui/assessment.py
```

Checklist:

Collect:

Profile:

* [ ] Age
* [ ] Gender
* [ ] Language

Pain:

* [ ] Pain location
* [ ] Pain level
* [ ] Duration

Lifestyle:

* [ ] Occupation
* [ ] Sitting hours
* [ ] Commute type
* [ ] Gym usage

Diet:

* [ ] Diet preference
* [ ] Dairy intake
* [ ] Meals per day

Psychometric:

* [ ] Motivation level
* [ ] Discipline level
* [ ] Sleep duration

Image:

* [ ] Injury photo upload

Deliverable:

Structured assessment_data

Dependency:

Phase 2 complete

---

## Muneer Tasks

File:

```
ai/image_analysis.py
```

Checklist:

* [ ] Validate image
* [ ] Preprocess image

Deliverable:

Safe image pipeline

Dependency:

Assessment image upload exists

---

# Phase 4 — MedGemma Integration

## Objective

Enable AI reasoning.

---

## Muneer Tasks

File:

```
ai/medgemma.py
```

Checklist:

* [ ] Load MedGemma model
* [ ] Implement inference function

Function:

```
generate_response(prompt)
```

Deliverable:

Working AI inference

Dependency:

Foundation complete

---

## Amogha Tasks

File:

```
ai/prompt_builder.py
```

Checklist:

* [ ] Convert assessment_data → prompt

Deliverable:

Medical prompt structure

Dependency:

Assessment complete

---

# Phase 5 — Plan Generation System

## Objective

Generate rehab + diet plan.

---

## Amogha Tasks

File:

```
ai/plan_generator.py
```

Checklist:

* [ ] Call medgemma
* [ ] Convert response → structured plan

Deliverable:

Plan object created

Dependency:

MedGemma working

---

## Muneer Tasks

File:

```
core/concurrency.py
```

Checklist:

* [ ] Implement ThreadPoolExecutor

Deliverable:

Concurrent inference

Dependency:

MedGemma working

---

# Phase 6 — Plan Display UI

## Amogha Tasks

File:

```
ui/plan.py
```

Checklist:

* [ ] Display exercises
* [ ] Display diet

Deliverable:

Plan visible to user

Dependency:

Plan generation complete

---

# Phase 7 — Guided Rehab Session System

## Amogha Tasks

File:

```
ui/session.py
```

Checklist:

* [ ] Show exercise
* [ ] Show timer
* [ ] Track completion

Deliverable:

Exercise session working

Dependency:

Plan display working

---

# Phase 8 — Progress Tracking System

## Muneer Tasks

File:

```
core/database.py
```

Checklist:

* [ ] Save progress
* [ ] Load progress

---

## Amogha Tasks

File:

```
ui/progress.py
```

Checklist:

* [ ] Show recovery graphs

Dependency:

Progress saving working

---

# Phase 9 — Plan Adaptation System

## Amogha Tasks

File:

```
ai/plan_adapter.py
```

Checklist:

* [ ] Modify plan based on progress

Dependency:

Progress tracking working

---

# Phase 10 — Report Generator

## Muneer Tasks

File:

```
core/report_generator.py
```

Checklist:

* [ ] Generate PDF report

---

## Amogha Tasks

File:

```
ui/report.py
```

Checklist:

* [ ] Export report UI

Dependency:

Report generator complete

---

# Final Integration Checklist

Full flow must work:

* [ ] User registers
* [ ] User logs in
* [ ] User completes assessment
* [ ] User uploads image
* [ ] AI generates plan
* [ ] User performs session
* [ ] Timer works
* [ ] Progress saved
* [ ] Plan adapts
* [ ] Report exports

---

# Authority and Ownership

Amogha owns:

* UI
* Prompt logic
* Plan generation
* Integration

Muneer owns:

* MedGemma integration
* Database
* Security
* Concurrency

---

# Execution Rule

Always build in flow order.

Never skip phases.

Never mix responsibilities.

This ensures production-grade architecture and hackathon-winning quality.
