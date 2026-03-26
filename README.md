# 🛡️ Aman ga? - Payment Verification POC

> **Tanya dulu, transfer kemudian.**
> *Ask first, transfer later.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/Therealratoshen/aman-ga/releases)
[![Self-Learning](https://img.shields.io/badge/self--learning-OCR-orange.svg)](./SELF-LEARNING-OCR.md)

[![Status](https://img.shields.io/badge/status-production--ready-success)](https://github.com/Therealratoshen/aman-ga)
[![Last Commit](https://img.shields.io/github/last-commit/Therealratoshen/aman-ga)](https://github.com/Therealratoshen/aman-ga/commits/main)
[![Live Demo](https://img.shields.io/badge/live_demo-available-brightgreen.svg)](http://147.139.202.129/)

### 🔗 Quick Links

| 📄 **Documentation** | 🎨 **Live Demo** | 💻 **Source Code** |
|---------------------|------------------|-------------------|
| [GitHub Pages](https://therealratoshen.github.io/aman-ga/) | [🔗 147.139.202.129](http://147.139.202.129/) | [GitHub Repo](https://github.com/Therealratoshen/aman-ga) |

> **⚠️ IMPORTANT:** This is a **Proof of Concept (POC) / Demo system**. No real payments are processed. All transactions are simulated for testing and learning purposes.

> **✨ NEW in v2.1:** Self-learning OCR system, modern smooth UI, uncertainty reporting, and automated deployment scripts!

---

## 📖 Table of Contents

- [What is Aman ga?](#-what-is-aman-ga)
- [✨ Features](#-features)
- [🆕 What's New in v2.1](#-whats-new-in-v21)
- [🎯 Quick Start](#-quick-start)
- [📋 Demo Credentials](#-demo-credentials)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [🔌 API Endpoints](#-api-endpoints)
- [💰 Service Pricing](#-service-pricing)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🛡️ Security](#️-security)
- [🧠 Self-Learning OCR](#-self-learning-ocr)
- [📊 Database Schema](#-database-schema)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📞 Support](#-support)

---

## 🎯 What is Aman ga?

**Aman ga?** is a **Receipt Validation & Deepfake Detection System** designed for the Indonesian market to help users verify if payment receipts are authentic before trusting transactions.

> **⚠️ DISCLAIMER:** This is a **demo/educational project**. The system demonstrates OCR, image validation, deepfake detection, and authenticity assessment concepts.

### The Problem We Solve

In Indonesia, online fraud is rampant with fake receipts and deepfakes. People need a way to:
- ✅ Verify if payment receipts are authentic
- ✅ Detect deepfakes and manipulated images
- ✅ Get AI-powered authenticity assessments
- ✅ Validate receipt details against extracted data

### How It Works

```mermaid
graph LR
    A[User Uploads Receipt] --> B{Validation}
    B --> C[File Validation]
    B --> D[OCR Extraction]
    B --> E[Image Analysis]
    B --> F[Deepfake Detection]
    C --> G[Authenticity Scoring]
    D --> G
    E --> G
    F --> G
    G --> H{Authenticity Level}
    H -->|HIGH| I[Trust Receipt]
    H -->|MEDIUM| J[Manual Review]
    H -->|LOW| K[Flag as Suspicious]
```

1. **User registers** (demo account)
2. **Uploads receipt/image** (screenshot or photo)
3. **System validates**:
   - File validation (size, MIME, dimensions)
   - OCR extraction with confidence scoring
   - Image manipulation detection
   - Deepfake detection analysis
   - Authenticity assessment
4. **Authenticity scoring** determines trust level
5. **Results**: Trust, Review, or Flag as suspicious

### 🌐 Live Demo

**Try it now:** [http://147.139.202.129/](http://147.139.202.129/)

**Demo Credentials:**
- **Admin**: `admin@amanga.id` / `admin123`
- **Finance**: `finance@amanga.id` / `admin123`
- **User**: Register a new account (demo)

**What You Can Do:**
- ✅ Upload receipts for validation
- ✅ See OCR extraction in action
- ✅ View deepfake detection results
- ✅ Get authenticity assessments
- ✅ Test admin validation dashboard
- ✅ Provide feedback to improve OCR
- ✅ Explore all features

---

## ✨ Features

### 🔐 Authentication & Authorization
- ✅ JWT-based authentication
- ✅ Role-based access control (USER, ADMIN, FINANCE)
- ✅ Secure password hashing (bcrypt)
- ✅ Token expiration & refresh

### 📸 Receipt Validation & Deepfake Detection
- ✅ **OCR extraction** with confidence scoring
- ✅ **Deepfake detection** with multiple indicators
- ✅ **Receipt format validation** (headers, items, totals, footers)
- ✅ **Business information extraction** (names, addresses, tax IDs)
- ✅ **Logical consistency validation** (amounts, taxes, calculations)
- ✅ **Image manipulation analysis** (ELA, metadata, noise)
- ✅ **Authenticity assessment** with scoring
- ✅ **Real-time validation** results

### 🛡️ Advanced Security
- ✅ Multi-layer validation (file, OCR, receipt structure, deepfake)
- ✅ Duplicate detection with perceptual hashing
- ✅ Rate limiting with IP blocking
- ✅ Comprehensive audit logging
- ✅ Security headers implementation

### 🧠 Self-Learning OCR ⭐ NEW v2.1
- ✅ Receipt format database (13 Indonesian providers)
- ✅ Uncertainty reporting with alternatives
- ✅ User feedback loop for continuous learning
- ✅ Confidence scoring (never 100%)
- ✅ OCR pattern refinement from corrections

### 🎨 Modern UI ⭐ NEW v2.1
- ✅ Smooth animations and transitions
- ✅ Real-time validation feedback
- ✅ Confidence visualization
- ✅ Interactive feedback interface
- ✅ Responsive design (mobile-friendly)

### 👮 Admin Dashboard
- ✅ Receipt validation statistics
- ✅ Authenticity assessment tracking
- ✅ Deepfake detection monitoring
- ✅ Real-time validation metrics
- ✅ Complete audit log

### 📱 User Interface
- ✅ Responsive design (mobile-first)
- ✅ Beautiful gradient UI (Tailwind CSS)
- ✅ Real-time validation results
- ✅ Receipt validation workflow
- ✅ Deepfake detection reports

### 🔔 Notifications (Optional)
- ✅ WhatsApp integration (Fonnte)
- ✅ Email integration (SendGrid)
- ✅ Mock mode for development

---

## 🆕 What's New in v2.1

### 🧠 Self-Learning OCR System

The system now learns from every user interaction:

- **Receipt Format Database**: Pre-configured for 13 Indonesian providers (BCA, BRI, Mandiri, GoPay, OVO, DANA, etc.)
- **Uncertainty Reporting**: Never 100% confident - always shows alternative interpretations
- **User Feedback Loop**: Every correction improves the system
- **Confidence Scoring**: Field-level confidence with visual indicators
- **Continuous Learning**: Accuracy improves over time

### 🎨 Modern Smooth UI

Beautiful new interface with:

- Smooth animations (fade, slide, scale)
- Real-time validation feedback
- Confidence visualization meters
- Interactive feedback interface
- Responsive design (works on all devices)

### 🛡️ Enhanced Security

- Multi-layer validation (file, OCR, image, fraud)
- Rate limiting with IP blocking
- Perceptual hashing for duplicate detection
- Image manipulation detection (ELA, metadata, noise)
- Comprehensive audit logging

### 🚀 Easy Deployment

- Automated deployment script (`deploy.sh`)
- Systemd service configuration
- Nginx reverse proxy setup
- One-command deployment to any VPS

### 📚 Complete Documentation

7 new comprehensive guides:
- `SELF-LEARNING-OCR.md` - OCR system details
- `SECURITY-IMPROVEMENTS.md` - Security features
- `DEPLOYMENT-SERVER.md` - Server deployment guide
- `QUICK-REFERENCE.md` - Common commands
- `DOCUMENTATION-INDEX.md` - Navigation index
- `FINAL-CHECKLIST.md` - Production checklist
- `IMPLEMENTATION-SUMMARY.md` - Implementation details

---

## 🎯 Quick Start

### Option 1: Mock Mode (Recommended for Testing) ⭐

**No external services needed!** Test everything locally in 5 minutes.

```bash
# 1. Clone repository
git clone https://github.com/Therealratoshen/aman-ga.git
cd aman-ga

# 2. Start Backend (Terminal 1)
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Look for this message:
# 🎯 MOCK MODE: Using in-memory database for testing
#    Demo accounts:
#    - Admin: admin@amanga.id / admin123
#    - Finance: finance@amanga.id / admin123

# 3. Start Frontend (Terminal 2)
cd frontend
npm install
npm run dev

# 4. Open browser
# http://localhost:3000
```

**✅ Ready to test!** Login with demo credentials below.

---

### Option 2: Production Mode (With Supabase)

For persistent data and production deployment:

```bash
# 1. Create free Supabase project
# Go to: https://supabase.com
# Create project → Copy URL and anon key

# 2. Run database schema
# SQL Editor → New Query → Paste database/schema.sql → Run

# 3. Configure backend
cd backend
cp .env.example .env
nano .env  # Edit with your Supabase credentials

# 4. Restart backend
uvicorn main:app --reload --port 8000
```

See [QUICKSTART.md](./QUICKSTART.md) for detailed setup guide.

---

## 📋 Demo Credentials

> **⚠️ IMPORTANT:** This is a **demo system**. No real payments are processed. All data is simulated for testing purposes.

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| **👑 Admin** | admin@amanga.id | admin123 | Full access, fraud flagging |
| **💰 Finance** | finance@amanga.id | admin123 | Approve/reject payments (simulated) |
| **👤 User** | Register new | Your choice | Test features (no real money) |

**Try these steps:**
1. Login as **Admin** → Explore admin dashboard
2. Register **new user** → Upload fake payment proof (test only)
3. Logout → Login as **Finance** → Approve payment (simulated)
4. Check user dashboard → See activated credit (demo)

**🌐 Live Demo:** [http://147.139.202.129/](http://147.139.202.129/)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Desktop   │  │   Mobile    │  │   Tablet    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Next.js 14 Frontend (React)               │    │
│  │           • Tailwind CSS                           │    │
│  │           • Axios HTTP Client                      │    │
│  │           • JWT Authentication                     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ REST API
┌─────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            FastAPI Backend (Python)                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │   Auth   │ │ Payment  │ │  Fraud   │            │    │
│  │  │ Service  │ │ Service  │ │ Service  │            │    │
│  │  └──────────┘ └──────────┘ └──────────┘            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ SQL
┌─────────────────────────────────────────────────────────────┐
│                        DATA LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Supabase   │  │    Mock     │  │   Storage   │         │
│  │  PostgreSQL │  │   Database  │  │  (Images)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
aman-ga/
├── 📂 backend/                    # FastAPI Backend
│   ├── main.py                   # 📄 API endpoints (414 lines)
│   ├── auth.py                   # 🔐 JWT authentication
│   ├── database.py               # 💾 Database client (Supabase/Mock)
│   ├── mock_database.py          # 🎭 In-memory mock database ⭐ NEW
│   ├── models.py                 # 📋 Pydantic schemas
│   ├── requirements.txt          # 📦 Python dependencies
│   ├── .env.example              # ⚙️ Environment template
│   └── 📂 services/
│       ├── payment.py            # 💳 Payment processing
│       ├── fraud.py              # 🛡️ Fraud detection
│       └── notification.py       # 🔔 WhatsApp/Email
│
├── 📂 frontend/                   # Next.js Frontend
│   ├── 📂 pages/
│   │   ├── index.js              # 🏠 Login/Register
│   │   ├── dashboard.js          # 📊 User dashboard
│   │   ├── admin.js              # 👮 Admin panel
│   │   └── payment.js            # 💳 Payment history
│   ├── 📂 components/
│   │   ├── PaymentUpload.js      # 📸 Upload modal
│   │   ├── ServiceCard.js        # 💎 Service pricing
│   │   └── AdminDashboard.js     # 📈 Admin view
│   ├── 📂 styles/
│   │   └── globals.css           # 🎨 Tailwind CSS
│   ├── package.json              # 📦 NPM dependencies
│   └── next.config.js            # ⚙️ Next.js config
│
├── 📂 database/
│   ├── schema.sql                # 🗄️ Database schema
│   └── seed.sql                  # 🌱 Test data
│
└── 📂 docs/
    ├── README.md                 # 📖 This file
    ├── QUICKSTART.md             # 🚀 Setup guide (5 min)
    ├── API-KEY-SETUP.md          # 🔑 API key acquisition
    ├── TEST-REVIEW.md            # ✅ Code review report
    └── DEPLOYMENT-OPTIONS.md     # ☁️ Deployment comparison
```

---

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/register` | Register new user | ❌ |
| `POST` | `/token` | Login (get JWT token) | ❌ |
| `GET` | `/me` | Get current user | ✅ |

**Example: Login**
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@amanga.id&password=admin123"
```

### Receipt Validation

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/receipt/validate` | Validate receipt for authenticity and deepfake detection | ✅ |
| `GET` | `/payment/credits` | Get service credits (simplified for mock mode) | ✅ |

**Example: Validate Receipt**
```bash
curl -X POST "http://localhost:8000/receipt/validate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "bank_name=BCA" \
  -F "transaction_id=TRX123" \
  -F "transaction_date=2024-01-01T10:00:00" \
  -F "amount=100000" \
  -F "proof_image=@receipt.png"
```

### Admin (Requires ADMIN or FINANCE role)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/admin/stats` | Dashboard statistics | ✅ |

**Example: Get Stats**
```bash
curl -X GET "http://localhost:8000/admin/stats" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Feedback & Learning

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/feedback/submit` | Submit OCR feedback for learning | ✅ |
| `GET` | `/feedback/uncertainty-report/{payment_id}` | Get uncertainty report | ✅ |

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Server status | ❌ |

**📖 Full API Documentation:** http://localhost:8000/docs (Swagger UI)

---

## 💰 Service Pricing

The system now focuses primarily on receipt validation and deepfake detection. Service credits are simplified when no database is present.

| Service | Price | Auto-Approve | Processing Time | Description |
|---------|-------|--------------|-----------------|-------------|
| **🔍 Receipt Validation** | Free (mock mode) | ✅ Yes | Instant | OCR validation & deepfake detection |
| **🎭 Deepfake Detection** | Free (mock mode) | ✅ Yes | Instant | Advanced image analysis |
| **✅ Authenticity Check** | Free (mock mode) | ✅ Yes | Instant | Receipt authenticity assessment |

### Validation Process

Receipt validation includes:
- ✅ OCR extraction with confidence scoring
- ✅ Image manipulation detection
- ✅ Deepfake analysis
- ✅ Authenticity assessment
- ✅ User feedback integration

---

## 🧪 Testing

### Test Flow (Mock Mode)

```bash
# 1. Start backend (Terminal 1)
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# 2. Start frontend (Terminal 2)
cd frontend
npm run dev

# 3. Open http://localhost:3000
```

### Test Scenarios

#### Scenario 1: User Registration & Receipt Validation
1. Register new account
2. Login with new credentials
3. Navigate to Receipt Validation page
4. Upload receipt image with transaction details
5. See OCR extraction results ✅
6. View deepfake detection analysis
7. Check authenticity assessment

#### Scenario 2: Admin Dashboard
1. Login as admin (`admin@amanga.id` / `admin123`)
2. Navigate to Admin Panel
3. View validation statistics
4. Monitor authenticity assessments
5. Review suspicious receipts

#### Scenario 3: Deepfake Detection
1. Upload a manipulated receipt image
2. Observe deepfake detection indicators
3. Check authenticity scoring
4. Verify system flags suspicious receipts

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

---

## 🚀 Deployment

### ⚡ Quick Deploy (Recommended)

Deploy to any VPS (Alibaba Cloud, DigitalOcean, etc.) in one command:

```bash
# SSH to your server
ssh root@YOUR_SERVER_IP

# Clone and deploy
git clone https://github.com/Therealratoshen/aman-ga.git
cd aman-ga
sudo ./deploy.sh
```

**That's it!** The script will:
- ✅ Install all dependencies (Python, Tesseract OCR, Nginx)
- ✅ Setup Python virtual environment
- ✅ Configure Nginx as reverse proxy
- ✅ Setup systemd service for auto-start
- ✅ Configure firewall
- ✅ Start everything automatically

### 📚 Deployment Options

| Method | Best For | Setup Time | Cost |
|--------|----------|------------|------|
| **Simple Application Server** | Production | 5 min | $5-10/month |
| **Docker** | Development | 10 min | Free |
| **Vercel + Railway** | Testing | 15 min | Free |

### 📖 Deployment Guides

- **[DEPLOYMENT-SERVER.md](./DEPLOYMENT-SERVER.md)** - Complete server deployment guide
- **[QUICK-REFERENCE.md](./QUICK-REFERENCE.md)** - Common commands & troubleshooting
- **[DEPLOYMENT-OPTIONS.md](./DEPLOYMENT-OPTIONS.md)** - Cloud provider comparison
- **[QUICKSTART.md](./QUICKSTART.md)** - Basic setup (5 min)
- **[API-KEY-SETUP.md](./API-KEY-SETUP.md)** - WhatsApp/Email setup

### 🔧 Server Requirements

```
- OS: Ubuntu 20.04+ / CentOS 7+
- RAM: 2GB minimum (4GB recommended)
- Storage: 10GB free space
- Python: 3.10+
```

### 🌐 After Deployment

Access your application:
- **Frontend**: `http://YOUR_SERVER_IP/`
- **API Docs**: `http://YOUR_SERVER_IP/docs`
- **Health Check**: `http://YOUR_SERVER_IP/health`

**Production Setup:**
1. Edit `.env` with Supabase credentials
2. Set `MOCK_MODE=False`
3. Install SSL certificate: `sudo certbot --nginx`
4. Change default passwords

---

## 🛡️ Security

### Authentication
- ✅ JWT tokens with 30-minute expiration
- ✅ Password hashing with bcrypt (12 rounds)
- ✅ Role-based access control (RBAC)
- ✅ Protected routes with middleware
- ✅ Rate limiting (login, upload, API)
- ✅ IP blocking after violations
- ✅ **ENFORCED SECRET_KEY requirement** for production

### Data Protection
- ✅ SQL injection prevention (Supabase client)
- ✅ Input validation (Pydantic + custom validators)
- ✅ CORS configuration (hardened)
- ✅ XSS protection headers
- ✅ Security headers (HSTS, CSP, etc.)
- ✅ File validation (MIME, size, dimensions)

### Receipt Validation Security
- ✅ **Deepfake detection** with multiple indicators
- ✅ Image manipulation detection (ELA, metadata, noise)
- ✅ OCR verification with form matching
- ✅ Authenticity assessment with scoring
- ✅ Perceptual hashing for duplicate detection

### Production Ready
- ✅ HTTPS/SSL (Certbot)
- ✅ Rate limiting enabled
- ✅ CSRF protection headers
- ✅ Comprehensive logging
- ✅ Automated backups support

---

## 📊 Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ PAYMENT_PROOFS : creates
    USERS ||--o{ SERVICE_CREDITS : owns
    USERS ||--o{ FRAUD_FLAGS : flagged_in
    USERS ||--o{ ADMIN_AUDIT_LOG : actions
    
    PAYMENT_PROOFS ||--o| SERVICE_CREDITS : generates
    PAYMENT_PROOFS ||--o{ FRAUD_FLAGS : associated_with
    
    USERS {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        string phone
        string role "USER|ADMIN|FINANCE"
        string status "ACTIVE|SUSPENDED|BANNED"
        timestamp created_at
        timestamp updated_at
    }
    
    PAYMENT_PROOFS {
        uuid id PK
        uuid user_id FK
        string service_type
        integer amount
        string payment_method
        string status
        text proof_image_url
        timestamp created_at
    }
    
    SERVICE_CREDITS {
        uuid id PK
        uuid user_id FK
        string service_type
        integer quantity
        integer used_quantity
        string status
        timestamp expires_at
    }
    
    FRAUD_FLAGS {
        uuid id PK
        uuid user_id FK
        uuid payment_proof_id FK
        string flag_type
        string severity
        string status
        string action_taken
        timestamp reviewed_at
    }
    
    ADMIN_AUDIT_LOG {
        uuid id PK
        uuid admin_id FK
        string action
        string target_type
        uuid target_id
        jsonb details
        timestamp created_at
    }
```

### Tables Overview

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | User accounts | email, role, status |
| `payment_proofs` | Payment records | amount, status, proof_image_url |
| `service_credits` | Service usage tracking | quantity, used_quantity, expires_at |
| `fraud_flags` | Fraud detection | flag_type, severity, action_taken |
| `admin_audit_log` | Admin action tracking | action, target_type, details |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Development Setup

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run dev
```

### Code Style

- **Python:** PEP 8, type hints where possible
- **JavaScript:** ESLint (Next.js recommended)
- **Commits:** Conventional Commits format

---

## 📄 License

MIT License - feel free to use for learning or commercial projects.

See [LICENSE](./LICENSE) for details.

---

## 📞 Support

### Documentation
- [📖 Quick Start](./QUICKSTART.md) - Setup in 5 minutes
- [🔑 API Keys](./API-KEY-SETUP.md) - Get WhatsApp/Email keys
- [🧪 Test Review](./TEST-REVIEW.md) - Complete code review
- [☁️ Deployment](./DEPLOYMENT-OPTIONS.md) - Cloud provider comparison
- [📡 API Docs](http://localhost:8000/docs) - Swagger UI (when running)

### Links
- **GitHub:** https://github.com/Therealratoshen/aman-ga
- **Issues:** https://github.com/Therealratoshen/aman-ga/issues
- **Discussions:** https://github.com/Therealratoshen/aman-ga/discussions

### Contact
For questions or support, please open an issue on GitHub.

---

## 🙏 Acknowledgments

Built with ❤️ for Indonesian market safety.

### Tech Stack
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Next.js](https://nextjs.org) - React framework
- [Supabase](https://supabase.com) - Open source Firebase alternative
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS
- [Python](https://python.org) - Programming language
- [React](https://react.dev) - UI library

### Inspiration
This project was built to help Indonesians verify online transactions and avoid fraud.

---

## 📈 Project Status

| Milestone | Status | Date |
|-----------|--------|------|
| Receipt Validation Focus | ✅ Complete | Mar 2026 |
| Deepfake Detection | ✅ Complete | Mar 2026 |
| Receipt Format Validation | ✅ Complete | Mar 2026 |
| Business Info Extraction | ✅ Complete | Mar 2026 |
| Logical Consistency Checks | ✅ Complete | Mar 2026 |
| Security Hardening | ✅ Complete | Mar 2026 |
| Mock Mode | ✅ Complete | Mar 2026 |
| Documentation | ✅ Complete | Mar 2026 |
| Frontend UI | ✅ Complete | Mar 2026 |
| Backend API | ✅ Complete | Mar 2026 |
| Production Deployment | 🔄 Ready | - |

**Last Updated:** March 21, 2026

---

<div align="center">

### 🛡️ Aman ga? - Tanya dulu, transfer kemudian.

[⭐ Star this repo](https://github.com/Therealratoshen/aman-ga/stargazers) • [🍴 Fork it](https://github.com/Therealratoshen/aman-ga/fork) • [📋 Issues](https://github.com/Therealratoshen/aman-ga/issues)

**Made with ❤️ in Indonesia**

</div>
