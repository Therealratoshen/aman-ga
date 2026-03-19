# 📚 Complete Documentation Index - Aman ga? v2.1

## 🎯 Quick Navigation

| Document | Purpose | Location |
|----------|---------|----------|
| **[README.md](./README.md)** | Project overview & quick start | Root |
| **[SELF-LEARNING-OCR.md](./SELF-LEARNING-OCR.md)** | Self-learning OCR system | Root |
| **[SECURITY-IMPROVEMENTS.md](./SECURITY-IMPROVEMENTS.md)** | Security features | Root |
| **[IMPLEMENTATION-SUMMARY.md](./IMPLEMENTATION-SUMMARY.md)** | Implementation details | Root |
| **[QUICKSTART.md](./QUICKSTART.md)** | 5-minute setup guide | Root |
| **[API-KEY-SETUP.md](./API-KEY-SETUP.md)** | API key acquisition | Root |
| **[DEPLOYMENT-OPTIONS.md](./DEPLOYMENT-OPTIONS.md)** | Deployment comparison | Root |
| **[DEPLOY-VERCEL.md](./DEPLOY-VERCEL.md)** | Vercel deployment | Root |

---

## 📁 Project Structure

```
aman-ga/
├── 📂 backend/
│   ├── main.py                    # FastAPI application (v2.1.0)
│   ├── auth.py                    # JWT authentication
│   ├── database.py                # Database client (Supabase/Mock)
│   ├── mock_database.py           # In-memory mock database
│   ├── models.py                  # Pydantic schemas
│   ├── validators.py              # Input/file/OCR validation ⭐ NEW
│   ├── ocr_learning.py            # Self-learning OCR ⭐ NEW
│   ├── feedback_models.py         # Feedback models ⭐ NEW
│   ├── rate_limiter.py            # Rate limiting ⭐ NEW
│   ├── requirements.txt           # Python dependencies
│   ├── test_validation.py         # Test suite ⭐ NEW
│   │
│   ├── 📂 services/
│   │   ├── payment.py             # Payment processing (enhanced)
│   │   ├── fraud.py               # Fraud detection (enhanced)
│   │   └── notification.py        # WhatsApp/Email notifications
│   │
│   └── 📂 ocr_config/             # OCR configuration ⭐ NEW
│       ├── receipt_formats.json   # Known receipt formats
│       └── learning_metrics.json  # Learning progress
│
├── 📂 frontend/
│   ├── 📂 public/
│   │   ├── index.html             # Modern smooth UI ⭐ NEW
│   │   └── app.html               # Legacy UI (still works)
│   │
│   ├── 📂 pages/                  # Next.js pages (legacy)
│   ├── 📂 components/             # React components
│   └── 📂 styles/                 # Tailwind CSS
│
├── 📂 database/
│   ├── schema.sql                 # Database schema (enhanced)
│   └── seed.sql                   # Test data
│
├── 📂 docs/ (Documentation)
│   ├── README.md                  # Main documentation
│   ├── SELF-LEARNING-OCR.md       # OCR system ⭐ NEW
│   ├── SECURITY-IMPROVEMENTS.md   # Security features ⭐ NEW
│   ├── IMPLEMENTATION-SUMMARY.md  # Implementation ⭐ NEW
│   ├── QUICKSTART.md              # Quick start
│   ├── API-KEY-SETUP.md           # API keys
│   ├── DEPLOYMENT-OPTIONS.md      # Deployment
│   ├── DEPLOY-VERCEL.md           # Vercel guide
│   └── TEST-REVIEW.md             # Code review
│
├── LICENSE                        # MIT License
├── install.sh                     # Installation script ⭐ NEW
└── .gitignore
```

---

## 🚀 Quick Start (Updated)

### Option 1: Automated Installation

```bash
cd aman-ga
./install.sh
```

### Option 2: Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/Therealratoshen/aman-ga.git
cd aman-ga

# 2. Install system dependencies
# macOS
brew install tesseract libmagic

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-ind libmagic1

# 3. Install Python dependencies
cd backend
pip install -r requirements.txt

# 4. Start backend
uvicorn main:app --reload --port 8000

