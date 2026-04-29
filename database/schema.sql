-- ============================================================
-- NourisHer PCOS Wellness App — PostgreSQL Schema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    username      VARCHAR(100) UNIQUE NOT NULL,
    full_name     VARCHAR(200) NOT NULL,
    password_hash TEXT NOT NULL,
    avatar_url    TEXT,
    is_active     BOOLEAN DEFAULT TRUE,
    is_verified   BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- PCOS PROFILES
-- ─────────────────────────────────────────
CREATE TABLE pcos_profiles (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age                 SMALLINT CHECK (age BETWEEN 10 AND 80),
    weight_kg           NUMERIC(5,2),
    height_cm           NUMERIC(5,2),
    bmi                 NUMERIC(4,2),
    diagnosis_year      SMALLINT,
    dietary_preference  VARCHAR(50) DEFAULT 'no_restriction',  -- vegetarian, vegan, mediterranean, low_gi
    activity_level      VARCHAR(30) DEFAULT 'moderate',        -- sedentary, light, moderate, active
    cycle_length_days   SMALLINT,
    last_period_date    DATE,
    stress_level        SMALLINT CHECK (stress_level BETWEEN 1 AND 10),
    sleep_hours         NUMERIC(3,1),
    onboarding_complete BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- SYMPTOMS
-- ─────────────────────────────────────────
CREATE TABLE symptoms (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50)  -- hormonal, metabolic, mental, dermatological, reproductive
);

INSERT INTO symptoms (name, category) VALUES
    ('Irregular periods',    'reproductive'),
    ('Weight gain',          'metabolic'),
    ('Acne',                 'dermatological'),
    ('Hair loss',            'dermatological'),
    ('Fatigue',              'metabolic'),
    ('Mood swings',          'mental'),
    ('Bloating',             'metabolic'),
    ('Insomnia',             'mental'),
    ('Anxiety',              'mental'),
    ('Brain fog',            'mental'),
    ('Hirsutism',            'hormonal'),
    ('Insulin resistance',   'metabolic'),
    ('Infertility',          'reproductive'),
    ('Ovarian cysts',        'reproductive'),
    ('Low libido',           'hormonal');

CREATE TABLE user_symptoms (
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    symptom_id INT  REFERENCES symptoms(id) ON DELETE CASCADE,
    severity   SMALLINT DEFAULT 3 CHECK (severity BETWEEN 1 AND 5),
    noted_at   TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, symptom_id)
);

-- ─────────────────────────────────────────
-- ALLERGIES & DIETARY RESTRICTIONS
-- ─────────────────────────────────────────
CREATE TABLE allergens (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

INSERT INTO allergens (name) VALUES
    ('Gluten'),('Dairy'),('Nuts'),('Soy'),
    ('Eggs'),('Shellfish'),('Corn'),('Nightshades');

CREATE TABLE user_allergens (
    user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
    allergen_id INT  REFERENCES allergens(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, allergen_id)
);

-- ─────────────────────────────────────────
-- WELLNESS GOALS
-- ─────────────────────────────────────────
CREATE TABLE wellness_goals (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

INSERT INTO wellness_goals (name) VALUES
    ('Lose weight'),
    ('Regulate hormones'),
    ('Reduce inflammation'),
    ('Improve fertility'),
    ('Boost energy'),
    ('Better mental health'),
    ('Improve sleep'),
    ('Clear skin');

CREATE TABLE user_goals (
    user_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    goal_id  INT  REFERENCES wellness_goals(id) ON DELETE CASCADE,
    achieved BOOLEAN DEFAULT FALSE,
    set_at   TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, goal_id)
);

-- ─────────────────────────────────────────
-- DIET PLANS
-- ─────────────────────────────────────────
CREATE TABLE diet_plans (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    plan_type    VARCHAR(30) DEFAULT 'daily',       -- daily, weekly
    total_cal    INT,
    total_protein_g NUMERIC(6,1),
    total_carbs_g   NUMERIC(6,1),
    total_fat_g     NUMERIC(6,1),
    notes        TEXT,
    generated_by VARCHAR(20) DEFAULT 'ai',          -- ai, manual
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, plan_date)
);

