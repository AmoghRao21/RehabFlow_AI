# RehabFlow AI — Complete Execution Checklist (Flow-First, Supabase, Production-Grade)

This checklist defines the **full production execution plan** for RehabFlow AI using:

- **uv** for Python environment
- **Gradio** for UI
- **MedGemma** for AI
- **Supabase (PostgreSQL)** for Database
- **Supabase Auth** for Authentication
- **Supabase Storage** for Image Storage

This replaces SQLite-based architecture.

Team:

- **Amogha** — Product Architect, UI/UX Lead, AI Logic Lead, Integration Lead
- **Muneer** — Infrastructure Lead, MedGemma Integration, Supabase Integration, Concurrency, Security

---

# Phase 0 — Foundation (Completed ✅)

Completed:

- [x] uv project initialized
- [x] Dependencies installed
- [x] Gradio base app running

---

# Phase 1 — Supabase Setup (CRITICAL FIRST STEP)

## Objective

Configure Supabase as the primary backend.

Supabase will handle:

- Authentication
- PostgreSQL Database
- Image Storage
- Password reset

---

## Muneer Tasks — Supabase Project Setup

Checklist:

- [x] Create Supabase project
- [x] Get credentials (SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY)
- [x] Store in `.env`
- [x] Add Supabase Python client dependency (`supabase>=2.4.0`)

Deliverable:

Supabase backend ready

Dependency:

None

---

## Database Schema (Supabase PostgreSQL)

Muneer creates tables:

### users

Managed by Supabase Auth

---

### profiles table

```
id (uuid, primary key, references auth.users)
name
age
created_at
```

---

### assessments table

```
id
user_id
assessment_data (jsonb)
created_at
```

---

### rehab_plans table

```
id
user_id
plan_data (jsonb)
created_at
```

---

### progress table

```
id
user_id
day
progress_data (jsonb)
created_at
```

---

# Phase 2 — Authentication System (Supabase Auth)

Supabase handles:

- Registration
- Login
- Session management
- Forgot password

---

## Amogha Tasks — Auth UI

File:

```
ui/auth.py
```

Checklist:

Create tabs:

Login Tab:

- [ ] Email input
- [ ] Password input
- [ ] Login button
- [ ] Forgot Password button

Register Tab:

- [ ] Name
- [ ] Age
- [ ] Email
- [ ] Password
- [ ] Register button

Forgot Password Flow:

- [ ] Email input
- [ ] Send reset request
- [ ] Show success message

Deliverable:

Full auth UI connected to Supabase

Dependency:

Supabase project created

---

## Muneer Tasks — Supabase Auth Integration

File:

```
core/supabase_client.py
```

Checklist:

- [x] Create `SupabaseClient` class
- [x] Implement `sign_up()` with email/password and metadata
- [x] Implement `sign_in()` with email/password
- [x] Implement `sign_out()`
- [x] Implement `reset_password()` (sends reset email)
- [x] Implement `get_current_user()`
- [x] Expose `get_supabase_client()` helper from `core` package
- [x] Add Supabase config to `utils/config.py` (URL, keys, bucket)

Deliverable:

Supabase auth fully working ✅ (backend ready, UI pending from Amogha)

Dependency:

Supabase credentials ready ✅

---

# Phase 3 — Session Management

Supabase handles session.

## Amogha Tasks

Checklist:

- [ ] Store current user
- [ ] Route authenticated users to home
- [ ] Prevent unauthenticated access

---

# Phase 4 — Medical Intake System

## Amogha Tasks

File:

```
ui/assessment.py
```

Checklist:

Collect:

- Profile data
- Pain data
- Lifestyle data
- Diet data
- Psychometric data
- Image upload

Upload image to Supabase Storage bucket.

Store image URL in database.

Deliverable:

Assessment stored in Supabase

Dependency:

Auth working

---

## Muneer Tasks

File:

```
ai/image_analysis.py
```

Checklist:

- [ ] Accept Supabase image URL
- [ ] Download image
- [ ] Process image

---

# Phase 5 — MedGemma Integration

## Muneer Tasks

File:

```
ai/medgemma.py
```

Checklist:

- [ ] Load MedGemma
- [ ] Generate response

---

## Amogha Tasks

File:

```
ai/prompt_builder.py
```

Checklist:

- [ ] Build prompt from assessment

---

# Phase 6 — Plan Generation

## Amogha Tasks

File:

```
ai/plan_generator.py
```

Checklist:

- [ ] Generate structured plan
- [ ] Save plan to Supabase

---

# Phase 7 — Plan Display

## Amogha Tasks

File:

```
ui/plan.py
```

Checklist:

- [ ] Show exercises
- [ ] Show diet

---

# Phase 8 — Rehab Session Engine

## Amogha Tasks

File:

```
ui/session.py
```

Checklist:

- [ ] Exercise timer
- [ ] Completion tracking

---

# Phase 9 — Progress Tracking

## Muneer Tasks

Checklist:

- [ ] Save progress to Supabase

---

## Amogha Tasks

File:

```
ui/progress.py
```

Checklist:

- [ ] Show progress

---

# Phase 10 — Plan Adaptation

## Amogha Tasks

File:

```
ai/plan_adapter.py
```

Checklist:

- [ ] Update plan

---

# Phase 11 — Report Generation

## Muneer Tasks

File:

```
core/report_generator.py
```

Checklist:

- [ ] Generate report

---

## Amogha Tasks

File:

```
ui/report.py
```

Checklist:

- [ ] Export report UI

---

# Forgot Password Flow (Supabase Native)

Flow:

```
User clicks Forgot Password
↓
User enters email
↓
Supabase sends reset email
↓
User resets password
↓
User logs in normally
```

---

# Storage Architecture

Supabase Storage:

```
Bucket: injury-images
```

Store:

- Injury photos

Save URL in assessments table

---

# Final Integration Checklist

- [ ] Register
- [ ] Login
- [ ] Forgot password
- [ ] Assessment
- [ ] Image upload
- [ ] Plan generation
- [ ] Session
- [ ] Progress tracking
- [ ] Report export

---

# Authority

Amogha owns:

- UI
- Prompt logic
- Plan logic

Muneer owns:

- Supabase integration
- MedGemma
- Storage
- Security

---

This is now fully production-ready architecture using Supabase.
