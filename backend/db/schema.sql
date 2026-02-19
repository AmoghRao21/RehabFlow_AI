-- =============================================================
-- RehabFlow AI — Production Database Schema
-- Target: Supabase (PostgreSQL 15+)
-- =============================================================

-- ======================== ENUM TYPES =========================

CREATE TYPE pain_location_enum AS ENUM (
    'knee', 'shoulder', 'lower_back', 'neck','upper_back','ankle', 'wrist', 'hip', 'elbow','foot','other'
);

CREATE TYPE habit_frequency_enum AS ENUM (
    'never', 'occasional', 'regular', 'heavy'
);

CREATE TYPE difficulty_enum AS ENUM (
    'beginner', 'intermediate', 'advanced'
);

CREATE TYPE plan_status_enum AS ENUM (
    'active', 'replaced'
);

-- ========================== TABLES ===========================

-- Profiles (linked to Supabase Auth)
CREATE TABLE profiles (
    id              uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name       text,
    language        text,
    total_points    integer DEFAULT 0,
    current_streak  integer DEFAULT 0,
    longest_streak  integer DEFAULT 0,
    last_completed_date date,
    created_at      timestamptz DEFAULT now()
);

-- Baseline Profiles
CREATE TABLE baseline_profiles (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE UNIQUE,
    age                 integer,
    gender              text,
    height_cm           integer,
    weight_kg           integer,
    occupation_type     text,
    daily_sitting_hours integer,
    physical_work_level text,
    gym_frequency       text,
    alcohol_usage       habit_frequency_enum,
    smoking_usage       habit_frequency_enum,
    drug_usage          habit_frequency_enum,
    created_at          timestamptz DEFAULT now(),
    updated_at          timestamptz DEFAULT now()
);

-- Baseline Profile Audit Log
CREATE TABLE baseline_profile_audit (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    baseline_profile_id  uuid NOT NULL REFERENCES baseline_profiles(id) ON DELETE CASCADE,
    changed_at           timestamptz DEFAULT now(),
    snapshot             jsonb
);

-- Medical Conditions Reference
CREATE TABLE medical_conditions (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name        text UNIQUE NOT NULL,
    description text
);

-- User ↔ Medical Conditions (many-to-many)
CREATE TABLE user_medical_conditions (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    condition_id  uuid NOT NULL REFERENCES medical_conditions(id) ON DELETE CASCADE,
    diagnosed_at  date
);

-- Injury Assessments
CREATE TABLE injury_assessments (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    pain_location        pain_location_enum,
    pain_level           integer CHECK (pain_level BETWEEN 0 AND 10),
    pain_started_at      timestamptz,
    pain_cause           text,
    visible_swelling     boolean,
    mobility_restriction boolean,
    additional_notes     text,
    created_at           timestamptz DEFAULT now()
);

-- Exercise Library (public reference data)
CREATE TABLE exercise_library (
    id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name                text UNIQUE NOT NULL,
    body_part           text,
    difficulty          difficulty_enum,
    instruction_text    text,
    video_url           text,
    thumbnail_url       text,
    contraindications   text,
    created_at          timestamptz DEFAULT now()
);

-- Rehab Plans (versioned per day per assessment)
CREATE TABLE rehab_plans (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    injury_assessment_id  uuid NOT NULL REFERENCES injury_assessments(id) ON DELETE CASCADE,
    day_number            integer NOT NULL,
    version               integer NOT NULL,
    status                plan_status_enum,
    created_at            timestamptz DEFAULT now()
);

-- Rehab Plan → Exercises
CREATE TABLE rehab_plan_exercises (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id           uuid NOT NULL REFERENCES rehab_plans(id) ON DELETE CASCADE,
    exercise_id       uuid REFERENCES exercise_library(id),
    sets              integer,
    reps              integer,
    duration_seconds  integer,
    order_index       integer
);

-- Rehab Plan → Diet Recommendations
CREATE TABLE rehab_plan_diet (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id     uuid NOT NULL REFERENCES rehab_plans(id) ON DELETE CASCADE,
    meal_type   text,
    description text
);

