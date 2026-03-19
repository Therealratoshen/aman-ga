# 🔒 Security Improvements - Aman ga? v2.0

## Overview

This document outlines all security improvements implemented to prevent fraud and ensure no false information is tolerated in the payment verification system.

---

## ✅ Implemented Security Features

### 1. **Strict Input Validation**

#### Amount Validation
- **Range**: Rp 100 - Rp 100,000,000
- **Type**: Integer only
- **Business Logic**: CEK_DASAR limited to Rp 1,000 for auto-approval

#### Transaction ID Validation
- **Length**: 5-50 characters
- **Pattern**: Alphanumeric, dash, underscore only (`^[A-Za-z0-9_-]+$`)
- **Blocked Patterns**: test, fake, demo, sample, example
- **Auto-uppercase**: Normalized to uppercase

#### Date Validation
- **Format**: ISO 8601 (YYYY-MM-DDTHH:MM:SS)
- **Future Check**: Cannot be more than 1 hour in future (timezone buffer)
- **History Limit**: Cannot be older than 365 days

#### Payment Method & Bank Validation
- **Enumerated Values**: Only predefined values accepted
- **Payment Methods**: BANK_TRANSFER, GOPAY, OVO, DANA, LINKAJA
- **Banks**: BCA, BRI, BNI, MANDIRI, PERMATA, DANAMON, CIMB, MAYBANK, BTN, OTHER

---

### 2. **File Upload Validation**

#### File Size
- **Minimum**: 10 KB (prevents 1x1 pixel images)
- **Maximum**: 10 MB (prevents DoS attacks)

#### File Type Detection
- **MIME Type Detection**: Uses `python-magic` for actual content detection (not just extension)
- **Allowed Types**: image/jpeg, image/png, image/webp
- **Rejected**: PDF, GIF, SVG (can contain scripts)

#### Image Dimensions
- **Minimum**: 200x200 pixels
- **Maximum**: 10,000x10,000 pixels
- **Aspect Ratio**: No restriction (different phone screens)

#### Image Hash
- **Algorithm**: Perceptual Hash (pHash)
- **Purpose**: Duplicate detection even if file is slightly modified
- **Storage**: Stored in database for future comparisons

---

### 3. **Duplicate Detection**

#### Transaction ID Duplicate
- **Check**: Exact match across all payment proofs
- **Risk Score**: +40 points

#### Image Duplicate
- **Check**: Perceptual hash similarity ≥95%
- **Scope**: Global (all users)
- **Risk Score**: +60 points

#### Transaction Pattern Duplicate
- **Check**: Same user + same amount + same date + same bank
- **Risk Score**: +35 points

---

### 4. **OCR Integration**

#### Text Extraction
- **Engine**: Tesseract OCR with Indonesian language support
- **Preprocessing**: Gaussian blur, grayscale conversion
- **Config**: OEM 3, PSM 6 (block of text)

#### Data Extraction
- **Amount**: Extracts "Rp 1.000.000" or "1.000.000" patterns
- **Transaction ID**: Looks for TRX, TXN, REF, No. Transaksi
- **Date**: Multiple date format support
- **Bank**: Matches bank names in text

#### Form-Image Verification
- **Amount Match**: Exact match required
- **Transaction ID Match**: Case-insensitive comparison
- **Bank Match**: Must match selected bank
- **Mismatch Penalty**: +25 points per mismatch (max 50)

#### Confidence Scoring
- **Low Confidence (<30%)**: +15 risk points
- **Medium Confidence (30-70%)**: Warning shown
- **High Confidence (>70%)**: Full validation

---

### 5. **AI Image Manipulation Detection**

#### Error Level Analysis (ELA)
- **Purpose**: Detect recompression artifacts
- **Method**: Recompress at 90% quality, compare difference
- **Threshold**: High variance indicates manipulation

#### Metadata Analysis
- **EXIF Check**: Missing metadata (common in screenshots)
- **Software Detection**: Photoshop, GIMP, Paint detected
- **Penalty**: +30 points if editing software detected

#### Noise Pattern Consistency
- **Method**: Local variance analysis
- **Detection**: Abrupt changes indicate splicing
- **Threshold**: Variance std > 1000

#### Copy-Move Forgery Detection
- **Method**: Block matching (simplified in v2.0)
- **Purpose**: Detect duplicated regions within image

#### Quality Assessment
- **Sharpness**: Laplacian variance
- **Brightness**: Mean pixel value
- **Score**: 0-1 (higher is better)

