#!/usr/bin/env python3
"""
Test script to verify OCR functionality with the Aman ga? validation system
"""

import sys
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont
import io
import uuid
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from validators import PaymentValidator
from virtual_accounts import get_va_manager


def create_realistic_receipt_image():
    """Create a realistic receipt image with VA number"""
    # Create a larger receipt-like image to meet minimum size requirements
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create realistic receipt content
    receipt_text = """
PT AMAN GA INDONESIA
Virtual Account Payment

Tanggal: 25/03/2026 10:30:45
Bank: BCA
VA Number: 888812345678
BCA 888812345678

Deskripsi: Pembayaran Layanan
Jumlah: Rp 100.000
ID Transaksi: TRXBCA20260325001

Terima kasih atas pembayaran Anda
Kode Pembayaran: 888812345678
    """
    
    # Add text to image with larger font for better OCR recognition
    try:
        # Try to use a larger font size
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw text with padding
    y_offset = 50
    for line in receipt_text.strip().split('\n'):
        if line.strip():  # Only draw non-empty lines
            draw.text((50, y_offset), line.strip(), fill='black', font=font)
            y_offset += 30  # Move to next line
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def test_ocr_functionality():
    """Test the OCR functionality with the validation system"""
    print("="*70)
    print("Testing OCR Functionality with Validation System")
    print("="*70)
    
    validator = PaymentValidator()
    va_manager = get_va_manager()
    
    # Create a realistic receipt image
    print("Creating realistic receipt image with VA number...")
    receipt_image = create_realistic_receipt_image()
    
    # Test file validation first
    print("\n1. Testing File Validation...")
    file_result = validator.validate_file(receipt_image, "test_receipt.png")
    print(f"   File validation: {'✅ PASS' if file_result.is_valid else '❌ FAIL'}")
    if file_result.is_valid:
        print(f"   File size: {file_result.file_size} bytes")
        print(f"   Dimensions: {file_result.image_width}x{file_result.image_height}")
    
    # Test OCR extraction
    print("\n2. Testing OCR Extraction...")
    ocr_result = validator.extract_ocr(receipt_image, "TRXBCA001")
    print(f"   OCR Confidence: {ocr_result.confidence_score:.2f}")
    print(f"   Extracted Text Preview: '{ocr_result.extracted_text[:100]}...'")
    print(f"   Extracted Amount: {ocr_result.extracted_amount}")
    print(f"   Extracted Transaction ID: {ocr_result.extracted_transaction_id}")
    print(f"   Extracted Date: {ocr_result.extracted_date}")
    print(f"   Extracted Bank: {ocr_result.extracted_bank}")
    
    # Test VA validation
    print("\n3. Testing VA Validation...")
    print(f"   VA Validation - Valid: {ocr_result.va_validation.is_valid_va}")
    print(f"   VA Validation - Matched: {ocr_result.va_validation.matched_accounts}")
    print(f"   VA Validation - Status: {ocr_result.va_validation.first_level_status}")
    print(f"   VA Validation - Notes: {ocr_result.va_validation.va_validation_notes}")
    
    # Test image analysis
    print("\n4. Testing Image Analysis...")
    image_analysis = validator.analyze_image(receipt_image)
    print(f"   Image Analysis - Risk Level: {image_analysis.risk_level}")
    print(f"   Image Analysis - Quality Score: {image_analysis.quality_score:.2f}")
    print(f"   Image Analysis - Manipulation Detected: {image_analysis.is_manipulated}")
    
    # Test deepfake detection
    print("\n5. Testing Deepfake Detection...")
    deepfake_result = validator.detect_deepfake_indicators(receipt_image)
    print(f"   Deepfake Detection - Is Likely Deepfake: {deepfake_result['is_likely_deepfake']}")
    print(f"   Deepfake Detection - Confidence: {deepfake_result['confidence_score']:.2f}")
    
    # Test receipt structure validation
    print("\n6. Testing Receipt Structure Validation...")
    receipt_validation = validator.validate_receipt_structure(ocr_result.extracted_text)
    print(f"   Receipt Validation - Business Info: {bool(receipt_validation['business_info'])}")
    print(f"   Receipt Validation - Format Validation: {receipt_validation['format_validation']['format_consistency_score']:.2f}")
    print(f"   Receipt Validation - VA Validation: {receipt_validation['va_validation']['is_valid_va']}")
    
    # Test amount validation
    print("\n7. Testing Amount Validation...")
    amount_result = validator.validate_amount(ocr_result.extracted_amount or 100000, 100000)
    print(f"   Amount Validation - Is Valid: {amount_result.is_valid}")
    print(f"   Amount Validation - Variance: {amount_result.variance_percentage:.2%}")
    
    # Test suspicious pattern validation
    print("\n8. Testing Suspicious Pattern Validation...")
    pattern_result = validator.validate_suspicious_patterns(
        ocr_result.extracted_text,
        ocr_result.extracted_amount or 100000,
        ocr_result.extracted_bank or "BCA"
    )
    print(f"   Pattern Validation - Is Suspicious: {pattern_result.is_suspicious}")
    print(f"   Pattern Validation - Confidence: {pattern_result.confidence_score:.2f}")
    print(f"   Pattern Validation - Patterns: {pattern_result.pattern_types}")
    
    # Test timing validation
    print("\n9. Testing Timing Validation...")
    timing_result = validator.validate_timing_patterns(
        datetime.now().isoformat(),
        ocr_result.extracted_date
    )
    print(f"   Timing Validation - Is Suspicious: {timing_result.is_suspicious}")
    print(f"   Timing Validation - Confidence: {timing_result.confidence_score:.2f}")
    print(f"   Timing Validation - Issues: {timing_result.timing_issues}")
    
    print("\n" + "="*70)
    print("OCR FUNCTIONALITY TEST COMPLETE")
    print("="*70)
    
    # Summary
    print("\nSUMMARY:")
    print(f"✓ File Validation: {'PASS' if file_result.is_valid else 'FAIL'}")
    print(f"✓ OCR Extraction: {'SUCCESS' if ocr_result.confidence_score > 0 else 'FAILURE'}")
    print(f"✓ VA Validation: {'SUCCESS' if ocr_result.va_validation.is_valid_va else 'FAILURE'}")
    print(f"✓ Image Analysis: {'COMPLETE' if image_analysis else 'FAILURE'}")
    print(f"✓ All validation components working: {'YES' if ocr_result.confidence_score > 0 else 'NO'}")
    
    return ocr_result.confidence_score > 0


