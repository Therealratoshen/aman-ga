# 🛡️ Aman ga? - Payment Verification System

> **Tanya dulu, transfer kemudian.** (Ask first, transfer later.)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com)

A complete **payment verification system** with auto-approval, fraud detection, and admin management designed for the Indonesian market.

---

## 🎯 What is Aman ga?

**Aman ga?** helps Indonesians verify if online transactions are safe before transferring money. Users upload payment proofs, get instant or verified approval, and receive service credits for fraud checks.

### Key Features

- ⚡ **Auto-Approval** - Payments < Rp 1.000 approved instantly
- 🛡️ **Fraud Detection** - Risk scoring and pattern analysis
- 👮 **Admin Dashboard** - Manual review and fraud flagging
- 📱 **Responsive UI** - Works on mobile and desktop
- 🔔 **Notifications** - WhatsApp & Email alerts (optional)
- 🎭 **Mock Mode** - Test without external dependencies

---

## 🚀 Quick Start (2 Options)

### Option 1: Mock Mode (Recommended for Testing) ⭐

**No external services needed!** Test everything locally.

```bash
# Clone repository
git clone https://github.com/Therealratoshen/aman-ga.git
cd aman-ga

# Backend (Terminal 1)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

**Open:** http://localhost:3000

**Login with:**
- Email: `admin@amanga.id`
- Password: `admin123`

---

### Option 2: Production Mode (With Supabase)

For persistent data and production use:

1. **Create free Supabase project:** https://supabase.com
2. **Run `database/schema.sql`** in SQL Editor
3. **Copy credentials** to `backend/.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```
4. **Restart backend**

See [QUICKSTART.md](./QUICKSTART.md) for detailed setup.

---

## 📋 Demo Credentials

| Role | Email | Password | Features |
|------|-------|----------|----------|
| **Admin** | admin@amanga.id | admin123 | Full access, fraud flagging |
| **Finance** | finance@amanga.id | admin123 | Approve/reject payments |
| **User** | Register new | Your choice | Purchase & use services |

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ──────> │   Backend    │ ──────> │  Database   │
│  Next.js 14 │  HTTP   │  FastAPI     │  SQL    │  Supabase   │
│  React      │  JSON   │  Python      │         │  PostgreSQL │
│  Tailwind   │         │  JWT Auth    │         │  (or Mock)  │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              v
                       ┌──────────────┐
                       │  Services    │
                       │  WhatsApp    │
                       │  SendGrid    │
                       │  Fraud AI    │
                       └──────────────┘
```

---

## 📁 Project Structure

```
aman-ga/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints (414 lines)
│   ├── auth.py                # JWT authentication
│   ├── database.py            # Database client (Supabase or Mock)
│   ├── mock_database.py       # In-memory mock database ⭐ NEW
│   ├── models.py              # Pydantic schemas
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment template
│   └── services/
│       ├── payment.py         # Payment processing
│       ├── fraud.py           # Fraud detection
│       └── notification.py    # WhatsApp/Email
│
├── frontend/                   # Next.js frontend
│   ├── pages/
│   │   ├── index.js           # Login/Register
│   │   ├── dashboard.js       # User dashboard
│   │   ├── admin.js           # Admin panel
│   │   └── payment.js         # Payment history
│   ├── components/
│   │   ├── PaymentUpload.js   # Upload modal
│   │   ├── ServiceCard.js     # Service pricing
│   │   └── AdminDashboard.js  # Admin view
│   ├── styles/globals.css     # Tailwind CSS
│   ├── package.json
│   └── next.config.js
│
├── database/
│   ├── schema.sql             # Database schema
│   └── seed.sql               # Test data
│
└── docs/
    ├── README.md              # This file
    ├── QUICKSTART.md          # Setup guide
    ├── API-KEY-SETUP.md       # API key acquisition
    └── TEST-REVIEW.md         # Code review report
```

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Register new user | ❌ |
| POST | `/token` | Login (get JWT token) | ❌ |
| GET | `/me` | Get current user | ✅ |

### Payment

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/payment/upload` | Upload payment proof | ✅ |
| GET | `/payment/my` | Get payment history | ✅ |
| GET | `/payment/credits` | Get service credits | ✅ |

### Admin (Requires ADMIN or FINANCE role)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/admin/payments/pending` | Pending payments | ✅ |
| POST | `/admin/payment/{id}/approve` | Approve payment | ✅ |
| POST | `/admin/payment/{id}/reject` | Reject payment | ✅ |
| POST | `/admin/payment/{id}/flag` | Flag as fraud | ✅ |
| GET | `/admin/stats` | Dashboard statistics | ✅ |

