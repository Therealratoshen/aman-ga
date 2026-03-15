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
    amount INTEGER NOT NULL,
    payment_method TEXT CHECK (payment_method IN ('BANK_TRANSFER', 'GOPAY', 'OVO', 'DANA')),
    bank_name TEXT,
    transaction_id TEXT,
    transaction_date TIMESTAMP WITH TIME ZONE,
    proof_image_url TEXT NOT NULL,
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
    flag_type TEXT CHECK (flag_type IN ('FAKE_PROOF', 'DUPLICATE_PROOF', 'MANIPULATED_IMAGE', 'SUSPICIOUS_PATTERN')),
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

-- Indexes
CREATE INDEX idx_payment_proofs_user ON payment_proofs(user_id);
CREATE INDEX idx_payment_proofs_status ON payment_proofs(status);
CREATE INDEX idx_service_credits_user ON service_credits(user_id);
CREATE INDEX idx_fraud_flags_user ON fraud_flags(user_id);

-- Create admin user (password: admin123)
INSERT INTO users (email, password_hash, role, full_name) 
VALUES (
    'admin@amanga.id',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu',
    'ADMIN',
    'System Administrator'
);