# 5. Open frontend
# http://localhost:8000/index.html
```

---

## 🔮 What's New in v2.1

### Self-Learning OCR System ⭐

- **Receipt Format Database**: Pre-configured for 8 Indonesian providers
- **Uncertainty Reporting**: Never 100% confident, always shows alternatives
- **User Feedback Loop**: Learn from every correction
- **Continuous Improvement**: Accuracy improves over time

### Enhanced Validation

- **File Validation**: Size, MIME type, dimensions, perceptual hash
- **OCR Verification**: Extract and compare with form data
- **Image Analysis**: ELA, metadata, noise patterns
- **Duplicate Detection**: Transaction ID, image hash, patterns

### Modern UI

- **Smooth Animations**: Fade, slide, scale effects
- **Confidence Visualization**: Color-coded meters
- **Interactive Feedback**: Easy correction interface
- **Responsive Design**: Works on all devices

### Rate Limiting

- **Login**: 5/minute, 20/hour
- **Upload**: 3/minute, 20/hour, 50/day
- **IP Blocking**: After 10 violations

---

## 📊 Receipt Format Support

### Pre-configured Providers

| Provider | Type | Status | Confidence |
|----------|------|--------|------------|
| BCA | Bank | ✅ Active | Learning |
| BRI | Bank | ✅ Active | Learning |
| BNI | Bank | ✅ Active | Learning |
| Mandiri | Bank | ✅ Active | Learning |
| Permata | Bank | ✅ Active | Learning |
| Danamon | Bank | ✅ Active | Learning |
| CIMB Niaga | Bank | ✅ Active | Learning |
| Maybank | Bank | ✅ Active | Learning |
| BTN | Bank | ✅ Active | Learning |
| GoPay | E-wallet | ✅ Active | Learning |
| OVO | E-wallet | ✅ Active | Learning |
| DANA | E-wallet | ✅ Active | Learning |
| LinkAja | E-wallet | ✅ Active | Learning |

### Adding New Formats

Users can suggest new receipt formats through the UI or API:

```bash
POST /receipt-formats/{provider}/improve
```

---

## 🧪 Testing

### Run Test Suite

```bash
cd backend
python test_validation.py
```

### Expected Output

```
============================================================
🔒 Aman ga? Security Validation Test Suite
============================================================

Testing Validators Module
✅ PaymentValidator initialized

📋 Test 1: Valid Payment Data
✅ Valid data accepted

📋 Test 2: Invalid Amount (Too Low)
✅ Correctly rejected

... (more tests)

============================================================
✅ All tests passed!
============================================================
```

---

## 📡 API Endpoints Summary

### Authentication
- `POST /register` - Register new user
- `POST /token` - Login (get JWT token)
- `GET /me` - Get current user

### Payment
- `POST /payment/upload` - Upload payment proof (enhanced with validation)
- `GET /payment/my` - Get payment history
- `GET /payment/credits` - Get service credits

### Feedback & Learning ⭐ NEW
- `POST /feedback/submit` - Submit feedback
- `GET /feedback/uncertainty-report/{payment_id}` - Get uncertainty report
- `GET /feedback/learning-metrics` - Get learning metrics (admin)
- `GET /receipt-formats` - Get known receipt formats
- `POST /receipt-formats/{provider}/improve` - Suggest format improvement

### Admin
- `GET /admin/payments/pending` - Get pending payments
- `POST /admin/payment/{id}/approve` - Approve payment
- `POST /admin/payment/{id}/reject` - Reject payment
- `POST /admin/payment/{id}/flag` - Flag as fraud
- `GET /admin/stats` - Dashboard statistics

### Health
- `GET /health` - Health check
- `GET /validation/test` - Test validation system

---

## 🔍 How to Use Self-Learning Features

### 1. Upload Payment Proof

Fill in all fields and upload receipt screenshot.

### 2. Review Results

System shows:
- Extracted data with confidence scores
- Uncertainty flags
- Alternative interpretations
- Validation results

### 3. Provide Feedback

Click "Bantu Kami Belajar!" (Help Us Learn):
- ✅ **Konfirmasi Benar** - If results are correct
- ✏️ **Ada yang Salah** - If corrections needed

### 4. Submit Corrections

If correcting:
- Enter correct values
- Add notes about what was wrong
- Rate receipt quality
- Mark as legitimate or not

### 5. System Learns

Your feedback:
- Adjusts extraction patterns
- Updates confidence scores
- Improves future accuracy

---

## 🎯 Confidence Scoring Explained

### How Confidence is Calculated

```
Base Confidence: 50% (neutral starting point)

