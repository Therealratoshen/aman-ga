# Enhanced Two-Level Validation System with Transaction, Amount, and Debit Status Validation

## Overview
The Aman ga? system now implements an enhanced three-tier validation system for payment receipts:

1. **First Level Validation**: Virtual Account (VA) and Transaction ID validation
2. **Second Level Validation**: Comprehensive receipt validation
3. **Additional Validations**: Amount and Debit Status validation

## First Level: Virtual Account and Transaction Validation

### 5 Virtual Accounts Defined
The system defines 5 Virtual Accounts for Indonesian banks with transaction prefixes:

1. **BCA VA** (ID: va_bca)
   - Account Number: 8888xxxxxx
   - Transaction Prefixes: ["BCA", "TRXBCA", "BCATRX"]
   - Pattern: `(?i)(?:8888\d{8}|BCA.*8888|\b8888\d{8}\b)`

2. **BRI VA** (ID: va_bri)
   - Account Number: 9999xxxxx
   - Transaction Prefixes: ["BRI", "TRXBRI", "BRITRX"]
   - Pattern: `(?i)(?:9999\d{7}|BRI.*9999|\b9999\d{7}\b)`

3. **Mandiri VA** (ID: va_mandiri)
   - Account Number: 7777xxxxxx
   - Transaction Prefixes: ["MANDIRI", "TRXMDR", "MDRTRX"]
   - Pattern: `(?i)(?:7777\d{8}|MANDIRI.*7777|\b7777\d{8}\b)`

4. **BNI VA** (ID: va_bni)
   - Account Number: 6666xxxxxx
   - Transaction Prefixes: ["BNI", "TRXBNI", "BNITRX"]
   - Pattern: `(?i)(?:6666\d{8}|BNI.*6666|\b6666\d{8}\b)`

5. **Permata VA** (ID: va_permata)
   - Account Number: 5555xxxxxx
   - Transaction Prefixes: ["PERMATA", "TRXPTM", "PTMTRX"]
   - Pattern: `(?i)(?:5555\d{8}|PERMATA.*5555|\b5555\d{8}\b)`

### First Level Validation Process
1. OCR extracts text from the uploaded receipt image
2. System checks if the extracted text contains any of the 5 VA patterns
3. Validates transaction ID against allowed prefixes for the matched VA
4. If both VA and transaction ID match, first level validation passes with status "VALIDATED"
5. If either fails, first level validation fails with status "REJECTED"
6. Only receipts passing first level proceed to second level validation

## Second Level: Comprehensive Validation

### Validation Components
If first level passes, the system performs comprehensive validation:

1. **OCR Confidence Check**: Ensures OCR confidence is above threshold (0.6)
2. **Image Risk Assessment**: Validates image risk level is acceptable (≤ MEDIUM)
3. **Data Consistency**: Compares OCR-extracted data with form data
4. **Receipt Format Validation**: Checks for proper receipt structure
5. **Amount Validation**: Compares extracted vs expected amounts
6. **Debit Status Validation**: Verifies transaction status (success/failure)
7. **Additional Business Rules**: Applies custom validation rules

### Second Level Validation Process
1. Validates OCR confidence score meets minimum threshold
2. Checks image analysis results for acceptable risk level
3. Compares extracted data (amount, transaction ID, date) with form data
4. Performs amount validation against expected values
5. Validates debit status to confirm transaction success
6. Evaluates receipt format consistency
7. Calculates overall confidence score
8. Provides recommendation: STRONGLY_ACCEPT, ACCEPT_WITH_CAUTION, MANUAL_REVIEW, or REJECT

## Additional Validations

### Amount Validation
- Compares extracted amount from OCR with expected amount from form
- Allows configurable variance threshold (default 5%)
- Validates amount matches expected range
- Flags discrepancies for review

### Debit Status Validation
- Checks receipt text for success/failed indicators
- Looks for debit/charge indicators
- Verifies transaction ID presence in receipt
- Confirms amount appears in receipt
- Determines if transaction was successfully processed

## Database Schema Updates

### New Fields in payment_proofs Table
- `va_validation_enabled`: BOOLEAN (default TRUE)
- `va_matched_accounts`: JSONB (stores array of matched VA IDs)
- `va_first_level_status`: TEXT (PENDING, VALIDATED, REJECTED)
- `va_second_level_status`: TEXT (PENDING, VALIDATED, REJECTED, SKIPPED)
- `va_validation_notes`: TEXT
- `va_validation_score`: DECIMAL(3,2) (0.00-1.00)

