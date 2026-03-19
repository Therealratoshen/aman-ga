# 🔮 Self-Learning OCR System - Aman ga? v2.1

## 📋 Overview

The Aman ga? system now includes a **self-learning OCR system** inspired by OpenCLAW configuration patterns. This system:

1. **Never gives fully confident answers** - Always flags uncertainty
2. **Learns from every user correction** - Continuous improvement
3. **Adapts to new receipt formats** - Extensible configuration
4. **Provides transparency** - Shows alternative interpretations
5. **Handles receipt diversity** - Indonesian bank/e-wallet formats

---

## 🎯 Key Principles

### 1. Uncertainty First Approach

> **Receipts can be fake but look real, or real but look fake.**

The system always:
- Shows confidence scores (never 100%)
- Provides alternative interpretations
- Flags potential OCR errors
- Requests user verification for low-confidence extractions

### 2. Self-Learning from Feedback

Every user interaction improves the system:
- **Corrections** → Adjust extraction patterns
- **Confirmations** → Reinforce current patterns
- **Flags** → Mark problematic formats

### 3. Receipt Format Diversity

Indonesian receipts vary widely:
- **Bank transfers**: BCA, BRI, BNI, Mandiri, etc.
- **E-wallets**: GoPay, OVO, DANA, LinkAja
- **Formats**: SMS, email, app screenshots, PDF exports

---

## 🗄️ Receipt Format Database

### Supported Providers

