# 🛡️ Aman ga? - Payment Verification System

> **Tanya dulu, transfer kemudian.** (Ask first, transfer later.)

A complete payment verification system with auto-approval, fraud detection, and admin management for Indonesian market.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Frontend Pages](#-frontend-pages)
- [Environment Variables](#-environment-variables)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### For Users
- 🔐 **Secure Authentication** - JWT-based login/register
- 💳 **Payment Upload** - Upload payment proof with image
- ⚡ **Auto-Approval** - Instant activation for low-risk payments (< Rp 1.000)
- 📊 **Dashboard** - View service credits and payment history
- 🔔 **Notifications** - WhatsApp and Email notifications

### For Admins
- 👥 **User Management** - View and manage users
- ✅ **Payment Review** - Approve/reject pending payments
- 🚩 **Fraud Detection** - Flag suspicious activities
- 📈 **Dashboard Stats** - Real-time payment statistics
- 📝 **Audit Log** - Complete admin action history

### Security Features
- 🛡️ **Fraud Detection** - Risk scoring system
- 🔒 **JWT Authentication** - Secure token-based auth
- 👮 **Role-Based Access** - USER, ADMIN, FINANCE roles
- 📸 **Image Validation** - Payment proof verification
- ⚠️ **Auto-Suspension** - Automatic action on fraud detection

---

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **File Upload:** aiofiles
- **Notifications:** SendGrid (email), Fonnte (WhatsApp)

### Frontend
- **Framework:** Next.js 14 (React)
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **State:** React Hooks

---

## 📦 Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 18 or higher
- **Supabase Account:** Free tier works ([supabase.com](https://supabase.com))
- **Optional:** SendGrid account for emails, Fonnte for WhatsApp

---

## 🚀 Quick Start

### Step 1: Clone Repository

```bash
git clone https://github.com/Therealratoshen/aman-ga.git
cd aman-ga
```

### Step 2: Setup Supabase (Required)

1. Go to [supabase.com](https://supabase.com) and create a free project
2. Go to **SQL Editor** → **New Query**
3. Copy and paste contents of `database/schema.sql`
4. Click **Run**
5. Go to **Settings** → **API** and copy:
   - Project URL
   - anon/public key

### Step 3: Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
nano .env  # or use your preferred editor
```

**Edit `backend/.env`:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SECRET_KEY=your-secret-key-min-32-characters
```

**Run Backend:**
```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### Step 4: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 📖 API Documentation

### Authentication Endpoints

#### Register User
```bash
POST /register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "081234567890"
}
```

#### Login
```bash
POST /token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123

Response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "email": "user@example.com",
    "role": "USER"
  }
}
```

#### Get Current User
```bash
GET /me
Authorization: Bearer <token>
```

### Payment Endpoints

#### Upload Payment Proof
```bash
POST /payment/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form data:
- service_type: CEK_DASAR
- amount: 1000
- payment_method: BANK_TRANSFER
- bank_name: BCA
- transaction_id: TRX123456
- transaction_date: 2024-01-01T10:00:00
- proof_image: <file>
```

#### Get My Payments
```bash
GET /payment/my
Authorization: Bearer <token>
```

#### Get My Credits
```bash
GET /payment/credits
Authorization: Bearer <token>
```

### Admin Endpoints

#### Get Pending Payments
```bash
GET /admin/payments/pending
Authorization: Bearer <admin-token>
```

#### Approve Payment
```bash
POST /admin/payment/{payment_id}/approve?notes=Verified
Authorization: Bearer <admin-token>
```

#### Reject Payment
```bash
POST /admin/payment/{payment_id}/reject?reason=Invalid+proof
Authorization: Bearer <admin-token>
```

#### Flag as Fraud
```bash
POST /admin/payment/{payment_id}/flag?flag_type=FAKE_PROOF&severity=HIGH
Authorization: Bearer <admin-token>
```

### Service Endpoints

#### Use Service Credit
```bash
GET /service/use/{service_type}
Authorization: Bearer <token>

Response:
{
  "success": true,
  "service_type": "CEK_DASAR",
  "credit_remaining": 0,
  "result": {
    "risk_score": 45,
    "risk_level": "MEDIUM",
    "indicators": ["No negative records found"],
    "recommendation": "Proceed with caution"
  }
}
```

---

## 🗄️ Database Schema

### Tables

#### users
```sql
- id: UUID (primary key)
- email: TEXT (unique)
- password_hash: TEXT
- full_name: TEXT
- phone: TEXT
- role: USER | ADMIN | FINANCE
- status: ACTIVE | SUSPENDED | BANNED
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### payment_proofs
```sql
- id: UUID (primary key)
- user_id: UUID (foreign key)
- service_type: CEK_DASAR | CEK_DEEP | CEK_PLUS | WALLET_TOPUP
- amount: INTEGER
- payment_method: BANK_TRANSFER | GOPAY | OVO | DANA
- bank_name: TEXT
- transaction_id: TEXT
- transaction_date: TIMESTAMP
- proof_image_url: TEXT
- status: PENDING | APPROVED | REJECTED | AUTO_APPROVED | FLAGGED
- verification_notes: TEXT
- verified_by: UUID
- verified_at: TIMESTAMP
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

#### service_credits
```sql
- id: UUID (primary key)
- user_id: UUID (foreign key)
- service_type: CEK_DASAR | CEK_DEEP | CEK_PLUS
- quantity: INTEGER
- used_quantity: INTEGER
- status: ACTIVE | USED | EXPIRED | REVOKED
- payment_proof_id: UUID (foreign key)
- expires_at: TIMESTAMP
- created_at: TIMESTAMP
- used_at: TIMESTAMP
```

#### fraud_flags
```sql
- id: UUID (primary key)
- user_id: UUID (foreign key)
- payment_proof_id: UUID (foreign key)
- flag_type: FAKE_PROOF | DUPLICATE_PROOF | MANIPULATED_IMAGE | SUSPICIOUS_PATTERN
- severity: LOW | MEDIUM | HIGH | CRITICAL
- status: PENDING_REVIEW | CONFIRMED | FALSE_POSITIVE
- action_taken: WARNING | SUSPENSION | BAN | NO_ACTION
- reviewed_by: UUID
- reviewed_at: TIMESTAMP
- created_at: TIMESTAMP
```

#### admin_audit_log
```sql
- id: UUID (primary key)
- admin_id: UUID (foreign key)
- action: TEXT
- target_type: TEXT
- target_id: UUID
- details: JSONB
- ip_address: TEXT
- created_at: TIMESTAMP
```

---

## 🎨 Frontend Pages

| Page | Route | Description |
|------|-------|-------------|
| Login/Register | `/` | User authentication |
| Dashboard | `/dashboard` | User dashboard with credits |
| Payment History | `/payment` | View all payments |
| Admin Panel | `/admin` | Admin management panel |

---

## 🔧 Environment Variables

### Backend (.env)

```env
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SECRET_KEY=your-secret-key-min-32-characters

# Optional (for notifications)
WHATSAPP_API_KEY=your-fonnte-token
WHATSAPP_API_URL=https://api.fonnte.com/send
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_FROM_EMAIL=noreply@amanga.id
SENDGRID_FROM_NAME=Aman ga?
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### Test with Demo Credentials

**Admin Account:**
- Email: `admin@amanga.id`
- Password: `admin123`

**Finance Account:**
- Email: `finance@amanga.id`
- Password: `admin123`

### Test Flow

1. **Register new user** at http://localhost:3000
2. **Login** with new account
3. **Purchase Cek Dasar** (Rp 1.000 - auto-approved)
4. **Upload payment proof** (any image file)
5. **See instant activation** in dashboard
6. **Use the service** from credits section
7. **Login as admin** to review payments

### Test Admin Features

1. Login as `admin@amanga.id`
2. Go to **Admin Panel**
3. **Approve/Reject** pending payments
4. **Flag fraud** to test auto-suspension
5. View **audit logs**

---

## 🚀 Deployment

### Backend (Railway/Render)

1. Create new project on [Railway](https://railway.app) or [Render](https://render.com)
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`

### Frontend (Vercel)

1. Push code to GitHub
2. Import project on [Vercel](https://vercel.com)
3. Set build command: `npm run build`
4. Set output directory: `.next`
5. Add environment variable: `NEXT_PUBLIC_API_URL`

### Database

- Use [Supabase](https://supabase.com) for production
- Enable Row Level Security (RLS)
- Add proper indexes for performance

---

## 📞 Support & Documentation

- **API Key Setup Guide:** [`API-KEY-SETUP.md`](./API-KEY-SETUP.md)
- **Quick Start Guide:** [`QUICKSTART.md`](./QUICKSTART.md)
- **API Documentation:** http://localhost:8000/docs

---

## 📄 License

MIT License - feel free to use for learning or commercial projects.

---

## 🙏 Acknowledgments

Built with ❤️ for Indonesian market safety.

**Aman ga?** - Tanya dulu, transfer kemudian.
