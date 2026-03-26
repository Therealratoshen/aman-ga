#!/usr/bin/env python3
"""
Targeted test to identify specific validation issues
"""

import sys
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from validators import PaymentValidator
from virtual_accounts import get_va_manager
from second_level_validator import SecondLevelValidator


def create_targeted_test_receipt():
    """Create a receipt specifically designed to pass all validations"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create receipt text that should be easily recognized by OCR
    receipt_text = f"""PT AMAN GA INDONESIA
Virtual Account Payment

Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Bank: BCA
VA Number: 888812345678
BCA 888812345678

Deskripsi: Pembayaran Layanan
Jumlah: Rp 100000
Nominal: 100000
Amount: 100000
ID Transaksi: TRXBCA001
No. Transaksi: TRXBCA001
Transaction ID: TRXBCA001

Thank you for your payment
Kode Pembayaran: 888812345678
    """
    
    # Add text to image with good spacing
    y_offset = 50
    for line in receipt_text.strip().split('\n'):
        if line.strip():
            draw.text((50, y_offset), line.strip(), fill='black')
            y_offset += 25  # Smaller spacing for more text
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def debug_validation_process():
    """Debug the validation process step by step"""
    print("="*80)
    print("DEBUGGING VALIDATION PROCESS")
    print("="*80)
    
    validator = PaymentValidator()
    second_level_validator = SecondLevelValidator()
    
    # Create a targeted test receipt
    print("\n1. Creating targeted test receipt...")
    test_receipt = create_targeted_test_receipt()
    
    # Step 1: File validation
    print("\n2. Testing file validation...")
    file_result = validator.validate_file(test_receipt, "targeted_test.png")
    print(f"   File validation: {'✅ PASS' if file_result.is_valid else '❌ FAIL'}")
    if not file_result.is_valid:
        print(f"   Error: {file_result.error_message}")
        return False
    
    # Step 2: Image analysis
    print("\n3. Testing image analysis...")
    image_analysis = validator.analyze_image(test_receipt)
    print(f"   Risk level: {image_analysis.risk_level}")
    print(f"   Quality score: {image_analysis.quality_score:.2f}")
    print(f"   Manipulation detected: {image_analysis.is_manipulated}")
    
    # Step 3: OCR extraction
    print("\n4. Testing OCR extraction...")
    ocr_result = validator.extract_ocr(test_receipt, "TRXBCA001")
    print(f"   OCR confidence: {ocr_result.confidence_score:.2f}")
    print(f"   Extracted text preview: '{ocr_result.extracted_text[:100]}...'")
    print(f"   Extracted amount: {ocr_result.extracted_amount}")
    print(f"   Extracted transaction ID: {ocr_result.extracted_transaction_id}")
    print(f"   Extracted bank: {ocr_result.extracted_bank}")
    
    # Step 4: VA validation
    print("\n5. Testing VA validation...")
    va_validation = ocr_result.va_validation
    print(f"   VA is valid: {va_validation.is_valid_va}")
    print(f"   Matched accounts: {va_validation.matched_accounts}")
    print(f"   First level status: {va_validation.first_level_status}")
    
    # Step 5: Amount validation (this might be the issue)
    print("\n6. Testing amount validation...")
    expected_amount = 100000
    extracted_amount = ocr_result.extracted_amount
    amount_result = validator.validate_amount(extracted_amount, expected_amount)
    print(f"   Expected amount: {expected_amount}")
    print(f"   Extracted amount: {extracted_amount}")
    print(f"   Amount validation: {'✅ PASS' if amount_result.is_valid else '❌ FAIL'}")
    print(f"   Variance: {amount_result.variance_percentage:.2%}")
    print(f"   Validation notes: {amount_result.validation_notes}")
    
    # Step 6: Data consistency check (this might be failing)
    print("\n7. Testing data consistency...")
    data_consistency = validator.verify_ocr_matches_form(ocr_result, type('obj', (object,), {
        'amount': expected_amount,
        'transaction_id': 'TRXBCA001',
        'bank_name': 'BCA'
    })())
    print(f"   OCR matches form: {data_consistency}")
    print(f"   OCR mismatches: {ocr_result.mismatches}")
    
    # Step 8: Second level validation
    print("\n8. Testing second level validation...")
    form_data = {
        "bank_name": "BCA",
        "amount": 100000,
        "transaction_id": "TRXBCA001",
        "transaction_date": datetime.now().isoformat()
    }
    
    second_result = second_level_validator.validate_second_level(
        ocr_result,
        image_analysis,
        form_data,
        validator
    )
    
    print(f"   Second level passed: {second_result['passed']}")
    print(f"   Recommendation: {second_result['recommendation']}")
    print(f"   Confidence score: {second_result['confidence_score']:.2f}")
    print(f"   Issues: {second_result['issues']}")
    print(f"   Warnings: {second_result['warnings']}")
    
    # Check specific validation components
    print("\n9. Checking specific validation components...")
    if 'amount_validation' in second_result:
        amt_val = second_result['amount_validation']
        print(f"   Amount validation in second level: {amt_val['is_valid']}")
    
    if 'debit_status_validation' in second_result:
        debit_val = second_result['debit_status_validation']
        print(f"   Debit status validation: {debit_val['status']}")
    
    # Determine overall success
    overall_success = (
        file_result.is_valid and
        va_validation.is_valid_va and
        va_validation.first_level_status == "VALIDATED" and
        second_result['passed']
    )
    
    print(f"\n10. Overall success: {'✅ YES' if overall_success else '❌ NO'}")
    
    print("\n" + "="*80)
    print("DEBUGGING COMPLETE")
    if overall_success:
        print("✅ ALL VALIDATIONS PASSING - SYSTEM READY")
    else:
        print("❌ SOME VALIDATIONS FAILING - NEEDS FIXING")
    print("="*80)
    
    return overall_success


if __name__ == "__main__":
    success = debug_validation_process()
    
    if success:
        print("\n🎉 SUCCESS: All validations are working correctly!")
        print("The system is ready for server deployment.")
    else:
        print("\n❌ ISSUES IDENTIFIED:")
        print("1. Check OCR extraction accuracy")
        print("2. Verify amount validation logic")
        print("3. Confirm data consistency checks")
        print("4. Ensure second level validation passes")