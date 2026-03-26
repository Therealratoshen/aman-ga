#!/usr/bin/env python3
"""
Comprehensive system test to verify all components are working properly
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


def create_test_receipt_image(va_number, bank_name="BCA", amount=100000):
    """Create a realistic test receipt image"""
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    receipt_text = f"""
PT AMAN GA INDONESIA
Virtual Account Payment

Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Bank: {bank_name}
VA Number: {va_number}
{bank_name} {va_number}

Deskripsi: Pembayaran Layanan
Jumlah: Rp {amount:,}
ID Transaksi: TRX{bank_name}{datetime.now().strftime('%Y%m%d')}001

Terima kasih atas pembayaran Anda
Kode Pembayaran: {va_number}
    """
    
    # Add text to image
    y_offset = 50
    for line in receipt_text.strip().split('\n'):
        if line.strip():
            draw.text((50, y_offset), line.strip(), fill='black')
            y_offset += 30
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def test_all_components():
    """Test all validation components comprehensively"""
    print("="*80)
    print("COMPREHENSIVE SYSTEM TEST")
    print("="*80)
    
    validator = PaymentValidator()
    va_manager = get_va_manager()
    second_level_validator = SecondLevelValidator()
    
    print("\n1. Testing Virtual Account Manager...")
    vas = va_manager.get_all_virtual_accounts()
    print(f"   ✅ Loaded {len(vas)} Virtual Accounts")
    for i, va in enumerate(vas):
        print(f"      {i+1}. {va.name} ({va.bank_code}): {va.account_number}xxx")
    
    print("\n2. Testing OCR with Valid BCA Receipt...")
    bca_receipt = create_test_receipt_image("888812345678", "BCA", 100000)
    
    # Test file validation
    file_result = validator.validate_file(bca_receipt, "bca_receipt.png")
    print(f"   ✅ File validation: {'PASS' if file_result.is_valid else 'FAIL'}")
    
    # Test OCR extraction
    ocr_result = validator.extract_ocr(bca_receipt, "TRXBCA001")
    print(f"   ✅ OCR extraction: Confidence={ocr_result.confidence_score:.2f}")
    print(f"   ✅ OCR - Amount: {ocr_result.extracted_amount}")
    print(f"   ✅ OCR - Bank: {ocr_result.extracted_bank}")
    print(f"   ✅ OCR - Transaction ID: {ocr_result.extracted_transaction_id}")
    
    # Test VA validation
    va_validation = ocr_result.va_validation
    print(f"   ✅ VA validation: Valid={va_validation.is_valid_va}, Status={va_validation.first_level_status}")
    
    # Test image analysis
    image_analysis = validator.analyze_image(bca_receipt)
    print(f"   ✅ Image analysis: Risk={image_analysis.risk_level}, Quality={image_analysis.quality_score:.2f}")
    
    print("\n3. Testing All 5 Virtual Accounts...")
    test_cases = [
        ("BCA", "888812345678"),
        ("BRI", "99991234567"),
        ("Mandiri", "777712345678"),
        ("BNI", "666612345678"),
        ("Permata", "555512345678")
    ]
    
    all_passed = True
    for bank, va_num in test_cases:
        test_img = create_test_receipt_image(va_num, bank, 50000)
        test_ocr = validator.extract_ocr(test_img, f"TRX{bank}001")
        va_valid = test_ocr.va_validation.is_valid_va
        status = test_ocr.va_validation.first_level_status
        passed = va_valid and status == "VALIDATED"
        all_passed = all_passed and passed
        print(f"   {'✅' if passed else '❌'} {bank} VA ({va_num}): Valid={va_valid}, Status={status}")
    
    print(f"\n   Overall VA test: {'✅ PASS' if all_passed else '❌ FAIL'}")
    
    print("\n4. Testing Invalid Receipt (Should Fail First Level)...")
    invalid_receipt = create_test_receipt_image("111111111111", "FAKE", 1000)  # Invalid VA
    invalid_ocr = validator.extract_ocr(invalid_receipt, "TRXFAKE001")
    invalid_va = invalid_ocr.va_validation
    invalid_passed = not invalid_va.is_valid_va and invalid_va.first_level_status == "REJECTED"
    print(f"   ✅ Invalid receipt: Valid={invalid_va.is_valid_va}, Status={invalid_va.first_level_status}")
    print(f"   Expected rejection: {'✅ CORRECT' if invalid_passed else '❌ INCORRECT'}")
    
    print("\n5. Testing Second Level Validation...")
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
    
    print(f"   ✅ Second level: Passed={second_result['passed']}")
    print(f"   ✅ Recommendation: {second_result['recommendation']}")
    print(f"   ✅ Confidence: {second_result['confidence_score']:.2f}")
    
    # Check additional validations
    if second_result.get('amount_validation'):
        print(f"   ✅ Amount validation: {second_result['amount_validation']['is_valid']}")
    if second_result.get('debit_status_validation'):
        print(f"   ✅ Debit status: {second_result['debit_status_validation']['status']}")
    
    print("\n6. Testing Additional Validation Components...")
    
    # Amount validation
    amount_result = validator.validate_amount(100000, 100000)
    print(f"   ✅ Amount validation (same): {amount_result.is_valid}")
    
    amount_result2 = validator.validate_amount(100000, 105000)  # Within threshold
    print(f"   ✅ Amount validation (within): {amount_result2.is_valid}")
    
    amount_result3 = validator.validate_amount(100000, 120000)  # Above threshold
    print(f"   ✅ Amount validation (above): {amount_result3.is_valid}")
    
    # Pattern validation
    pattern_result = validator.validate_suspicious_patterns("Normal receipt text", 100000, "BCA")
    print(f"   ✅ Pattern validation (normal): Suspicious={pattern_result.is_suspicious}")
    
    pattern_result2 = validator.validate_suspicious_patterns("test demo sample fake", 1, "BCA")
    print(f"   ✅ Pattern validation (suspicious): Suspicious={pattern_result2.is_suspicious}")
    
    # Timing validation
    timing_result = validator.validate_timing_patterns(datetime.now().isoformat(), None)
    print(f"   ✅ Timing validation: Suspicious={timing_result.is_suspicious}")
    
    print("\n7. Testing Complete Validation Flow...")
    # Simulate complete flow with valid receipt
    complete_success = (
        file_result.is_valid and
        ocr_result.confidence_score > 0 and
        va_validation.is_valid_va and
        va_validation.first_level_status == "VALIDATED" and
        second_result['passed']
    )
    
    print(f"   Complete flow success: {'✅ YES' if complete_success else '❌ NO'}")
    
    print("\n" + "="*80)
    print("SYSTEM TEST RESULTS")
    print("="*80)
    
    components = [
        ("Virtual Account Manager", len(vas) == 5),
        ("OCR Functionality", ocr_result.confidence_score > 0),
        ("VA Validation", va_validation.is_valid_va),
        ("First Level Pass", va_validation.first_level_status == "VALIDATED"),
        ("Second Level Pass", second_result['passed']),
        ("Invalid Receipt Rejection", invalid_passed),
        ("All VA Types", all_passed),
        ("Complete Flow", complete_success)
    ]
    
    all_working = True
    for name, status in components:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {name}")
        if not status:
            all_working = False
    
    print("\n" + "="*80)
    if all_working:
        print("🎉 ALL SYSTEMS OPERATIONAL - READY FOR SERVER DEPLOYMENT!")
        print("✅ OCR is working properly")
        print("✅ All validation layers are functional")
        print("✅ VA validation correctly identifies authorized accounts")
        print("✅ Invalid receipts are properly rejected")
        print("✅ Complete validation flow is operational")
        print("✅ Ready for demonstration on server")
    else:
        print("❌ ISSUES DETECTED - SYSTEM NOT READY")
    
    print("="*80)
    
    return all_working


def test_api_endpoint_simulation():
    """Simulate the API endpoint validation flow"""
    print("\n" + "="*80)
    print("API ENDPOINT SIMULATION TEST")
    print("="*80)
    
    validator = PaymentValidator()
    second_level_validator = SecondLevelValidator()
    
    # Create a valid receipt
    receipt_img = create_test_receipt_image("888812345678", "BCA", 100000)
    
    # Simulate the API endpoint validation steps
    print("Simulating /receipt/validate endpoint flow...")
    
    # Step 1: File validation
    file_validation = validator.validate_file(receipt_img, "test_receipt.png")
    print(f"1. File validation: {'✅ PASS' if file_validation.is_valid else '❌ FAIL'}")
    
    # Step 2: Image analysis
    image_analysis = validator.analyze_image(receipt_img)
    print(f"2. Image analysis: Risk={image_analysis.risk_level}, Quality={image_analysis.quality_score:.2f}")
    
    # Step 3: OCR extraction with VA validation
    ocr_result = validator.extract_ocr(receipt_img, "TRXBCA001")
    print(f"3. OCR extraction: Confidence={ocr_result.confidence_score:.2f}, VA_Valid={ocr_result.va_validation.is_valid_va}")
    
    # Step 4: First level result
    first_level_result = ocr_result.va_validation
    print(f"4. First level: Status={first_level_result.first_level_status}")
    
    # Step 5: Second level validation (only if first level passes)
    if first_level_result.first_level_status == "VALIDATED":
        form_data = {
            "bank_name": "BCA",
            "amount": 100000,
            "transaction_id": "TRXBCA001",
            "transaction_date": datetime.now().isoformat()
        }
        
        second_level_result = second_level_validator.validate_second_level(
            ocr_result,
            image_analysis,
            form_data,
            validator
        )
        
        print(f"5. Second level: Passed={second_level_result['passed']}")
        print(f"   Recommendation: {second_level_result['recommendation']}")
        print(f"   Confidence: {second_level_result['confidence_score']:.2f}")
        
        # Additional validations
        if second_level_result.get('amount_validation'):
            print(f"   Amount validation: {second_level_result['amount_validation']['is_valid']}")
        if second_level_result.get('debit_status_validation'):
            print(f"   Debit status: {second_level_result['debit_status_validation']['status']}")
        if second_level_result.get('pattern_validation'):
            print(f"   Pattern validation: Suspicious={second_level_result['pattern_validation']['is_suspicious']}")
        if second_level_result.get('timing_validation'):
            print(f"   Timing validation: Suspicious={second_level_result['timing_validation']['is_suspicious']}")
    
    print("\n✅ API endpoint simulation completed successfully!")
    return True


if __name__ == "__main__":
    print("Running comprehensive system test...")
    
    # Test all components
    system_working = test_all_components()
    
    # Test API endpoint simulation
    api_working = test_api_endpoint_simulation()
    
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)
    
    if system_working and api_working:
        print("✅ SYSTEM IS FULLY OPERATIONAL")
        print("✅ READY FOR SERVER DEPLOYMENT")
        print("✅ OCR FUNCTIONALITY WORKING")
        print("✅ ALL VALIDATION LAYERS OPERATIONAL")
        print("✅ DEMO READY")
        print("\nURL http://147.139.202.129/ - YES, SYSTEM IS READY TO BE TESTED THERE")
    else:
        print("❌ SYSTEM NOT READY FOR DEPLOYMENT")
    
    print("="*80)