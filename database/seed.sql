-- Seed data for testing

-- Test users
INSERT INTO users (email, password_hash, role, full_name, phone) 
VALUES 
    ('user1@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'USER', 'Test User 1', '081234567890'),
    ('user2@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'USER', 'Test User 2', '081234567891'),
    ('finance@amanga.id', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', 'FINANCE', 'Finance Team', '081234567892');

-- Sample payment proofs
INSERT INTO payment_proofs (user_id, service_type, amount, payment_method, bank_name, transaction_id, transaction_date, proof_image_url, status)
SELECT 
    u.id,
    'CEK_DASAR',
    1000,
    'BANK_TRANSFER',
    'BCA',
    'TRX001',
    NOW(),
    'https://storage.example.com/proof1.png',
    'AUTO_APPROVED'
FROM users u WHERE u.email = 'user1@test.com';

-- Sample service credits
INSERT INTO service_credits (user_id, service_type, quantity, used_quantity, status, payment_proof_id)
SELECT 
    u.id,
    'CEK_DASAR',
    1,
    0,
    'ACTIVE',
    pp.id
FROM users u, payment_proofs pp 
WHERE u.email = 'user1@test.com' AND pp.user_id = u.id;