-- Rehab Plan → Safety Warnings
CREATE TABLE rehab_plan_safety (
    id      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id uuid NOT NULL REFERENCES rehab_plans(id) ON DELETE CASCADE,
    warning text
);

-- Daily Progress Tracking
CREATE TABLE daily_progress (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    injury_assessment_id  uuid NOT NULL REFERENCES injury_assessments(id) ON DELETE CASCADE,
    day_number            integer,
    pain_level            integer CHECK (pain_level BETWEEN 0 AND 10),
    notes                 text,
    created_at            timestamptz DEFAULT now()
);

-- Exercise Sessions
CREATE TABLE exercise_sessions (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    exercise_id       uuid REFERENCES exercise_library(id),
    duration_seconds  integer,
    completed         boolean DEFAULT false,
    verified          boolean DEFAULT false,
    created_at        timestamptz DEFAULT now()
);

-- Points Log (gamification)
CREATE TABLE points_log (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    points      integer,
    source      text,
    created_at  timestamptz DEFAULT now()
);

-- Safety Rules (public reference data)
CREATE TABLE safety_rules (
    id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    injury_type                 text,
    max_difficulty_allowed      difficulty_enum,
    contraindicated_exercises   text,
    created_at                  timestamptz DEFAULT now()
);

-- ========================= INDEXES ===========================

CREATE INDEX idx_baseline_profiles_user_id            ON baseline_profiles(user_id);
CREATE INDEX idx_injury_assessments_user_id            ON injury_assessments(user_id);
CREATE INDEX idx_rehab_plans_injury_assessment_id      ON rehab_plans(injury_assessment_id);
CREATE INDEX idx_daily_progress_injury_assessment_id   ON daily_progress(injury_assessment_id);
CREATE INDEX idx_exercise_sessions_user_id             ON exercise_sessions(user_id);
CREATE INDEX idx_points_log_user_id                    ON points_log(user_id);

-- ==================== ROW LEVEL SECURITY =====================

-- ---------- Enable RLS on all user-scoped tables ----------

ALTER TABLE profiles                ENABLE ROW LEVEL SECURITY;
ALTER TABLE baseline_profiles       ENABLE ROW LEVEL SECURITY;
ALTER TABLE baseline_profile_audit  ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_conditions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_medical_conditions ENABLE ROW LEVEL SECURITY;
ALTER TABLE injury_assessments      ENABLE ROW LEVEL SECURITY;
ALTER TABLE rehab_plans             ENABLE ROW LEVEL SECURITY;
ALTER TABLE rehab_plan_exercises    ENABLE ROW LEVEL SECURITY;
ALTER TABLE rehab_plan_diet         ENABLE ROW LEVEL SECURITY;
ALTER TABLE rehab_plan_safety       ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_progress          ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_sessions       ENABLE ROW LEVEL SECURITY;
ALTER TABLE points_log              ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_library        ENABLE ROW LEVEL SECURITY;
ALTER TABLE safety_rules            ENABLE ROW LEVEL SECURITY;

-- ---------- profiles ----------

CREATE POLICY profiles_select ON profiles
    FOR SELECT USING (id = auth.uid());

CREATE POLICY profiles_update ON profiles
    FOR UPDATE USING (id = auth.uid());

CREATE POLICY profiles_insert ON profiles
    FOR INSERT WITH CHECK (id = auth.uid());

-- ---------- baseline_profiles ----------

CREATE POLICY baseline_profiles_select ON baseline_profiles
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY baseline_profiles_insert ON baseline_profiles
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY baseline_profiles_update ON baseline_profiles
    FOR UPDATE USING (user_id = auth.uid());

-- ---------- baseline_profile_audit ----------

CREATE POLICY baseline_profile_audit_select ON baseline_profile_audit
    FOR SELECT USING (
        baseline_profile_id IN (
            SELECT id FROM baseline_profiles WHERE user_id = auth.uid()
        )
    );

-- ---------- medical_conditions (public read-only) ----------

