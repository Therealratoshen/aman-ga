-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    phone TEXT,
    role TEXT CHECK (role IN ('USER', 'ADMIN', 'FINANCE')) DEFAULT 'USER',
    status TEXT CHECK (status IN ('ACTIVE', 'SUSPENDED', 'BANNED')) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment Proofs Table
CREATE TABLE payment_proofs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    service_type TEXT CHECK (service_type IN ('CEK_DASAR', 'CEK_DEEP', 'CEK_PLUS', 'WALLET_TOPUP')),
    amount INTEGER NOT NULL CHECK (amount >= 100 AND amount <= 100000000),
    payment_method TEXT CHECK (payment_method IN ('BANK_TRANSFER', 'GOPAY', 'OVO', 'DANA', 'LINKAJA')),
    bank_name TEXT CHECK (bank_name IN ('BCA', 'BRI', 'BNI', 'MANDIRI', 'PERMATA', 'DANAMON', 'CIMB', 'MAYBANK', 'BTN', 'OTHER')),
    transaction_id TEXT NOT NULL CHECK (LENGTH(transaction_id) >= 5 AND LENGTH(transaction_id) <= 50),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    proof_image_url TEXT NOT NULL,
    proof_image_hash TEXT,
    proof_image_metadata JSONB,
    ocr_extracted_amount INTEGER,
    ocr_extracted_transaction_id TEXT,
    ocr_extracted_date TIMESTAMP WITH TIME ZONE,
    ocr_extracted_bank TEXT,
    ocr_confidence_score DECIMAL(3,2) CHECK (ocr_confidence_score >= 0 AND ocr_confidence_score <= 1),
    ocr_matches_form BOOLEAN DEFAULT FALSE,
    ocr_mismatches JSONB,
    -- Virtual Account validation fields
    va_validation_enabled BOOLEAN DEFAULT TRUE,
    va_matched_accounts JSONB,  -- Stores array of matched VA IDs
    va_first_level_status TEXT CHECK (va_first_level_status IN ('PENDING', 'VALIDATED', 'REJECTED')) DEFAULT 'PENDING',
    va_second_level_status TEXT CHECK (va_second_level_status IN ('PENDING', 'VALIDATED', 'REJECTED', 'SKIPPED')) DEFAULT 'PENDING',
    va_validation_notes TEXT,
    va_validation_score DECIMAL(3,2) CHECK (va_validation_score >= 0 AND va_validation_score <= 1),
    -- Transaction validation fields
    transaction_validation_enabled BOOLEAN DEFAULT TRUE,
    transaction_validation_status TEXT CHECK (transaction_validation_status IN ('PENDING', 'VALIDATED', 'REJECTED')) DEFAULT 'PENDING',
    transaction_validation_notes TEXT,
    -- Amount validation fields
    amount_validation_enabled BOOLEAN DEFAULT TRUE,
    amount_extracted INTEGER,
    amount_expected INTEGER,
    amount_variance_percentage DECIMAL(5,2),
    amount_validation_status TEXT CHECK (amount_validation_status IN ('PENDING', 'VALIDATED', 'REJECTED')) DEFAULT 'PENDING',
    amount_validation_notes TEXT,
    -- Debit status validation fields
    debit_status_validation_enabled BOOLEAN DEFAULT TRUE,
    is_debited BOOLEAN DEFAULT FALSE,
    debit_status TEXT CHECK (debit_status IN ('PENDING', 'VERIFIED', 'FAILED')) DEFAULT 'PENDING',
    debit_verification_method TEXT CHECK (debit_verification_method IN ('OCR', 'API', 'MANUAL')) DEFAULT 'OCR',
    debit_verification_notes TEXT,
    debit_timestamp_verified TIMESTAMP WITH TIME ZONE,
    -- Original fields continued
    image_manipulation_detected BOOLEAN DEFAULT FALSE,
    image_risk_level TEXT CHECK (image_risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'UNKNOWN')),
    image_quality_score DECIMAL(3,2),
    fraud_risk_score INTEGER CHECK (fraud_risk_score >= 0 AND fraud_risk_score <= 200),
    fraud_risk_factors JSONB,
    status TEXT CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'AUTO_APPROVED', 'FLAGGED')) DEFAULT 'PENDING',
    verification_notes TEXT,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service Credits Table