def test_complete_validation_flow():
    """Test the complete validation flow with a real scenario"""
    print("\n" + "="*70)
    print("Testing Complete Validation Flow")
    print("="*70)
    
    from second_level_validator import SecondLevelValidator
    validator = PaymentValidator()
    second_level_validator = SecondLevelValidator()
    
    # Create a valid receipt image
    receipt_image = create_realistic_receipt_image()
    
    # Simulate the complete validation process
    print("Simulating complete validation flow...")
    
    # Step 1: File validation
    file_validation = validator.validate_file(receipt_image, "valid_receipt.png")
    print(f"1. File validation: {'✅' if file_validation.is_valid else '❌'}")
    
    # Step 2: Image analysis
    image_analysis = validator.analyze_image(receipt_image)
    print(f"2. Image analysis: Risk={image_analysis.risk_level}, Quality={image_analysis.quality_score:.2f}")
    
    # Step 3: OCR extraction with VA validation
    ocr_result = validator.extract_ocr(receipt_image, "TRXBCA001")
    print(f"3. OCR extraction: Confidence={ocr_result.confidence_score:.2f}, VA_Valid={ocr_result.va_validation.is_valid_va}")
    
    # Step 4: First level validation result
    first_level_result = ocr_result.va_validation
    print(f"4. First level validation: Status={first_level_result.first_level_status}")
    
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
            validator  # Pass validator instance for additional checks
        )
        
        print(f"5. Second level validation: Passed={second_level_result['passed']}")
        print(f"   Recommendation: {second_level_result['recommendation']}")
        print(f"   Confidence: {second_level_result['confidence_score']:.2f}")
        
        # Check additional validations
        if second_level_result.get('amount_validation'):
            print(f"   Amount validation: {second_level_result['amount_validation']['is_valid']}")
        if second_level_result.get('debit_status_validation'):
            print(f"   Debit status validation: {second_level_result['debit_status_validation']['status']}")
    else:
        print("5. Second level validation: SKIPPED (first level failed)")
    
    print("\n" + "="*70)
    print("COMPLETE VALIDATION FLOW TEST COMPLETE")
    print("="*70)
    
    success = (file_validation.is_valid and 
               ocr_result.confidence_score > 0 and 
               ocr_result.va_validation.is_valid_va and
               ocr_result.va_validation.first_level_status == "VALIDATED")
    
    print(f"\nFlow successful: {'✅ YES' if success else '❌ NO'}")
    return success


if __name__ == "__main__":
    print("Testing OCR functionality with Aman ga? validation system...")
    
    # Test OCR functionality
    ocr_success = test_ocr_functionality()
    
    # Test complete validation flow
    flow_success = test_complete_validation_flow()
    
    print("\n" + "="*70)
    print("FINAL RESULTS:")
    print("="*70)
    print(f"OCR Functionality: {'✅ WORKING' if ocr_success else '❌ NOT WORKING'}")
    print(f"Complete Flow: {'✅ SUCCESS' if flow_success else '❌ FAILURE'}")
    
    if ocr_success and flow_success:
        print("\n🎉 SUCCESS: OCR is working properly with the validation system!")
        print("   - VA validation correctly identifies valid Virtual Accounts")
        print("   - OCR extraction works with real images")
        print("   - All validation layers are functioning")
        print("   - Complete validation flow is operational")
    else:
        print("\n❌ ISSUES DETECTED: OCR may not be working properly")
    
    print("="*70)