CREATE TABLE meals (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    diet_plan_id UUID NOT NULL REFERENCES diet_plans(id) ON DELETE CASCADE,
    meal_type    VARCHAR(20) NOT NULL,              -- breakfast, lunch, dinner, snack
    name         VARCHAR(200) NOT NULL,
    emoji        VARCHAR(10),
    description  TEXT,
    calories     INT,
    protein_g    NUMERIC(5,1),
    carbs_g      NUMERIC(5,1),
    fat_g        NUMERIC(5,1),
    fiber_g      NUMERIC(5,1),
    gi_level     VARCHAR(10),                       -- low, medium, high
    tags         TEXT[],                            -- anti-inflammatory, omega-3, low-gi, etc.
    recipe_url   TEXT,
    sort_order   SMALLINT DEFAULT 0
);

-- ─────────────────────────────────────────
-- DAILY ROUTINES
-- ─────────────────────────────────────────
CREATE TABLE routine_tasks (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_name   VARCHAR(200) NOT NULL,
    category    VARCHAR(50),                        -- nutrition, exercise, mindfulness, sleep
    scheduled_time TIME,
    color_hex   VARCHAR(7),
    is_default  BOOLEAN DEFAULT FALSE,
    sort_order  SMALLINT DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE routine_logs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id     UUID NOT NULL REFERENCES routine_tasks(id) ON DELETE CASCADE,
    log_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    completed   BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    notes       TEXT,
    UNIQUE (user_id, task_id, log_date)
);

-- ─────────────────────────────────────────
-- CYCLE TRACKING
-- ─────────────────────────────────────────
CREATE TABLE cycle_entries (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date   DATE NOT NULL,
    phase        VARCHAR(30),                       -- menstrual, follicular, ovulatory, luteal
    cycle_day    SMALLINT,
    flow_level   VARCHAR(20),                       -- none, light, medium, heavy
    symptoms     TEXT[],
    mood_score   SMALLINT CHECK (mood_score BETWEEN 1 AND 10),
    energy_score SMALLINT CHECK (energy_score BETWEEN 1 AND 10),
    pain_level   SMALLINT CHECK (pain_level BETWEEN 0 AND 10),
    notes        TEXT,
    logged_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, entry_date)
);

-- ─────────────────────────────────────────
-- AI CHAT
-- ─────────────────────────────────────────
CREATE TABLE chat_sessions (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      VARCHAR(200),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at   TIMESTAMPTZ,
    message_count INT DEFAULT 0
);

CREATE TABLE chat_messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id  UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role        VARCHAR(10) NOT NULL CHECK (role IN ('user','assistant')),
    content     TEXT NOT NULL,
    tokens_used INT,
    sent_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, sent_at);