CREATE POLICY medical_conditions_select ON medical_conditions
    FOR SELECT USING (true);

-- ---------- user_medical_conditions ----------

CREATE POLICY user_medical_conditions_select ON user_medical_conditions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY user_medical_conditions_insert ON user_medical_conditions
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY user_medical_conditions_delete ON user_medical_conditions
    FOR DELETE USING (user_id = auth.uid());

-- ---------- injury_assessments ----------

CREATE POLICY injury_assessments_select ON injury_assessments
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY injury_assessments_insert ON injury_assessments
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- ---------- rehab_plans (via injury_assessments) ----------

CREATE POLICY rehab_plans_select ON rehab_plans
    FOR SELECT USING (
        injury_assessment_id IN (
            SELECT id FROM injury_assessments WHERE user_id = auth.uid()
        )
    );

CREATE POLICY rehab_plans_insert ON rehab_plans
    FOR INSERT WITH CHECK (
        injury_assessment_id IN (
            SELECT id FROM injury_assessments WHERE user_id = auth.uid()
        )
    );

-- ---------- rehab_plan_exercises (via rehab_plans → injury_assessments) ----------

CREATE POLICY rehab_plan_exercises_select ON rehab_plan_exercises
    FOR SELECT USING (
        plan_id IN (
            SELECT rp.id FROM rehab_plans rp
            JOIN injury_assessments ia ON rp.injury_assessment_id = ia.id
            WHERE ia.user_id = auth.uid()
        )
    );

CREATE POLICY rehab_plan_exercises_insert ON rehab_plan_exercises
    FOR INSERT WITH CHECK (
        plan_id IN (
            SELECT rp.id FROM rehab_plans rp
            JOIN injury_assessments ia ON rp.injury_assessment_id = ia.id
            WHERE ia.user_id = auth.uid()
        )
    );

-- ---------- rehab_plan_diet (via rehab_plans → injury_assessments) ----------

CREATE POLICY rehab_plan_diet_select ON rehab_plan_diet
    FOR SELECT USING (
        plan_id IN (
            SELECT rp.id FROM rehab_plans rp
            JOIN injury_assessments ia ON rp.injury_assessment_id = ia.id
            WHERE ia.user_id = auth.uid()
        )
    );

CREATE POLICY rehab_plan_diet_insert ON rehab_plan_diet
    FOR INSERT WITH CHECK (
        plan_id IN (
            SELECT rp.id FROM rehab_plans rp
            JOIN injury_assessments ia ON rp.injury_assessment_id = ia.id
            WHERE ia.user_id = auth.uid()
        )
    );

-- ---------- rehab_plan_safety (via rehab_plans → injury_assessments) ----------

CREATE POLICY rehab_plan_safety_select ON rehab_plan_safety
    FOR SELECT USING (
        plan_id IN (
            SELECT rp.id FROM rehab_plans rp
            JOIN injury_assessments ia ON rp.injury_assessment_id = ia.id
            WHERE ia.user_id = auth.uid()
        )
    );

CREATE POLICY rehab_plan_safety_insert ON rehab_plan_safety
    FOR INSERT WITH CHECK (
        plan_id IN (
            SELECT rp.id FROM rehab_plans rp
            JOIN injury_assessments ia ON rp.injury_assessment_id = ia.id
            WHERE ia.user_id = auth.uid()
        )
    );

-- ---------- daily_progress (via injury_assessments) ----------

CREATE POLICY daily_progress_select ON daily_progress
    FOR SELECT USING (
        injury_assessment_id IN (
            SELECT id FROM injury_assessments WHERE user_id = auth.uid()
        )
    );

CREATE POLICY daily_progress_insert ON daily_progress
    FOR INSERT WITH CHECK (
        injury_assessment_id IN (
            SELECT id FROM injury_assessments WHERE user_id = auth.uid()
        )
    );

-- ---------- exercise_sessions ----------

CREATE POLICY exercise_sessions_select ON exercise_sessions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY exercise_sessions_insert ON exercise_sessions
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY exercise_sessions_update ON exercise_sessions
    FOR UPDATE USING (user_id = auth.uid());

