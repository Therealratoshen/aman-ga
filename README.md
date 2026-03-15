# AMAN GA? - Proof of Concept (POC)

Fully functional POC for payment verification system with auto-approval and fraud detection.

## Project Structure

```
aman-ga-poc/
├── backend/           # FastAPI backend
├── frontend/          # Next.js frontend
├── database/          # SQL schemas
└── README.md
```

## Quick Start

### 1. Setup Supabase

1. Create project at [supabase.com](https://supabase.com)
2. Run `database/schema.sql` in SQL Editor
3. Get your Supabase URL and Key

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Supabase credentials
python main.py
```

Backend runs on `http://localhost:8000`

### 3. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Demo Credentials

- **Admin**: `admin@amanga.id` / `admin123`
- **Finance**: `finance@amanga.id` / `admin123`
- **Test User**: Register new account

## Features

| Feature | Status |
|---------|--------|
| User Registration | ✅ |
| JWT Authentication | ✅ |
| Role-based Access | ✅ |
| Payment Upload | ✅ |
| Auto-Approval (< Rp 1.000) | ✅ |
| Manual Approval | ✅ |
| Service Credits | ✅ |
| Fraud Flagging | ✅ |
| Admin Audit Log | ✅ |

## API Endpoints

### Auth
- `POST /register` - Register new user
- `POST /token` - Login
- `GET /me` - Get current user

### Payment
- `POST /payment/upload` - Upload payment proof
- `GET /payment/my` - Get payment history
- `GET /payment/credits` - Get service credits

### Admin
- `GET /admin/payments/pending` - Get pending payments
- `POST /admin/payment/{id}/approve` - Approve payment
- `POST /admin/payment/{id}/reject` - Reject payment
- `POST /admin/payment/{id}/flag` - Flag fraud

### Service
- `GET /service/use/{type}` - Use service credit

## Services

| Service | Price | Auto-Approve |
|---------|-------|--------------|
| CEK_DASAR | Rp 1.000 | ✅ Yes |
| CEK_DEEP | Rp 15.000 | ❌ Manual |
| CEK_PLUS | Rp 45.000 | ❌ Manual |

## Auto-Approval Rules

- Amount ≤ Rp 1.000
- Service type = CEK_DASAR
- No fraud history
- Passes 10% random audit

## Next Steps

1. Add Supabase Storage for images
2. Add WhatsApp notifications
3. Add AI fraud detection
4. Add payment gateway (Midtrans)
5. Production security hardening

## License

MIT