- `transaction_validation_enabled`: BOOLEAN (default TRUE)
- `transaction_validation_status`: TEXT (PENDING, VALIDATED, REJECTED)
- `transaction_validation_notes`: TEXT

- `amount_validation_enabled`: BOOLEAN (default TRUE)
- `amount_extracted`: INTEGER
- `amount_expected`: INTEGER
- `amount_variance_percentage`: DECIMAL(5,2)
- `amount_validation_status`: TEXT (PENDING, VALIDATED, REJECTED)
- `amount_validation_notes`: TEXT

- `debit_status_validation_enabled`: BOOLEAN (default TRUE)
- `is_debited`: BOOLEAN (default FALSE)
- `debit_status`: TEXT (PENDING, VERIFIED, FAILED)
- `debit_verification_method`: TEXT (OCR, API, MANUAL)
- `debit_verification_notes`: TEXT
- `debit_timestamp_verified`: TIMESTAMP

## API Endpoint Updates

### Receipt Validation Endpoint (`/receipt/validate`)
The endpoint now includes comprehensive three-tier validation:

1. **First Level**: Checks if receipt matches any of the 5 VAs and validates transaction ID
2. **Second Level**: Comprehensive validation for matching receipts
3. **Additional Validation**: Amount and debit status validation
4. **Response Structure**: Includes all validation results

### Response Format
```json
{
  "success": true,
  "validation_status": "COMPLETED",
  "first_level_validation": {
    "is_valid_va": true,
    "matched_accounts": ["va_bca"],
    "first_level_status": "VALIDATED",
    "transaction_validation": {
      "valid": true,
      "reason": "Transaction ID matches allowed prefix: BCA"
    }
  },
  "second_level_validation": {
    "passed": true,
    "recommendation": "STRONGLY_ACCEPT",
    "confidence_score": 0.85,
    "amount_validation": {
      "is_valid": true,
      "extracted_amount": 100000,
      "expected_amount": 100000,
      "variance_percentage": 0.0,
      "validation_notes": "Variance: 0.00%, Threshold: 5.00%, Status: PASS"
    },
    "debit_status_validation": {
      "is_debited": true,
      "status": "VERIFIED",
      "verification_method": "OCR",
      "verification_notes": "Success and debit indicators found in receipt",
      "timestamp_verified": "2026-03-25T00:00:00"
    }
  },
  "amount_validation": {
    "is_valid": true,
    "extracted_amount": 100000,
    "expected_amount": 100000,
    "variance_percentage": 0.0,
    "validation_notes": "Variance: 0.00%, Threshold: 5.00%, Status: PASS"
  },
  "debit_status_validation": {
    "is_debited": true,
    "status": "VERIFIED",
    "verification_method": "OCR",
    "verification_notes": "Success and debit indicators found in receipt",
    "timestamp_verified": "2026-03-25T00:00:00"
  },
  "...other fields": "..."
}
```

## Implementation Files

### New/Updated Files
1. `virtual_accounts.py`: Enhanced with transaction validation
2. `validators.py`: Added amount and debit status validation
3. `second_level_validator.py`: Updated with new validation checks
4. `main.py`: Updated endpoint with comprehensive validation
5. `mock_database.py`: Updated to include new validation fields
6. `database/schema_va_update.sql`: Updated schema with all new fields

## Benefits of Enhanced Validation

1. **Enhanced Security**: Validates both VA and transaction ID
2. **Amount Verification**: Ensures amounts match expectations
3. **Status Confirmation**: Verifies transaction was successfully debited
4. **Efficiency**: Quickly rejects invalid receipts at first level
5. **Accuracy**: Comprehensive validation for legitimate receipts
6. **Scalability**: Easy to add more VAs or validation rules
7. **Compliance**: Validates all aspects of payment processing

## Validation Indicators

### Success Indicators (Indonesian/English)
- 'success', 'berhasil', 'completed', 'selesai', 'paid', 'dibayar'
- 'processed', 'diproses', 'confirmed', 'disetujui', 'approved', 'disetujukan'

### Failure Indicators (Indonesian/English)
- 'failed', 'gagal', 'cancelled', 'dibatalkan', 'rejected', 'ditolak'
- 'pending', 'menunggu', 'waiting', 'error', 'kesalahan'

### Debit Indicators (Indonesian/English)
- 'debit', 'potong', 'pengurangan', 'keluar', 'outgoing', 'withdrawal'
- 'charged', 'charged to', 'dikenakan', 'biaya', 'fee', 'tarif'

The system now provides comprehensive validation covering Virtual Account matching, transaction ID verification, amount validation, and debit status confirmation, ensuring only legitimate and successful transactions are accepted.