### Service

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/service/use/{type}` | Use service credit | ✅ |

### Health Check

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Server status | ❌ |

**API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## 💰 Service Pricing

| Service | Price | Auto-Approve | Description |
|---------|-------|--------------|-------------|
| **Cek Dasar** | Rp 1.000 | ✅ Yes | Basic OJK/Kominfo check |
| **Cek Deep** | Rp 15.000 | ❌ Manual | AI chat analysis |
| **Cek Plus** | Rp 45.000 | ❌ Manual | Contract + legal letter |

---

## 🛡️ Security Features

- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Password Hashing** - bcrypt (12 rounds)
- ✅ **Role-Based Access** - USER, ADMIN, FINANCE
- ✅ **Fraud Detection** - Risk scoring system
- ✅ **Auto-Suspension** - For confirmed fraud
- ✅ **Audit Logging** - All admin actions tracked
- ✅ **Input Validation** - Pydantic schemas
- ✅ **CORS Protection** - Configurable origins

---

## 🧪 Testing

### Run in Mock Mode (No Setup Required)

```bash
# Backend will automatically use mock database
# if SUPABASE_URL and SUPABASE_KEY are not set

cd backend
uvicorn main:app --reload --port 8000
```

**Look for this message:**
```
🎯 MOCK MODE: Using in-memory database for testing
   Note: Data will reset when server restarts
   Demo accounts:
   - Admin: admin@amanga.id / admin123
   - Finance: finance@amanga.id / admin123
```

### Test Flow

1. **Open** http://localhost:3000
2. **Login** as admin (`admin@amanga.id` / `admin123`)
3. **Navigate** to dashboard
4. **Purchase** "Cek Dasar" (Rp 1.000)
5. **Upload** any image as payment proof
6. **See** auto-approval (instant for < Rp 1.000)
7. **Use** service credit from dashboard
8. **Check** admin panel for payment stats

---

## 📊 Database Schema

### Tables

```sql
users
├── id (UUID)
├── email (TEXT, unique)
├── password_hash (TEXT)
├── full_name (TEXT)
├── phone (TEXT)
├── role (USER | ADMIN | FINANCE)
├── status (ACTIVE | SUSPENDED | BANNED)
└── created_at, updated_at (TIMESTAMP)

payment_proofs
├── id (UUID)
├── user_id (FK → users)
├── service_type (CEK_DASAR | CEK_DEEP | CEK_PLUS)
├── amount (INTEGER)
├── payment_method (BANK_TRANSFER | GOPAY | OVO | DANA)
├── status (PENDING | APPROVED | REJECTED | AUTO_APPROVED | FLAGGED)
└── proof_image_url (TEXT)

service_credits
├── id (UUID)
├── user_id (FK → users)
├── service_type (CEK_DASAR | CEK_DEEP | CEK_PLUS)
├── quantity, used_quantity (INTEGER)
└── status (ACTIVE | USED | EXPIRED | REVOKED)

fraud_flags
├── id (UUID)
├── user_id (FK → users)
├── flag_type (FAKE_PROOF | DUPLICATE_PROOF | etc.)
├── severity (LOW | MEDIUM | HIGH | CRITICAL)
└── action_taken (WARNING | SUSPENSION | BAN | NO_ACTION)

admin_audit_log
├── id (UUID)
├── admin_id (FK → users)
├── action (TEXT)
├── target_type, target_id
└── details (JSONB)
```

---

## 🚀 Deployment

### Recommended Stack (Free Tier Friendly)

| Component | Service | Cost |
|-----------|---------|------|
| **Frontend** | Vercel | Free |
| **Backend** | Railway | $5/month |
| **Database** | Supabase | Free (500MB) |
| **Storage** | Supabase Storage | Free (1GB) |
| **WhatsApp** | Fonnte | ~$10/month |
| **Email** | SendGrid | Free (100/day) |

**Total:** ~$15/month for production setup

### Deploy Steps

1. **Frontend (Vercel):**
   ```bash
   # Push to GitHub
   # Import at vercel.com
   # Set NEXT_PUBLIC_API_URL
   ```

2. **Backend (Railway):**
   ```bash
   # Connect GitHub repo
   # Set environment variables
   # Deploy automatically
   ```

3. **Database (Supabase):**
   - Create production project
   - Run schema.sql
   - Enable Row Level Security

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guide.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - feel free to use for learning or commercial projects.

See [LICENSE](./LICENSE) for details.

---

## 📞 Support & Resources

### Documentation
- [Quick Start Guide](./QUICKSTART.md) - Setup in 5 minutes
- [API Key Setup](./API-KEY-SETUP.md) - Get WhatsApp/Email keys
- [Test Review](./TEST-REVIEW.md) - Complete code review
- [API Docs](http://localhost:8000/docs) - Swagger UI

### Demo
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Contact
- **GitHub:** https://github.com/Therealratoshen/aman-ga
- **Issues:** https://github.com/Therealratoshen/aman-ga/issues

---

## 🙏 Acknowledgments

Built with ❤️ for Indonesian market safety.

**Tech Stack:**
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Next.js](https://nextjs.org) - React framework
- [Supabase](https://supabase.com) - Open source Firebase alternative
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS

---

## 📈 Project Status

- ✅ **POC Complete** - All features implemented
- ✅ **Mock Mode** - Test without external services
- ✅ **Documentation** - Comprehensive guides
- ✅ **Production Ready** - 85% ready for deployment
- 🔄 **Next Steps** - Add payment gateway integration

**Last Updated:** March 15, 2026

---

<div align="center">

**Aman ga?** - Tanya dulu, transfer kemudian.

[Report Bug](https://github.com/Therealratoshen/aman-ga/issues) · [Request Feature](https://github.com/Therealratoshen/aman-ga/issues)

</div>
