-- Emergency SQL script to create missing tables
-- Run this directly in Railway's PostgreSQL database

-- Create mentalhealth_securedassresult table
CREATE TABLE IF NOT EXISTS mentalhealth_securedassresult (
    dassresult_ptr_id INTEGER NOT NULL PRIMARY KEY,
    encrypted_answers TEXT,
    encrypted_depression_score TEXT,
    encrypted_anxiety_score TEXT,
    encrypted_stress_score TEXT,
    data_hash VARCHAR(64),
    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
    consent_timestamp TIMESTAMP WITH TIME ZONE,
    encryption_version VARCHAR(10) NOT NULL DEFAULT 'v1',
    access_count INTEGER NOT NULL DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE,
    CONSTRAINT mentalhealth_securedassresult_dassresult_ptr_id_fkey
        FOREIGN KEY (dassresult_ptr_id)
        REFERENCES mentalhealth_dassresult(id) DEFERRABLE INITIALLY DEFERRED
);

-- Create mentalhealth_dassdataretentionpolicy table
CREATE TABLE IF NOT EXISTS mentalhealth_dassdataretentionpolicy (
    id SERIAL NOT NULL PRIMARY KEY,
    policy_type VARCHAR(20) NOT NULL DEFAULT 'standard',
    applied_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retention_until TIMESTAMP WITH TIME ZONE,
    reason TEXT,
    approved_by_id INTEGER,
    user_id INTEGER NOT NULL,
    CONSTRAINT mentalhealth_dassdataretentionpolicy_policy_type_check
        CHECK (policy_type IN ('standard', 'extended', 'anonymized', 'deleted')),
    CONSTRAINT mentalhealth_dassdataretentionpolicy_approved_by_id_fkey
        FOREIGN KEY (approved_by_id)
        REFERENCES mentalhealth_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT mentalhealth_dassdataretentionpolicy_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES mentalhealth_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT mentalhealth_dassdataretentionpolicy_user_id_policy_type_uniq
        UNIQUE (user_id, policy_type)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS mentalhealth_securedassresult_access_count_idx
    ON mentalhealth_securedassresult(access_count);
CREATE INDEX IF NOT EXISTS mentalhealth_securedassresult_last_accessed_idx
    ON mentalhealth_securedassresult(last_accessed);
CREATE INDEX IF NOT EXISTS mentalhealth_dassdataretentionpolicy_user_id_idx
    ON mentalhealth_dassdataretentionpolicy(user_id);
CREATE INDEX IF NOT EXISTS mentalhealth_dassdataretentionpolicy_approved_by_id_idx
    ON mentalhealth_dassdataretentionpolicy(approved_by_id);

-- Verify tables were created
SELECT 'mentalhealth_securedassresult' as table_name,
       CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'mentalhealth_securedassresult')
            THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT 'mentalhealth_dassdataretentionpolicy' as table_name,
       CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables
                        WHERE table_name = 'mentalhealth_dassdataretentionpolicy')
            THEN 'EXISTS' ELSE 'MISSING' END as status;