CREATE TABLE service_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    service_type TEXT CHECK (service_type IN ('CEK_DASAR', 'CEK_DEEP', 'CEK_PLUS')),
    quantity INTEGER DEFAULT 1,
    used_quantity INTEGER DEFAULT 0,
    status TEXT CHECK (status IN ('ACTIVE', 'USED', 'EXPIRED', 'REVOKED')) DEFAULT 'ACTIVE',
    payment_proof_id UUID REFERENCES payment_proofs(id),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '90 days',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    used_at TIMESTAMP WITH TIME ZONE
);

-- Fraud Flags Table
CREATE TABLE fraud_flags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    payment_proof_id UUID REFERENCES payment_proofs(id),
    flag_type TEXT CHECK (flag_type IN ('FAKE_PROOF', 'DUPLICATE_PROOF', 'MANIPULATED_IMAGE', 'SUSPICIOUS_PATTERN', 'INVALID_VA')),
    severity TEXT CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status TEXT CHECK (status IN ('PENDING_REVIEW', 'CONFIRMED', 'FALSE_POSITIVE')) DEFAULT 'PENDING_REVIEW',
    action_taken TEXT CHECK (action_taken IN ('WARNING', 'SUSPENSION', 'BAN', 'NO_ACTION')),
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Admin Audit Log
CREATE TABLE admin_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    target_type TEXT,
    target_id UUID,
    details JSONB,
    ip_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- OCR Feedback Table (for self-learning)
CREATE TABLE ocr_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_proof_id UUID REFERENCES payment_proofs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    feedback_type TEXT CHECK (feedback_type IN ('CORRECTION', 'CONFIRMATION', 'FLAG')),
    corrected_amount INTEGER,
    corrected_transaction_id TEXT,
    corrected_date TEXT,
    corrected_bank TEXT,
    corrected_fields JSONB,
    notes TEXT,
    is_legitimate_receipt BOOLEAN,
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    would_recommend BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Receipt Format Suggestions Table
CREATE TABLE receipt_format_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider TEXT NOT NULL,
    suggested_by UUID REFERENCES users(id),
    suggested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    feedback JSONB,
    status TEXT CHECK (status IN ('PENDING', 'REVIEWED', 'IMPLEMENTED', 'REJECTED')) DEFAULT 'PENDING',
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Virtual Accounts Configuration Table
CREATE TABLE virtual_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    va_id TEXT UNIQUE NOT NULL,  -- Internal ID like 'va_bca'
    name TEXT NOT NULL,
    bank_code TEXT NOT NULL,
    account_number TEXT NOT NULL,
    description TEXT,
    pattern TEXT NOT NULL,  -- Regex pattern to match in OCR text
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_payment_proofs_user ON payment_proofs(user_id);
CREATE INDEX idx_payment_proofs_status ON payment_proofs(status);
CREATE INDEX idx_payment_proofs_va_first_level_status ON payment_proofs(va_first_level_status);
CREATE INDEX idx_payment_proofs_va_second_level_status ON payment_proofs(va_second_level_status);
CREATE INDEX idx_service_credits_user ON service_credits(user_id);
CREATE INDEX idx_fraud_flags_user ON fraud_flags(user_id);
CREATE INDEX idx_ocr_feedback_payment ON ocr_feedback(payment_proof_id);
CREATE INDEX idx_ocr_feedback_type ON ocr_feedback(feedback_type);

-- Insert the 5 Virtual Accounts
INSERT INTO virtual_accounts (va_id, name, bank_code, account_number, description, pattern) VALUES
('va_bca', 'BCA Virtual Account', 'BCA', '8888', 'BCA Virtual Account for payment verification', '(?i)(?:8888\d{8}|BCA.*8888|\b8888\d{8}\b)'),
('va_bri', 'BRI Virtual Account', 'BRI', '9999', 'BRI Virtual Account for payment verification', '(?i)(?:9999\d{7}|BRI.*9999|\b9999\d{7}\b)'),
('va_mandiri', 'Mandiri Virtual Account', 'MANDIRI', '7777', 'Mandiri Virtual Account for payment verification', '(?i)(?:7777\d{8}|MANDIRI.*7777|\b7777\d{8}\b)'),
('va_bni', 'BNI Virtual Account', 'BNI', '6666', 'BNI Virtual Account for payment verification', '(?i)(?:6666\d{8}|BNI.*6666|\b6666\d{8}\b)'),
('va_permata', 'Permata Virtual Account', 'PERMATA', '5555', 'Permata Virtual Account for payment verification', '(?i)(?:5555\d{8}|PERMATA.*5555|\b5555\d{8}\b)');

-- Create admin user (password: admin123)
INSERT INTO users (email, password_hash, role, full_name)
VALUES (
    'admin@amanga.id',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu',
    'ADMIN',
    'System Administrator'
);