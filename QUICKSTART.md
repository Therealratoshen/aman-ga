# 🚀 Aman ga? - Quick Start Guide

## Prerequisites
- Python 3.10+ (tested on 3.14)
- Node.js 18+ 
- Supabase account (free tier works)

## 1. Setup Supabase (5 minutes)

1. Go to [supabase.com](https://supabase.com) and create a free project
2. Once project is ready, go to **Settings** → **API**
3. Copy these two values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (e.g., `eyJhbG...`)

4. Go to **SQL Editor** and run the contents of `database/schema.sql`
5. (Optional) Run `database/seed.sql` for test data

## 2. Setup Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
nano .env  # or use your preferred editor
```

### Edit `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SECRET_KEY=your-secret-key-for-jwt-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Run Backend:
```bash
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: **http://localhost:8000**

API Docs: **http://localhost:8000/docs**

## 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local (optional)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

Frontend will run on: **http://localhost:3000**

## 4. Test the Application

### Demo Credentials:
- **Admin**: `admin@amanga.id` / `admin123`
- **Finance**: `finance@amanga.id` / `admin123`
- **User**: Register a new account

### Test Flow:
1. Open http://localhost:3000
2. Login as admin or register new user
3. **As User**:
   - Purchase "Cek Dasar" (Rp 1.000 - auto-approved)
   - Upload payment proof (screenshot any image)
   - See service credit activated instantly
   - Use the service from dashboard
4. **As Admin**:
   - View pending payments
   - Approve/Reject payments
   - Flag fraud (auto-suspends user)

## 5. API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /token` - Login
- `GET /me` - Get current user

### Payment
- `POST /payment/upload` - Upload payment proof
- `GET /payment/my` - Payment history
- `GET /payment/credits` - Service credits

### Admin (requires role)
- `GET /admin/payments/pending` - Pending payments
- `POST /admin/payment/{id}/approve` - Approve payment
- `POST /admin/payment/{id}/reject` - Reject payment
- `POST /admin/payment/{id}/flag` - Flag as fraud

### Health Check
- `GET /health` - Server status

## Troubleshooting

### Backend won't start:
```bash
# Check if Supabase credentials are correct
# Check if schema.sql was run in Supabase SQL Editor
# Check port 8000 is not in use
lsof -i :8000
```

### Frontend won't start:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Can't login:
- Make sure you ran `database/schema.sql` in Supabase
- Default admin password: `admin123`
- Check backend logs for errors

## Project Structure

```
aman-ga-poc/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── auth.py          # JWT authentication
│   ├── database.py      # Supabase client
│   ├── models.py        # Pydantic schemas
│   └── services/        # Business logic
│       ├── payment.py   # Payment processing
│       ├── fraud.py     # Fraud detection
│       └── notification.py
├── frontend/            # Next.js frontend
│   ├── pages/          # React pages
│   │   ├── index.js    # Login/Register
│   │   ├── dashboard.js
│   │   ├── admin.js
│   │   └── payment.js
│   └── components/     # Reusable components
└── database/           # SQL schemas
    ├── schema.sql
    └── seed.sql
```

## Next Steps

1. **Add real payment gateway** (Midtrans, Xendit)
2. **Add Supabase Storage** for image uploads
3. **Add WhatsApp API** for notifications
4. **Deploy to production** (Vercel + Railway/Render)

## Support

For issues or questions, create an issue on GitHub.