#### Screenshot Detection
- **Edge Density**: Screenshots have more sharp edges
- **Color Diversity**: Limited palette vs photos
- **Result**: Boolean (is_screenshot)

---

### 6. **Rate Limiting**

#### Authentication Endpoints
- **Login**: 5/minute, 20/hour per IP
- **Register**: 10/hour per IP
- **Violation Tracking**: 10 violations = 1 hour block

#### Payment Upload
- **Per Minute**: 3 uploads
- **Per Hour**: 20 uploads
- **Per Day**: 50 uploads

#### General API
- **Per Hour**: 500 requests
- **Per Minute**: 30 requests

#### Admin Actions
- **Per Minute**: 10 actions

#### IP Blocking
- **Threshold**: 10 rate limit violations in 1 hour
- **Block Duration**: 1 hour
- **Headers**: X-Forwarded-For, X-Real-IP support

---

### 7. **Security Headers**

```python
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

### 8. **CORS Hardening**

```python
allow_origins: ["http://localhost:3000", "http://147.139.202.129"]
allow_methods: ["GET", "POST", "PUT", "DELETE"]
allow_headers: ["Authorization", "Content-Type"]
max_age: 600  # Preflight cache 10 minutes
```

---

## 📊 Risk Scoring System

### Score Calculation

| Factor | Points | Trigger |
|--------|--------|---------|
| Previous fraud history | +50 | CONFIRMED fraud flag |
| Duplicate transaction ID | +40 | Exact match |
| Duplicate image | +60 | ≥95% hash similarity |
| Duplicate transaction pattern | +35 | Same amount+date+bank |
| Rapid submissions | +20 | >3 in 1 hour |
| Multiple rejections | +25 | ≥3 rejected payments |
| High amount (>Rp 100k) | +15 | Large transaction |
| Image manipulation | +70 | AI detection |
| High risk image | +30 | Risk indicators |
| Critical risk image | +50 | Multiple indicators |
| OCR mismatch (each) | +25 | Form ≠ Image |
| Low OCR confidence | +15 | <30% confidence |

### Risk Levels

| Level | Score Range | Action |
|-------|-------------|--------|
| **LOW** | 0-29 | Auto-approve if <Rp 1,000 |
| **MEDIUM** | 30-49 | Manual review required |
| **HIGH** | 50-69 | Manual review + notification |
| **CRITICAL** | 70+ | Blocked + fraud flag created |

---

## 🗄️ Database Schema Additions

### New Columns in `payment_proofs`

```sql
proof_image_hash TEXT              -- Perceptual hash
proof_image_metadata JSONB         -- EXIF, dimensions
ocr_extracted_amount INTEGER       -- OCR result
ocr_extracted_transaction_id TEXT  -- OCR result
ocr_extracted_date TIMESTAMP       -- OCR result
ocr_extracted_bank TEXT            -- OCR result
ocr_confidence_score DECIMAL       -- 0.00-1.00
ocr_matches_form BOOLEAN           -- Validation result
ocr_mismatches JSONB               -- Array of mismatches
image_manipulation_detected BOOLEAN -- AI result
image_risk_level TEXT              -- LOW/MEDIUM/HIGH/CRITICAL
image_quality_score DECIMAL        -- 0.00-1.00
fraud_risk_score INTEGER           -- 0-200
fraud_risk_factors JSONB           -- Array of factors
```

### Constraints

```sql
CHECK (amount >= 100 AND amount <= 100000000)
CHECK (LENGTH(transaction_id) >= 5 AND LENGTH(transaction_id) <= 50)
CHECK (bank_name IN ('BCA', 'BRI', ...))
CHECK (ocr_confidence_score >= 0 AND ocr_confidence_score <= 1)
CHECK (fraud_risk_score >= 0 AND fraud_risk_score <= 200)
```

---

## 🔍 Validation Flow

```
User Upload → File Validation
    ├─ Size check (10KB-10MB)
    ├─ MIME type detection
    ├─ Dimension check (200x200 min)
    └─ Generate perceptual hash
         ↓
Form Data Validation
    ├─ Amount range (Rp 100-100M)
    ├─ Transaction ID format
    ├─ Date validation (not future, not >1 year)
    └─ Enum validation (bank, payment method)
         ↓
Duplicate Detection
    ├─ Transaction ID check
    ├─ Image hash similarity
    └─ Transaction pattern check
         ↓
OCR Processing
    ├─ Extract text from image
    ├─ Extract amount, ID, date, bank
    └─ Compare with form data
         ↓
Image Analysis
    ├─ ELA (recompression detection)
    ├─ Metadata analysis
    ├─ Noise pattern check
    └─ Quality assessment
         ↓