| Provider | Type | Colors | QR Code | Confidence |
|----------|------|--------|---------|------------|
| BCA | Bank | Blue (#00529F) | Yes | Learning |
| BRI | Bank | Blue+Red | Yes | Learning |
| BNI | Bank | Red (#E3000B) | Yes | Learning |
| Mandiri | Bank | Blue+Yellow | Yes | Learning |
| GoPay | E-wallet | Green (#00AA13) | Yes | Learning |
| OVO | E-wallet | Purple (#4C3494) | Yes | Learning |
| DANA | E-wallet | Blue (#118EEA) | Yes | Learning |
| LinkAja | E-wallet | Red (#E3000B) | Yes | Learning |

### Format Configuration Structure

```json
{
  "provider": "BCA",
  "bank_name": "Bank Central Asia",
  "amount_patterns": [
    "Rp[\\s\\.]*(\\d+[\\.\\d]*)",
    "Jumlah[\\s:]+Rp[\\s]*(\\d+[\\.\\d]*)"
  ],
  "transaction_id_patterns": [
    "TRX[\\s:]*([A-Z0-9]+)",
    "No\\.\\s*Transaksi[\\s:]*([A-Z0-9]+)"
  ],
  "date_patterns": [
    "(\\d{2}/\\d{2}/\\d{4}\\s+\\d{2}:\\d{2}:\\d{2})"
  ],
  "typical_colors": ["#00529F", "#00A3E0", "#FFFFFF"],
  "logo_position": "top-center",
  "has_qr_code": true,
  "has_watermark": true,
  "font_family": "Arial",
  "font_sizes": [12, 14, 16, 18, 24],
  "width_pixels": 720,
  "height_pixels": 1280,
  "aspect_ratio": 0.56,
  "sample_count": 0,
  "confidence_score": 0.5,
  "last_updated": null
}
```

---

## 🧠 Self-Learning Mechanism

### Learning Flow

```
User Uploads Receipt
        ↓
OCR Extraction with Confidence Scores
        ↓
Show Results + Uncertainty Flags
        ↓
User Provides Feedback
        ↓
System Learns from Feedback
        ↓
Update Pattern Weights
        ↓
Improve Future Extractions
```

### Feedback Types

1. **CORRECTION** - User fixes OCR mistakes
   - Adjusts extraction patterns
   - Updates confidence for specific fields
   - Records common error patterns

2. **CONFIRMATION** - User confirms accuracy
   - Reinforces current patterns
   - Increases confidence score
   - Marks format as reliable

3. **FLAG** - User reports problems
   - Marks receipt as problematic
   - Triggers manual review
   - May indicate fraud

### Learning Metrics

```json
{
  "total_samples": 1000,
  "total_feedback": 350,
  "correction_rate": 0.15,
  "overall_accuracy": 0.85,
  "amount_accuracy": 0.88,
  "transaction_id_accuracy": 0.82,
  "date_accuracy": 0.91,
  "avg_confidence": 0.75,
  "confidence_calibration": 0.70,
  "provider_accuracy": {
    "BCA": 0.88,
    "BRI": 0.85,
    "MANDIRI": 0.87,
    "GOPAY": 0.82
  }
}
```

---

## 🔍 Uncertainty Reporting

### Confidence Levels

| Level | Score | Action |
|-------|-------|--------|
| **LOW** | < 50% | Flag for manual verification |
| **MEDIUM** | 50-70% | Show warning, suggest verification |
| **HIGH** | 70-90% | Likely accurate |
| **VERY HIGH** | > 90% | Very reliable (but never 100%) |

### Uncertainty Flags

- `LOW_CONFIDENCE_EXTRACTION` - Overall confidence below threshold
- `MEDIUM_CONFIDENCE_EXTRACTION` - Some fields uncertain
- `POSSIBLE_OCR_ERROR` - Common OCR mistake patterns detected
- `FORMAT_MISMATCH` - Doesn't match known format
- `ALTERNATIVE_INTERPRETATIONS` - Multiple valid readings

### Alternative Interpretations

For each field, the system provides alternatives:

**Amount:**
- Primary: Rp 100.000
- Alternative: Rp 100.000.000 (possible decimal shift)

**Transaction ID:**
- Primary: TRX2024ABC123
- Alternative: TRX2024ABCI23 (1/I confusion)

**Date:**
- Primary: 19/03/2024
- Alternative: 03/19/2024 (DD/MM vs MM/DD)

---

## 🎨 User Interface

### Modern Smooth UI Features

1. **Gradient Backgrounds** - Beautiful visual design
2. **Smooth Animations** - Fade, slide, scale effects
3. **Real-time Feedback** - Loading states, progress
4. **Confidence Visualization** - Color-coded meters
5. **Interactive Feedback** - Easy correction interface
6. **Responsive Design** - Works on all devices

### Feedback Interface

Users can:
- ✅ Confirm OCR results are correct
- ✏️ Correct specific fields
- 📝 Add notes about receipt format
- ⭐ Rate receipt quality
- 🏷️ Mark as legitimate or suspicious

---

## 📡 API Endpoints

### Submit Feedback

```bash
POST /feedback/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_proof_id": "payment-123",
  "feedback_type": "CORRECTION",
  "corrected_amount": 100000,
  "corrected_transaction_id": "TRX123",
  "corrected_fields": ["amount", "transaction_id"],
  "notes": "OCR salah baca angka 8 jadi B",
  "is_legitimate_receipt": true,
  "quality_rating": 5
}
```

### Get Uncertainty Report

```bash
GET /feedback/uncertainty-report/{payment_id}
Authorization: Bearer <token>

Response:
{
  "overall_confidence": 0.65,
  "confidence_level": "MEDIUM",
  "amount_confidence": 0.80,
  "transaction_id_confidence": 0.50,
  "uncertainty_flags": ["MEDIUM_CONFIDENCE_EXTRACTION"],
  "warnings": ["⚠️ Beberapa field mungkin tidak akurat."],
  "alternatives": {
    "amount": [{"value": "100000", "reason": "Primary"}],
    "transaction_id": [
      {"value": "TRX123", "reason": "Primary"},
      {"value": "TRXI23", "reason": "Possible 1/I confusion"}
    ]
  },
  "needs_manual_verification": true
}
```

### Get Learning Metrics

```bash
GET /feedback/learning-metrics
Authorization: Bearer <token>

Response:
{
  "total_samples": 1000,
  "total_feedback": 350,
  "overall_accuracy": 0.85,
  "provider_accuracy": {
    "BCA": 0.88,
    "BRI": 0.85
  },
  "accuracy_trend": [0.75, 0.78, 0.80, 0.82, 0.83, 0.85, 0.87]
}
```

### Get Receipt Formats

```bash
GET /receipt-formats

Response:
{
  "formats": [
    {
      "provider": "BCA",
      "bank_name": "Bank Central Asia",
      "sample_count": 150,
      "confidence_score": 0.85,
      "typical_colors": ["#00529F", "#00A3E0"],
      "has_qr_code": true
    }
  ]
}
```

---

## 🔧 Configuration Files

### Location

```
backend/ocr_config/
├── receipt_formats.json    # Known receipt format patterns
├── learning_metrics.json   # Learning progress tracking
└── error_patterns.json     # Common OCR errors by provider
```

### Updating Formats

Users can suggest improvements:

```bash
POST /receipt-formats/{provider}/improve
Authorization: Bearer <token>
Content-Type: application/json

{
  "suggested_pattern": "New regex pattern",
  "reason": "Current pattern misses some receipts",
  "example_receipt": "base64_encoded_image"
}
```

---

## 📊 How to Know if Receipt is Legit

### Multi-Layer Verification

1. **Visual Analysis**
   - Color matching with known format
   - Logo position verification
   - Font consistency check
   - QR code presence

2. **OCR Cross-Validation**
   - Extract amount from multiple locations
   - Compare transaction ID format
   - Verify date consistency

3. **Metadata Analysis**
   - Image manipulation detection
   - EXIF data consistency
   - Compression artifact analysis

4. **Pattern Matching**
   - Compare with known legitimate receipts
   - Check for template consistency
   - Verify security features

### Red Flags

- ⚠️ Colors don't match provider
- ⚠️ Font looks different from standard
- ⚠️ Transaction ID format unusual
- ⚠️ Amount appears modified
- ⚠️ Date inconsistent with metadata
- ⚠️ Image shows manipulation signs

### Green Flags

- ✅ Colors match provider exactly
- ✅ Font family and size consistent
- ✅ Transaction ID follows known pattern
- ✅ Amount appears in expected locations
- ✅ Date matches metadata timestamp
- ✅ No manipulation detected

---

## 🚀 Installation

### System Requirements

```bash
# Python dependencies
pip install -r requirements.txt

# System dependencies
# macOS
brew install tesseract libmagic

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-ind libmagic1
```

### Database Migration

```sql
-- Add feedback tables
CREATE TABLE ocr_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_proof_id UUID REFERENCES payment_proofs(id),
    user_id UUID REFERENCES users(id),
    feedback_type TEXT CHECK (feedback_type IN ('CORRECTION', 'CONFIRMATION', 'FLAG')),
    corrected_amount INTEGER,
    corrected_transaction_id TEXT,
    corrected_date TEXT,
    corrected_bank TEXT,
    corrected_fields JSONB,
    notes TEXT,
    is_legitimate_receipt BOOLEAN,
    quality_rating INTEGER CHECK (quality_rating >= 1 AND quality_rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE receipt_format_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider TEXT NOT NULL,
    suggested_by UUID REFERENCES users(id),
    suggested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    feedback JSONB,
    status TEXT DEFAULT 'PENDING'
);
```

---

## 📈 Learning Progress

### Initial State

- Confidence: 50% (neutral)
- Samples: 0
- Patterns: Basic regex

### After 100 Samples

- Confidence: 70-80%
- Patterns: Refined based on feedback
- Error rate: < 15%

### After 1000 Samples

- Confidence: 85-90%
- Patterns: Provider-specific optimization
- Error rate: < 10%

### Continuous Improvement

The system never stops learning:
- New receipt formats added regularly
- Patterns refined with each correction
- Accuracy improves over time

---

## 🎯 Best Practices

### For Users

1. **Always verify low-confidence results**
   - Check alternative interpretations
   - Compare with original receipt

2. **Provide detailed feedback**
   - Explain what was wrong
   - Suggest correct values
   - Rate receipt quality

3. **Report new formats**
   - Submit unfamiliar receipt types
   - Help expand format database

### For Admins

1. **Review learning metrics regularly**
   - Check accuracy trends
   - Identify problematic providers
   - Monitor confidence calibration

2. **Validate format suggestions**
   - Review user submissions
   - Test new patterns
   - Update configuration

3. **Monitor uncertainty patterns**
   - High uncertainty may indicate:
     - New receipt format
     - OCR model issues
     - Potential fraud

---

## 🔮 Future Enhancements

1. **Deep Learning Integration**
   - Train custom OCR model on Indonesian receipts
   - Improve accuracy for low-quality images

2. **Automated Pattern Discovery**
   - Cluster similar receipts automatically
   - Generate patterns from samples

3. **Collaborative Learning**
   - Share learnings across instances
   - Community-driven format database

4. **Advanced Fraud Detection**
   - ML-based manipulation detection
   - Cross-reference with fraud database

---

## 📞 Support

- **Documentation**: See all `.md` files in repo
- **API Docs**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Config Location**: `backend/ocr_config/`

---

**Version**: 2.1.0  
**Last Updated**: March 19, 2026  
**Status**: ✅ Production Ready with Self-Learning

---

<div align="center">

### 🔮 Aman ga? — Never 100% Confident, Always Learning

The system embraces uncertainty and learns from every interaction.

[⭐ Star](https://github.com/Therealratoshen/aman-ga) • [🍴 Fork](https://github.com/Therealratoshen/aman-ga/fork) • [📋 Issues](https://github.com/Therealratoshen/aman-ga/issues)

**Made with ❤️ in Indonesia**

</div>