-- ---------- points_log ----------

CREATE POLICY points_log_select ON points_log
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY points_log_insert ON points_log
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- ---------- exercise_library (public read-only) ----------

CREATE POLICY exercise_library_select ON exercise_library
    FOR SELECT USING (true);

-- ---------- safety_rules (public read-only) ----------

CREATE POLICY safety_rules_select ON safety_rules
    FOR SELECT USING (true);

-- =============================================================
-- END OF SCHEMA
-- =============================================================


create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, full_name)
  values (new.id, new.raw_user_meta_data->>'full_name');
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();



insert into medical_conditions (name, description) values
('Diabetes', 'Chronic condition affecting blood sugar levels'),
('Hypertension', 'High blood pressure'),
('Arthritis', 'Inflammation of joints'),
('Cardiovascular Disease', 'Heart-related conditions'),
('Asthma', 'Respiratory condition'),
('Obesity', 'Excess body weight condition'),
('Thyroid Disorder', 'Hormonal imbalance condition'),
('Osteoporosis', 'Bone density reduction condition');


insert into exercise_library (name, body_part, difficulty, instruction_text)
values
('Knee Extension Stretch', 'knee', 'beginner', 'Sit upright and slowly extend your knee. Hold for 5 seconds.'),
('Shoulder Roll', 'shoulder', 'beginner', 'Roll shoulders gently forward and backward.'),
('Lower Back Stretch', 'lower_back', 'beginner', 'Gently bend forward keeping knees slightly bent.'),
('Ankle Rotation', 'ankle', 'beginner', 'Rotate ankle clockwise and counterclockwise slowly.'),
('Neck Tilt', 'neck', 'beginner', 'Tilt head side to side gently without strain.');


-- =============================================================
-- AI SUPPORT EXTENSION (Injury Images + Clinical Analysis)
-- =============================================================

-- -------------------------
-- Injury Images (Multiple per Injury)
-- -------------------------

CREATE TABLE injury_images (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    injury_assessment_id  uuid NOT NULL REFERENCES injury_assessments(id) ON DELETE CASCADE,
    image_url             text NOT NULL,
    ai_description        text,
    created_at            timestamptz DEFAULT now()
);

CREATE INDEX idx_injury_images_injury_assessment_id
    ON injury_images(injury_assessment_id);

-- -------------------------
-- AI Clinical Analysis (Versioned)
-- -------------------------

CREATE TABLE ai_clinical_analysis (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    injury_assessment_id  uuid NOT NULL REFERENCES injury_assessments(id) ON DELETE CASCADE,
    probable_condition    text,
    confidence_score      numeric,
    reasoning             text,
    model_version         text,
    created_at            timestamptz DEFAULT now()
);

CREATE INDEX idx_ai_clinical_analysis_injury_assessment_id
    ON ai_clinical_analysis(injury_assessment_id);

-- =============================================================
-- RLS
-- =============================================================

ALTER TABLE injury_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_clinical_analysis ENABLE ROW LEVEL SECURITY;

-- -------------------------
-- injury_images (via injury_assessments)
-- -------------------------

CREATE POLICY injury_images_select ON injury_images
    FOR SELECT USING (
        injury_assessment_id IN (
            SELECT id FROM injury_assessments WHERE user_id = auth.uid()
        )
    );

CREATE POLICY injury_images_insert ON injury_images
    FOR INSERT WITH CHECK (
        injury_assessment_id IN (
            SELECT id FROM injury_assessments WHERE user_id = auth.uid()
        )
    );

-- -------------------------
-- ai_clinical_analysis (via injury_assessments)
-- -------------------------

CREATE POLICY ai_clinical_analysis_select ON ai_clinical_analysis
    FOR SELECT USING (
        injury_assessment_id IN (
            SELECT id FROM injury_assessments WHERE user_id = auth.uid()
        )
    );

-- IMPORTANT:
-- Do NOT allow client-side INSERT for ai_clinical_analysis.
-- Only backend (service role) should insert AI results.