-- ─────────────────────────────────────────
-- COMMUNITY
-- ─────────────────────────────────────────
CREATE TABLE community_groups (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    emoji       VARCHAR(10),
    category    VARCHAR(50),
    color_hex   VARCHAR(7),
    member_count INT DEFAULT 0,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO community_groups (name, description, emoji, category, color_hex) VALUES
    ('PCOS Mental Health Circle',       'Safe space for emotional support and mental wellness', '💜', 'mental_health', '#6B3D6E'),
    ('Hormone-Friendly Recipes',        'Share and discover PCOS-friendly meals', '🥗', 'nutrition', '#7BAE8C'),
    ('Move & Heal — Exercise for PCOS', 'Workouts adapted for PCOS bodies', '🏃', 'fitness', '#E8506A'),
    ('Sleep & Stress Support',          'Rest, recover, and reduce cortisol', '🌙', 'wellness', '#F4956A'),
    ('PCOS & Fertility Journey',        'For those navigating fertility with PCOS', '🌸', 'fertility', '#C4622A');

CREATE TABLE group_members (
    group_id   UUID REFERENCES community_groups(id) ON DELETE CASCADE,
    user_id    UUID REFERENCES users(id) ON DELETE CASCADE,
    joined_at  TIMESTAMPTZ DEFAULT NOW(),
    role       VARCHAR(20) DEFAULT 'member',        -- member, moderator, admin
    PRIMARY KEY (group_id, user_id)
);

CREATE TABLE posts (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id     UUID NOT NULL REFERENCES community_groups(id) ON DELETE CASCADE,
    author_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content      TEXT NOT NULL,
    image_url    TEXT,
    like_count   INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    is_pinned    BOOLEAN DEFAULT FALSE,
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE post_likes (
    post_id  UUID REFERENCES posts(id) ON DELETE CASCADE,
    user_id  UUID REFERENCES users(id) ON DELETE CASCADE,
    liked_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (post_id, user_id)
);

CREATE TABLE comments (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id    UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content    TEXT NOT NULL,
    like_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- EDUCATIONAL CONTENT
-- ─────────────────────────────────────────
CREATE TABLE content_tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO content_tags (name) VALUES
    ('hormones'),('nutrition'),('exercise'),('mental-health'),
    ('fertility'),('insulin'),('sleep'),('supplements'),('skincare'),('recipes');

CREATE TABLE educational_content (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title        VARCHAR(300) NOT NULL,
    content_type VARCHAR(20) NOT NULL,             -- video, article, guide, podcast
    description  TEXT,
    emoji        VARCHAR(10),
    thumbnail_url TEXT,
    content_url  TEXT,
    duration_min SMALLINT,
    author       VARCHAR(200),
    tags         TEXT[],
    view_count   INT DEFAULT 0,
    like_count   INT DEFAULT 0,
    is_featured  BOOLEAN DEFAULT FALSE,
    is_active    BOOLEAN DEFAULT TRUE,
    published_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE content_progress (
    user_id      UUID REFERENCES users(id) ON DELETE CASCADE,
    content_id   UUID REFERENCES educational_content(id) ON DELETE CASCADE,
    progress_pct SMALLINT DEFAULT 0 CHECK (progress_pct BETWEEN 0 AND 100),
    completed    BOOLEAN DEFAULT FALSE,
    bookmarked   BOOLEAN DEFAULT FALSE,
    last_viewed  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, content_id)
);

-- ─────────────────────────────────────────
-- NOTIFICATIONS
-- ─────────────────────────────────────────
CREATE TABLE notifications (
    id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type       VARCHAR(50),                         -- routine_reminder, diet_tip, community_reply, etc.
    title      VARCHAR(200),
    body       TEXT,
    is_read    BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- STREAK & GAMIFICATION
-- ─────────────────────────────────────────
CREATE TABLE user_streaks (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id          UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_streak   INT DEFAULT 0,
    longest_streak   INT DEFAULT 0,
    last_active_date DATE,
    total_points     INT DEFAULT 0,
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────
CREATE INDEX idx_users_email          ON users(email);
CREATE INDEX idx_pcos_profiles_user   ON pcos_profiles(user_id);
CREATE INDEX idx_diet_plans_user_date ON diet_plans(user_id, plan_date);
CREATE INDEX idx_meals_plan           ON meals(diet_plan_id);
CREATE INDEX idx_posts_group          ON posts(group_id, created_at DESC);
CREATE INDEX idx_posts_author         ON posts(author_id);
CREATE INDEX idx_cycle_user_date      ON cycle_entries(user_id, entry_date DESC);
CREATE INDEX idx_notifications_user   ON notifications(user_id, is_read, created_at DESC);
CREATE INDEX idx_content_type         ON educational_content(content_type, is_featured);

-- ─────────────────────────────────────────
-- UPDATED_AT TRIGGER
-- ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated         BEFORE UPDATE ON users         FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_pcos_updated          BEFORE UPDATE ON pcos_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_posts_updated         BEFORE UPDATE ON posts         FOR EACH ROW EXECUTE FUNCTION update_updated_at();