Adjustments:
+ OCR quality match
+ Format pattern match
+ Color signature match
+ User confirmations

- OCR errors detected
- Format mismatch
- User corrections
- Low image quality
```

### Confidence Levels

| Level | Score | Meaning | Action |
|-------|-------|---------|--------|
| 🔴 LOW | < 50% | Very uncertain | Manual verification required |
| 🟡 MEDIUM | 50-70% | Somewhat uncertain | Suggest verification |
| 🟢 HIGH | 70-90% | Likely accurate | Probably correct |
| ✅ VERY HIGH | > 90% | Very reliable | Highly confident |

### Why Never 100%?

Receipts can be:
- **Fake but look real** - Well-designed forgeries
- **Real but look fake** - Damaged, poor quality photos

The system always maintains uncertainty to:
- Encourage user verification
- Allow for edge cases
- Prevent overconfidence errors

---

## 📈 Learning Progress Tracking

### Metrics Dashboard

Access via UI (Self-Learning tab) or API:

```json
{
  "total_samples": 1000,
  "total_feedback": 350,
  "correction_rate": 0.15,
  "overall_accuracy": 0.85,
  "amount_accuracy": 0.88,
  "transaction_id_accuracy": 0.82,
  "date_accuracy": 0.91,
  "provider_accuracy": {
    "BCA": 0.88,
    "BRI": 0.85,
    "GOPAY": 0.82
  },
  "accuracy_trend": [0.75, 0.78, 0.80, 0.82, 0.83, 0.85, 0.87]
}
```

### Accuracy Trends

The system tracks accuracy over time:
- Daily accuracy calculations
- Provider-specific metrics
- Field-level accuracy (amount, date, ID)

---

## 🔧 Configuration

### OCR Configuration Files

Location: `backend/ocr_config/`

#### receipt_formats.json

Known receipt format patterns:
- Amount extraction patterns
- Transaction ID patterns
- Date patterns
- Color signatures
- Layout characteristics

#### learning_metrics.json

Learning progress:
- Total samples processed
- Feedback statistics
- Accuracy metrics
- Provider-specific data

### Updating Configuration

1. **Automatic** (Recommended)
   - System learns from user feedback
   - Patterns adjust automatically

2. **Manual** (Advanced)
   - Edit JSON files directly
   - Restart backend to apply

3. **User Suggestions**
   - Submit via UI or API
   - Admin reviews and approves

---

## 🚨 Troubleshooting

### OCR Not Working

```bash
# Check Tesseract installation
tesseract --version

# Check language data
tesseract --list-langs

# Install Indonesian if missing
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-ind
```

### Low Confidence Scores

Possible causes:
- Poor image quality
- Unusual receipt format
- New provider not in database
- OCR errors

Solutions:
- Improve image quality
- Provide feedback to help learning
- Submit new format suggestion

### High Correction Rate

If many corrections needed:
- System is still learning
- Receipt format may be new
- Check image quality

Action:
- Continue providing feedback
- System will improve over time

---

## 📞 Support & Community

### Documentation
- Full documentation in `.md` files
- API docs: http://localhost:8000/docs

### GitHub
- **Issues**: Report bugs or request features
- **Discussions**: Ask questions, share ideas
- **Pull Requests**: Contribute improvements

### Contact
For questions or support, open an issue on GitHub.

---

## 🎉 Summary

Aman ga? v2.1 is a **self-learning payment verification system** that:

1. ✅ **Never overconfident** - Always shows uncertainty
2. ✅ **Learns from feedback** - Improves with each correction
3. ✅ **Handles diversity** - Supports many receipt formats
4. ✅ **Transparent** - Shows alternatives and confidence
5. ✅ **User-friendly** - Modern smooth UI
6. ✅ **Secure** - Multi-layer validation
7. ✅ **Extensible** - Easy to add new formats

**Built for Indonesia, learning from everyone.**

---

**Version**: 2.1.0  
**Last Updated**: March 19, 2026  
**Status**: ✅ Production Ready

---

<div align="center">

### 🔮 Aman ga? — Tanya dulu, transfer kemudian.

**Never 100% confident, always learning.**

[⭐ Star](https://github.com/Therealratoshen/aman-ga) • [🍴 Fork](https://github.com/Therealratoshen/aman-ga/fork) • [📋 Issues](https://github.com/Therealratoshen/aman-ga/issues)

**Made with ❤️ in Indonesia**

</div>
