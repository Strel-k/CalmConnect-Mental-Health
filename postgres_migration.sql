-- PostgreSQL Migration Script - Converted from SQLite
-- Generated for Railway PostgreSQL deployment
-- Run this script in Railway's PostgreSQL database console

-- Create sequences for auto-increment fields
CREATE SEQUENCE IF NOT EXISTS django_migrations_id_seq;
CREATE SEQUENCE IF NOT EXISTS django_content_type_id_seq;
CREATE SEQUENCE IF NOT EXISTS auth_permission_id_seq;
CREATE SEQUENCE IF NOT EXISTS auth_group_id_seq;
CREATE SEQUENCE IF NOT EXISTS custom_user_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_dassresult_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_counselor_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_report_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_feedback_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_appointment_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_livesession_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_sessionmessage_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_sessionparticipant_id_seq;
CREATE SEQUENCE IF NOT EXISTS mentalhealth_notification_id_seq;

-- Create tables with PostgreSQL syntax
CREATE TABLE IF NOT EXISTS django_migrations (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('django_migrations_id_seq'),
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS django_content_type (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('django_content_type_id_seq'),
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_permission (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('auth_permission_id_seq'),
    content_type_id INTEGER NOT NULL REFERENCES django_content_type(id),
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_group (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('auth_group_id_seq'),
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id INTEGER NOT NULL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES auth_group(id),
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id)
);

CREATE TABLE IF NOT EXISTS custom_user (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('custom_user_id_seq'),
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    email_verified BOOLEAN NOT NULL,
    verification_token VARCHAR(64) NULL,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    age INTEGER NULL CHECK (age >= 0),
    full_name VARCHAR(255) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    college VARCHAR(10) NOT NULL,
    program VARCHAR(255) NOT NULL,
    year_level VARCHAR(2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    profile_picture VARCHAR(100) NULL
);

CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS mentalhealth_relaxationlog (
    id INTEGER NOT NULL PRIMARY KEY,
    exercise_type VARCHAR(100) NOT NULL,
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds >= 0),
    timestamp TIMESTAMP NOT NULL,
    user_id BIGINT NOT NULL REFERENCES custom_user(id)
);

CREATE TABLE IF NOT EXISTS mentalhealth_dassresult (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_dassresult_id_seq'),
    date_taken TIMESTAMP NOT NULL,
    depression_score INTEGER NOT NULL,
    anxiety_score INTEGER NOT NULL,
    stress_score INTEGER NOT NULL,
    depression_severity VARCHAR(50) NOT NULL,
    anxiety_severity VARCHAR(50) NOT NULL,
    answers TEXT NOT NULL CHECK (json_valid(answers) OR answers IS NULL),
    user_id BIGINT NOT NULL REFERENCES custom_user(id),
    stress_severity VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS mentalhealth_counselor (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_counselor_id_seq'),
    name VARCHAR(100) NOT NULL,
    unit VARCHAR(100) NOT NULL,
    rank VARCHAR(100) NOT NULL,
    bio TEXT NOT NULL,
    image VARCHAR(100) NULL,
    available_days TEXT NOT NULL CHECK (json_valid(available_days) OR available_days IS NULL),
    is_active BOOLEAN NOT NULL,
    email VARCHAR(254) NULL,
    user_id BIGINT NULL UNIQUE REFERENCES custom_user(id),
    available_end_time TIME NULL,
    available_start_time TIME NULL,
    day_schedules TEXT NOT NULL CHECK (json_valid(day_schedules) OR day_schedules IS NULL)
);

CREATE TABLE IF NOT EXISTS mentalhealth_report (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_report_id_seq'),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    report_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    counselor_id BIGINT NOT NULL REFERENCES mentalhealth_counselor(id),
    user_id BIGINT NULL REFERENCES custom_user(id),
    appointment_id BIGINT NULL REFERENCES mentalhealth_appointment(id)
);

CREATE TABLE IF NOT EXISTS mentalhealth_feedback (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_feedback_id_seq'),
    overall_rating INTEGER NULL,
    professionalism_rating INTEGER NULL,
    helpfulness_rating INTEGER NULL,
    recommend_rating INTEGER NULL,
    positive_feedback TEXT NOT NULL,
    improvement_feedback TEXT NOT NULL,
    additional_comments TEXT NOT NULL,
    submitted_at TIMESTAMP NOT NULL,
    skipped BOOLEAN NOT NULL,
    appointment_id BIGINT NOT NULL REFERENCES mentalhealth_appointment(id),
    counselor_id BIGINT NOT NULL REFERENCES mentalhealth_counselor(id),
    user_id BIGINT NOT NULL REFERENCES custom_user(id)
);

CREATE TABLE IF NOT EXISTS mentalhealth_appointment (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_appointment_id_seq'),
    date DATE NOT NULL,
    time TIME NOT NULL,
    services TEXT NOT NULL CHECK (json_valid(services) OR services IS NULL),
    reason TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    course_section VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    cancellation_deadline TIMESTAMP NULL,
    cancellation_reason TEXT NOT NULL,
    cancellation_token VARCHAR(64) NULL UNIQUE,
    user_id BIGINT NOT NULL REFERENCES custom_user(id),
    counselor_id BIGINT NOT NULL REFERENCES mentalhealth_counselor(id),
    dass_result_id BIGINT NULL REFERENCES mentalhealth_dassresult(id),
    cancelled_at TIMESTAMP NULL,
    notes TEXT NULL,
    session_type VARCHAR(20) NOT NULL,
    video_call_url VARCHAR(200) NULL
);

CREATE TABLE IF NOT EXISTS mentalhealth_livesession (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_livesession_id_seq'),
    session_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    room_id VARCHAR(100) NOT NULL UNIQUE,
    session_token VARCHAR(255) NOT NULL,
    meeting_url VARCHAR(200) NOT NULL,
    scheduled_start TIMESTAMP NOT NULL,
    scheduled_end TIMESTAMP NOT NULL,
    actual_start TIMESTAMP NULL,
    actual_end TIMESTAMP NULL,
    notes TEXT NOT NULL,
    recording_url VARCHAR(200) NOT NULL,
    session_data TEXT NOT NULL CHECK (json_valid(session_data) OR session_data IS NULL),
    is_recorded BOOLEAN NOT NULL,
    consent_given BOOLEAN NOT NULL,
    privacy_level VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    appointment_id BIGINT NOT NULL UNIQUE REFERENCES mentalhealth_appointment(id)
);

CREATE TABLE IF NOT EXISTS mentalhealth_sessionmessage (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_sessionmessage_id_seq'),
    message TEXT NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    sender_id BIGINT NOT NULL REFERENCES custom_user(id),
    session_id BIGINT NOT NULL REFERENCES mentalhealth_livesession(id)
);

CREATE TABLE IF NOT EXISTS mentalhealth_sessionparticipant (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_sessionparticipant_id_seq'),
    role VARCHAR(20) NOT NULL,
    joined_at TIMESTAMP NOT NULL,
    left_at TIMESTAMP NULL,
    connection_quality VARCHAR(20) NOT NULL,
    session_id BIGINT NOT NULL REFERENCES mentalhealth_livesession(id),
    user_id BIGINT NOT NULL REFERENCES custom_user(id)
);

CREATE TABLE IF NOT EXISTS mentalhealth_notification (
    id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('mentalhealth_notification_id_seq'),
    message TEXT NOT NULL,
    type VARCHAR(20) NOT NULL,
    url VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL,
    read BOOLEAN NOT NULL,
    dismissed BOOLEAN NOT NULL,
    user_id BIGINT NOT NULL REFERENCES custom_user(id),
    priority VARCHAR(10) NOT NULL,
    category VARCHAR(20) NOT NULL,
    action_url VARCHAR(200) NULL,
    action_text VARCHAR(50) NULL,
    expires_at TIMESTAMP NULL,
    metadata TEXT NOT NULL CHECK (json_valid(metadata) OR metadata IS NULL)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS django_session_expire_date_a5c62663 ON django_session(expire_date);
CREATE INDEX IF NOT EXISTS mentalhealth_relaxationlog_user_id_67408ce8 ON mentalhealth_relaxationlog(user_id);
CREATE INDEX IF NOT EXISTS mentalhealth_dassresult_user_id_894d8140 ON mentalhealth_dassresult(user_id);
CREATE INDEX IF NOT EXISTS mentalhealth_report_counselor_id_afeeb10e ON mentalhealth_report(counselor_id);
CREATE INDEX IF NOT EXISTS mentalhealth_report_user_id_3b752968 ON mentalhealth_report(user_id);
CREATE INDEX IF NOT EXISTS mentalhealth_report_appointment_id_680e9f34 ON mentalhealth_report(appointment_id);
CREATE INDEX IF NOT EXISTS mentalhealth_feedback_appointment_id_88ddd43a ON mentalhealth_feedback(appointment_id);
CREATE INDEX IF NOT EXISTS mentalhealth_feedback_counselor_id_68ca5b30 ON mentalhealth_feedback(counselor_id);
CREATE INDEX IF NOT EXISTS mentalhealth_feedback_user_id_f4f53b9f ON mentalhealth_feedback(user_id);
CREATE INDEX IF NOT EXISTS mentalhealth_appointment_user_id_411474ed ON mentalhealth_appointment(user_id);
CREATE INDEX IF NOT EXISTS mentalhealth_appointment_counselor_id_611341d2 ON mentalhealth_appointment(counselor_id);
CREATE INDEX IF NOT EXISTS mentalhealth_appointment_dass_result_id_0904d2af ON mentalhealth_appointment(dass_result_id);
CREATE INDEX IF NOT EXISTS mentalhealth_sessionmessage_sender_id_fd2ed8d8 ON mentalhealth_sessionmessage(sender_id);
CREATE INDEX IF NOT EXISTS mentalhealth_sessionmessage_session_id_26d36977 ON mentalhealth_sessionmessage(session_id);
CREATE INDEX IF NOT EXISTS mentalhealth_sessionparticipant_session_id_d581f83b ON mentalhealth_sessionparticipant(session_id);
CREATE INDEX IF NOT EXISTS mentalhealth_sessionparticipant_user_id_f021e1d7 ON mentalhealth_sessionparticipant(user_id);
CREATE INDEX IF NOT EXISTS mentalhealth_notification_user_id_22db40c4 ON mentalhealth_notification(user_id);

-- Insert basic data (content types and permissions)
-- Note: You may need to adjust these INSERT statements based on your specific data

COMMIT;