Fraud Risk Scoring
    ├─ Calculate total risk score
    ├─ Determine risk level
    └─ Decision:
        • LOW (0-29) → Auto-approve if eligible
        • MEDIUM (30-49) → Manual review
        • HIGH (50-69) → Manual review + alert
        • CRITICAL (70+) → Block + fraud flag
```

---

## 🚨 What Happens with Fake/Random Images

### Cat Photo Upload
```
1. File validation: ✅ Pass (valid image)
2. OCR: ⚠️ Low confidence (no text detected)
3. Image analysis: ⚠️ Not a screenshot
4. Risk score: +15 (low OCR confidence)
5. Result: Manual review required
```

### Meme Upload
```
1. File validation: ✅ Pass
2. OCR: ⚠️ May detect random text
3. Form-Image match: ❌ Mismatch (+25 points)
4. Risk score: 25-50 depending on content
5. Result: Likely manual review or rejection
```

### Photoshopped Proof
```
1. File validation: ✅ Pass
2. ELA analysis: ⚠️ Manipulation detected (+70)
3. Metadata: ⚠️ Photoshop detected (+30)
4. Risk score: 100+ → CRITICAL
5. Result: BLOCKED + fraud flag created
```

### Same Image Reused
```
1. File validation: ✅ Pass
2. Hash check: ❌ Duplicate found (+60)
3. Risk score: 60+ → HIGH
4. Result: Manual review + alert
```

---

## 📦 New Dependencies

```txt
slowapi>=0.1.9          # Rate limiting
Pillow>=10.2.0          # Image processing
pytesseract>=0.3.10     # OCR
opencv-python-headless>=4.9.0  # Image analysis
numpy>=1.26.0           # Numerical operations
imagehash>=4.3.1        # Perceptual hashing
python-magic>=0.4.27    # MIME type detection
pydantic-settings>=2.1.0  # Settings management
```

### System Requirements

```bash
# Install Tesseract OCR
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-ind

# Install libmagic
# macOS
brew install libmagic

# Ubuntu/Debian
sudo apt-get install libmagic1
```

---

## 🧪 Testing

### Test Valid Payment
```bash
curl -X POST "http://localhost:8000/payment/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "service_type=CEK_DASAR" \
  -F "amount=1000" \
  -F "payment_method=BANK_TRANSFER" \
  -F "bank_name=BCA" \
  -F "transaction_id=TRX20240319ABC123" \
  -F "transaction_date=2024-03-19T10:00:00" \
  -F "proof_image=@valid_screenshot.png"
```

### Test Invalid Amount
```bash
curl -X POST "http://localhost:8000/payment/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "service_type=CEK_DASAR" \
  -F "amount=50" \  # Below minimum
  -F "payment_method=BANK_TRANSFER" \
  -F "bank_name=BCA" \
  -F "transaction_id=TRX123" \
  -F "transaction_date=2024-03-19T10:00:00" \
  -F "proof_image=@screenshot.png"

# Response: 400 Bad Request - Amount must be between Rp 100 and Rp 100,000,000
```

### Test Rate Limiting
```bash
# Make 6 rapid login attempts
for i in {1..6}; do
  curl -X POST "http://localhost:8000/token" \
    -d "username=admin@amanga.id&password=wrong"
done

# 6th attempt: 429 Too Many Requests
```

---

## 📈 Monitoring

### Key Metrics to Track

1. **Validation Failures**
   - File rejections (size, type, dimensions)
   - Input validation errors
   - OCR confidence distribution

2. **Fraud Detection**
   - Risk score distribution
   - Duplicate detection rate
   - Manipulation detection rate

3. **Rate Limiting**
   - Requests per endpoint
   - Rate limit violations
   - Blocked IPs

4. **Processing Time**
   - OCR processing time
   - Image analysis time
   - Total upload time

---

## 🔮 Future Improvements (v3.0)

1. **Advanced AI Models**
   - Integration with AWS Rekognition
   - Google Cloud Vision API
   - Custom fraud detection ML model

2. **Behavioral Analysis**
   - User behavior patterns
   - Device fingerprinting
   - Geolocation analysis

3. **Real-time Alerts**
   - WhatsApp notifications for high-risk
   - Email alerts for admins
   - Slack/Discord integration

4. **Enhanced OCR**
   - Multi-language support
   - Handwritten text detection
   - QR code scanning

---

## 📞 Support

For security issues, please contact the development team or open an issue on GitHub.

**Last Updated**: March 19, 2026
**Version**: 2.0.0
