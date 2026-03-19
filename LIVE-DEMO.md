# 🌐 Live Demo Information

## 🎯 Live Demo Available

**URL:** [http://147.139.202.129/](http://147.139.202.129/)

**Status:** ✅ **Running** (Alibaba Cloud Simple Application Server)

---

## ⚠️ IMPORTANT DISCLAIMER

### This is a Proof of Concept (POC) / Demo System

**NO REAL PAYMENTS ARE PROCESSED** in this system. This is an **educational/demo project** that demonstrates:

1. ✅ OCR technology for receipt scanning
2. ✅ Image validation techniques
3. ✅ Fraud detection concepts
4. ✅ Self-learning systems
5. ✅ Modern web application architecture

### What You CAN Do

- ✅ Upload **fake/simulated** payment proofs for testing
- ✅ Test OCR extraction on real receipt screenshots
- ✅ Explore the admin approval workflow
- ✅ Provide feedback to improve OCR accuracy
- ✅ Learn about image validation techniques
- ✅ Test the self-learning feedback system

### What You CANNOT Do

- ❌ Process real payments
- ❌ Transfer actual money
- ❌ Connect to real bank accounts
- ❌ Use for actual fraud detection in production
- ❌ Store sensitive financial data

---

## 🔑 Demo Credentials

### Admin Account
- **Email:** `admin@amanga.id`
- **Password:** `admin123`
- **Access:** Full admin dashboard, fraud flagging, manual review

### Finance Account
- **Email:** `finance@amanga.id`
- **Password:** `admin123`
- **Access:** Approve/reject payments (simulated)

### User Account
- **Register:** Create a new account with any email
- **Password:** Your choice
- **Access:** Upload payment proofs, view credits (all simulated)

---

## 🧪 Testing Scenarios

### Scenario 1: Test OCR Accuracy
1. Register a new user account
2. Take a screenshot of a real bank transfer receipt
3. Upload it in the "Upload Pembayaran" section
4. Fill in the form with the same details
5. See how well OCR extracts the data
6. Provide feedback if OCR made mistakes

### Scenario 2: Test Fraud Detection
1. Login as admin (`admin@amanga.id` / `admin123`)
2. Upload a payment proof with suspicious details
3. See the fraud risk scoring in action
4. Try uploading the same image twice (duplicate detection)
5. Try uploading a photoshopped image (manipulation detection)

### Scenario 3: Test Admin Workflow
1. Login as regular user
2. Upload a payment proof
3. Logout and login as finance (`finance@amanga.id` / `admin123`)
4. Approve or reject the payment
5. Check if user credit is activated

### Scenario 4: Test Self-Learning
1. Upload a receipt
2. OCR will extract data with confidence scores
3. If OCR made mistakes, click "Ada yang Salah" (Something is wrong)
4. Provide correct values
5. System learns from your correction

---

## 📊 What's Real vs Simulated

| Feature | Status | Notes |
|---------|--------|-------|
| **User Registration** | ✅ Real | Accounts stored in database |
| **Login/Authentication** | ✅ Real | JWT tokens work |
| **File Upload** | ✅ Real | Images are stored |
| **OCR Extraction** | ✅ Real | Tesseract OCR processes images |
| **Image Analysis** | ✅ Real | ELA, metadata, noise detection |
| **Fraud Scoring** | ✅ Real | Algorithm calculates risk |
| **Payment Processing** | ❌ Simulated | No real money transferred |
| **Service Credits** | ❌ Simulated | Demo credits only |
| **Bank Integration** | ❌ Not Connected | No real bank APIs |
| **Notifications** | ⚠️ Mock Mode | Console logging only |

---

## 🏗️ Technical Stack (Live Demo)

### Server
- **Provider:** Alibaba Cloud Simple Application Server
- **Location:** Indonesia (Jakarta)
- **OS:** Ubuntu 20.04
- **RAM:** 2GB
- **Storage:** 40GB SSD

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **OCR:** Tesseract OCR
- **Image Processing:** OpenCV, Pillow
- **Validation:** Custom validators + Pydantic
- **Database:** Mock Mode (in-memory for demo)

### Frontend
- **UI:** Modern HTML5 + CSS3
- **Animations:** CSS3 transitions
- **Responsive:** Mobile-friendly
- **No Framework:** Vanilla JavaScript for simplicity

### Security
- **Rate Limiting:** Enabled
- **File Validation:** Enabled
- **Input Validation:** Enabled
- **JWT Authentication:** Enabled
- **HTTPS:** Not enabled (demo only, don't use real data)

---

## ⚠️ Security Warning

### This Demo is NOT Secure for Production Use

1. **No HTTPS/SSL** - Data transmitted in plain text
2. **Mock Database** - Data resets periodically
3. **Demo Credentials** - Well-known passwords
4. **No Real Authentication** - For testing only
5. **No Data Encryption** - Don't upload sensitive data

### DO NOT Upload:
- ❌ Real bank account numbers
- ❌ Real credit card numbers
- ❌ Personal identification numbers
- ❌ Sensitive financial documents
- ❌ Any data you want to keep private

### OK to Upload:
- ✅ Fake/simulated payment proofs
- ✅ Test receipts you create yourself
- ✅ Sample images for OCR testing
- ✅ Public domain receipt templates

---

## 📈 Demo Limitations

### Performance
- **Concurrent Users:** Limited by server resources (~10-20)
- **Upload Size:** Max 10MB per file
- **Processing Time:** 5-30 seconds per upload
- **Uptime:** Best effort (not guaranteed)

### Data Persistence
- **Mock Mode:** Data may reset on server restart
- **No Backups:** Demo data not backed up
- **No Guarantees:** Data may be lost anytime

### Features Disabled
- ❌ Real email notifications
- ❌ WhatsApp notifications
- ❌ Payment gateway integration
- ❌ Real bank API connections
- ❌ Production monitoring

---

## 🔄 Demo Data Reset

The demo server may be reset periodically:
- **Frequency:** Approximately once per month
- **What's Lost:** User accounts, uploaded images, feedback data
- **What Remains:** System configuration, OCR format database

**Don't rely on this demo for long-term data storage.**

---

## 📞 Reporting Issues

If you find bugs or issues with the live demo:

1. **GitHub Issues:** https://github.com/Therealratoshen/aman-ga/issues
2. **Include:**
   - What you were trying to do
   - What happened
   - Error messages (screenshots)
   - Browser and version

---

## 🚀 Deploy Your Own Instance

Want to run your own copy?

### Quick Deploy
```bash
ssh root@YOUR_SERVER_IP
git clone https://github.com/Therealratoshen/aman-ga.git
cd aman-ga
sudo ./deploy.sh
```

### Documentation
- **[DEPLOYMENT-SERVER.md](./DEPLOYMENT-SERVER.md)** - Complete guide
- **[QUICK-REFERENCE.md](./QUICK-REFERENCE.md)** - Common commands
- **[QUICKSTART.md](./QUICKSTART.md)** - 5-minute setup

---

## 📊 Demo Statistics

### Current Version
- **Version:** 2.1.0
- **Last Updated:** March 19, 2026
- **Uptime:** Best effort
- **Users:** Demo (reset periodically)
- **Uploads:** Demo (reset periodically)

### Features Active
- ✅ OCR Extraction
- ✅ Image Validation
- ✅ Fraud Scoring
- ✅ Self-Learning Feedback
- ✅ Admin Dashboard
- ✅ Rate Limiting
- ✅ Duplicate Detection

---

## 🎯 Purpose of This Demo

This demo serves several purposes:

1. **Educational** - Learn about OCR, image validation, fraud detection
2. **Portfolio** - Showcase technical skills
3. **Testing** - Test new features before production
4. **Community** - Get feedback from users
5. **Research** - Study OCR accuracy and learning patterns

---

## ❓ FAQ

### Q: Is this a real payment system?
**A:** No! This is a demo/POC. No real payments are processed.

### Q: Can I use this for my business?
**A:** Not as-is. You would need to:
- Set up proper security (HTTPS, encryption)
- Connect to real payment gateways
- Add compliance (PCI DSS, etc.)
- Implement proper data protection

### Q: Is my data safe?
**A:** No. This is a demo. Don't upload sensitive data. Data may be deleted anytime.

### Q: Can I contribute?
**A:** Yes! See [CONTRIBUTING.md](./CONTRIBUTING.md)

### Q: Will this stay online forever?
**A:** No guarantees. Demo may be taken down anytime.

---

## 📝 Summary

**Live Demo:** http://147.139.202.129/

**Purpose:** Educational/POC for OCR and fraud detection concepts

**Status:** ✅ Running (best effort uptime)

**Security:** ⚠️ Demo only - NOT for production use

**Data:** ⚠️ May be reset periodically

**Use For:** Testing, learning, experimentation

**NOT For:** Real payments, sensitive data, production use

---

**Last Updated:** March 19, 2026  
**Version:** 2.1.0  
**Contact:** Via GitHub Issues
