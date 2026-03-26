# Two-Level Validation System with Virtual Accounts

## Overview
The Aman ga? system now implements a comprehensive two-level validation system for payment receipts:

1. **First Level Validation**: Virtual Account (VA) validation
2. **Second Level Validation**: Comprehensive receipt validation

## First Level: Virtual Account Validation

### 5 Virtual Accounts Defined
The system defines 5 Virtual Accounts for Indonesian banks:

1. **BCA VA** (ID: va_bca)
   - Account Number: 8888xxxxxx
   - Pattern: `(?i)(?:8888\d{8}|BCA.*8888|\b8888\d{8}\b)`

2. **BRI VA** (ID: va_bri)
   - Account Number: 9999xxxxx
   - Pattern: `(?i)(?:9999\d{7}|BRI.*9999|\b9999\d{7}\b)`

3. **Mandiri VA** (ID: va_mandiri)
   - Account Number: 7777xxxxxx
   - Pattern: `(?i)(?:7777\d{8}|MANDIRI.*7777|\b7777\d{8}\b)`

4. **BNI VA** (ID: va_bni)
   - Account Number: 6666xxxxxx
   - Pattern: `(?i)(?:6666\d{8}|BNI.*6666|\b6666\d{8}\b)`

5. **Permata VA** (ID: va_permata)
   - Account Number: 5555xxxxxx
   - Pattern: `(?i)(?:5555\d{8}|PERMATA.*5555|\b5555\d{8}\b)`

### First Level Validation Process
1. OCR extracts text from the uploaded receipt image
2. System checks if the extracted text contains any of the 5 VA patterns
3. If a match is found, first level validation passes with status "VALIDATED"
4. If no match is found, first level validation fails with status "REJECTED"
5. Only receipts passing first level proceed to second level validation

## Second Level: Comprehensive Validation

### Validation Components
If first level passes, the system performs comprehensive validation:

1. **OCR Confidence Check**: Ensures OCR confidence is above threshold (0.6)
2. **Image Risk Assessment**: Validates image risk level is acceptable (≤ MEDIUM)
3. **Data Consistency**: Compares OCR-extracted data with form data
4. **Receipt Format Validation**: Checks for proper receipt structure
5. **Additional Business Rules**: Applies custom validation rules

### Second Level Validation Process
1. Validates OCR confidence score meets minimum threshold
2. Checks image analysis results for acceptable risk level
3. Compares extracted data (amount, transaction ID, date) with form data
4. Evaluates receipt format consistency
5. Calculates overall confidence score
6. Provides recommendation: STRONGLY_ACCEPT, ACCEPT_WITH_CAUTION, MANUAL_REVIEW, or REJECT

## Database Schema Updates

### New Fields in payment_proofs Table
- `va_validation_enabled`: BOOLEAN (default TRUE)
- `va_matched_accounts`: JSONB (stores array of matched VA IDs)
- `va_first_level_status`: TEXT (PENDING, VALIDATED, REJECTED)
- `va_second_level_status`: TEXT (PENDING, VALIDATED, REJECTED, SKIPPED)
- `va_validation_notes`: TEXT
- `va_validation_score`: DECIMAL(3,2) (0.00-1.00)

### New Virtual Accounts Table
- `virtual_accounts`: Stores configuration for the 5 VAs
- Includes ID, name, bank code, account number, description, and regex pattern

## API Endpoint Updates

### Receipt Validation Endpoint (`/receipt/validate`)
The endpoint now includes two-level validation:

1. **First Level**: Checks if receipt matches any of the 5 VAs
2. **Conditional Second Level**: Only proceeds if first level passes
3. **Response Structure**: Includes both levels' validation results

### Response Format
```json
{
  "success": true,
  "validation_status": "COMPLETED",
  "first_level_validation": {
    "is_valid_va": true,
    "matched_accounts": ["va_bca"],
    "first_level_status": "VALIDATED"
  },
  "second_level_validation": {
    "passed": true,
    "recommendation": "STRONGLY_ACCEPT",
    "confidence_score": 0.85
  },
  "...other fields": "..."
}
```

## Implementation Files

### New Files
1. `virtual_accounts.py`: Defines VA configuration and validation logic
2. `second_level_validator.py`: Implements comprehensive validation rules
3. `test_two_level_validation.py`: Comprehensive tests for the system

### Modified Files
1. `validators.py`: Updated to include VA validation in OCR extraction
2. `main.py`: Updated endpoint to implement two-level validation
3. `mock_database.py`: Updated to include VA validation fields
4. `database/schema_va_update.sql`: Updated schema with VA fields

## Benefits of Two-Level Validation

1. **Efficiency**: Quickly rejects non-matching receipts at first level
2. **Security**: Ensures only authorized VAs are processed
3. **Accuracy**: Comprehensive validation for legitimate receipts
4. **Scalability**: Easy to add more VAs or validation rules
5. **Flexibility**: Can be customized for different business requirements

## Testing

The system includes comprehensive tests that verify:
- VA pattern matching works correctly
- First level validation rejects non-matching receipts
- Second level validation processes matching receipts
- Database fields are properly updated
- API responses include correct validation status