# 🔑 API Key Setup Guide - Aman ga?

This guide shows you how to get all required API keys for the Aman ga? POC.

---

## 📋 Required vs Optional Services

| Service | Status | Purpose | Cost |
|---------|--------|---------|------|
| **Supabase** | ✅ REQUIRED | Database & Auth | Free tier available |
| **WhatsApp API** | ⚠️ OPTIONAL | User notifications | Free tier available |
| **SendGrid** | ⚠️ OPTIONAL | Email notifications | Free tier (100/day) |

---

## 1️⃣ SUPABASE (REQUIRED)

### What it's used for:
- User database
- Payment records
- Service credits
- Fraud flags
- Admin audit logs

### How to get credentials:

#### Step 1: Create Account
1. Go to https://supabase.com
2. Click "Start your project" or "Sign Up"
3. Sign up with GitHub or email

#### Step 2: Create Project
1. Click "New Project"
2. Fill in:
   - **Name**: `aman-ga` (or any name)
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to you
3. Click "Create new project"
4. Wait 2-3 minutes for setup

#### Step 3: Get API Credentials
1. Click **Settings** (gear icon) in left sidebar
2. Click **API**
3. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

#### Step 4: Run Database Schema
1. Click **SQL Editor** in left sidebar
2. Click **New Query**
3. Copy entire contents of `database/schema.sql`
4. Paste into SQL Editor
5. Click **Run** (or press Cmd/Ctrl + Enter)
6. You should see "Success. No rows returned"

#### Step 5: Verify Setup
1. Click **Table Editor** in left sidebar
2. You should see these tables:
   - `users`
   - `payment_proofs`
   - `service_credits`
   - `fraud_flags`
   - `admin_audit_log`

### Add to .env:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-anon-key
```

---

## 2️⃣ WHATSAPP API (OPTIONAL)

### What it's used for:
- Payment confirmation notifications
- Account status alerts
- Admin notifications

### Option A: Fonnte (Indonesia - Recommended)

#### Step 1: Create Account
1. Go to https://fonnte.com
2. Click "Daftar" (Register)
3. Fill in your details

#### Step 2: Get API Token
1. Login to https://fonnte.com/dashboard
2. Click menu **API** → **API Key**
3. Copy your API token

#### Step 3: Activate Device
1. Click **Add Device**
2. Scan QR code with your WhatsApp
3. Wait for connection

#### Step 4: Get API URL
- Base URL: `https://api.fonnte.com/send`

### Add to .env:
```env
WHATSAPP_API_KEY=your-fonnte-token
WHATSAPP_API_URL=https://api.fonnte.com/send
```

### Option B: Twilio (International)

#### Step 1: Create Account
1. Go to https://www.twilio.com
2. Click "Sign Up"
3. Verify email and phone

#### Step 2: Get Credentials
1. Go to Console Dashboard
2. Copy **Account SID** and **Auth Token**

#### Step 3: Setup WhatsApp Sandbox
1. Go to Messaging → Try it out → Send a WhatsApp message
2. Follow instructions to connect your WhatsApp
3. Copy the sandbox number

### Add to .env (Twilio):
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## 3️⃣ SENDGRID (OPTIONAL)

### What it's used for:
- Payment confirmation emails
- Password reset emails
- Admin notifications

#### Step 1: Create Account
1. Go to https://sendgrid.com
2. Click "Sign Up Free"
3. Complete registration

#### Step 2: Verify Email
1. Check your email
2. Click verification link
3. Complete account setup

#### Step 3: Create API Key
1. Go to **Settings** → **API Keys**
2. Click **Create API Key**
3. Name: `Aman ga?`
4. Permissions: **Full Access** (or Restricted Access → Mail Send)
5. Click **Create & View**
6. **Copy the API key immediately** (won't show again!)

#### Step 4: Verify Sender
1. Go to **Settings** → **Sender Authentication**
2. Click **Verify a Single Sender**
3. Fill in:
   - From Email: `noreply@amanga.id` (or your email)
   - From Name: `Aman ga?`
   - Reply-To: your email
4. Click verification link sent to your email

### Add to .env:
```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxx.your-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@amanga.id
SENDGRID_FROM_NAME=Aman ga?
```

---

## 📝 Complete .env File

Copy this to `backend/.env`:

```env
# ============ SUPABASE (REQUIRED) ============
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-key

# ============ JWT Security ============
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============ WHATSAPP (OPTIONAL - Leave empty for mock mode) ============
WHATSAPP_API_KEY=
WHATSAPP_API_URL=

# ============ EMAIL (OPTIONAL - Leave empty for mock mode) ============
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@amanga.id
SENDGRID_FROM_NAME=Aman ga?
```

---

## 🧪 Testing Without API Keys

The POC works **without** WhatsApp and SendGrid!

- If `WHATSAPP_API_KEY` is empty → Logs to console instead of sending
- If `SENDGRID_API_KEY` is empty → Logs to console instead of sending

This is perfect for development and testing.

---

## ✅ Verification Checklist

### Supabase
- [ ] Created Supabase account
- [ ] Created project
- [ ] Copied URL and anon key
- [ ] Ran schema.sql in SQL Editor
- [ ] Verified tables exist in Table Editor

### WhatsApp (Optional)
- [ ] Created Fonnte/Twilio account
- [ ] Got API token
- [ ] Connected WhatsApp device
- [ ] Test message sent successfully

### SendGrid (Optional)
- [ ] Created SendGrid account
- [ ] Verified email
- [ ] Created API key
- [ ] Verified sender email
- [ ] Test email sent successfully

---

## 🚀 Quick Test

After setting up Supabase:

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see all API endpoints!

---

## 📞 Support

If you get stuck:
1. Check Supabase logs: https://app.supabase.com/project/_/logs
2. Check backend console for error messages
3. Verify your API keys are correct (no extra spaces)
