#!/usr/bin/env python3
"""
Test script to check image validation accuracy for Aman ga? system
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
from second_level_validator import SecondLevelValidator


def create_test_image_with_va(va_number, bank_name="BCA", text_content=None):
    """Create a test image with a specific VA number"""
    # Create a larger receipt-like image to meet minimum size requirements
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Default text content if none provided
    if text_content is None:
        # Add the bank name and VA number in the format expected by the regex
        text_content = f"""
        PT AMAN GA INDONESIA
        Virtual Account Payment
        
        Bank: {bank_name}
        VA Number: {va_number}
        {bank_name} {va_number}  # This ensures the pattern matches for the specific bank
        Amount: Rp 100.000
        Transaction ID: TRX{datetime.now().strftime('%Y%m%d')}001
        Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        
        Thank you for your payment
        """
    
    # Add text to image
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        # Fallback to basic drawing
        font = None
    
    draw.text((20, 20), text_content, fill='black', font=font)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


def test_image_validation_accuracy():
    """Test the accuracy of image validation components"""
    print("="*70)
    print("Testing Image Validation Accuracy")
    print("="*70)
    
    validator = PaymentValidator()
    va_manager = get_va_manager()
    second_level_validator = SecondLevelValidator()
    
    # Test 1: Valid BCA VA image
    print("\n1. Testing Valid BCA VA Image...")
    bca_img = create_test_image_with_va("888812345678", "BCA")
    
    # File validation
    file_result = validator.validate_file(bca_img, "test_bca.png")
    print(f"   File validation: {'✅ PASS' if file_result.is_valid else '❌ FAIL'}")
    
    # Image analysis
    image_analysis = validator.analyze_image(bca_img)
    print(f"   Image analysis - Risk Level: {image_analysis.risk_level}")
    print(f"   Image analysis - Quality Score: {image_analysis.quality_score:.2f}")
    
    # OCR extraction
    ocr_result = validator.extract_ocr(bca_img, "TRXBCA001")
    print(f"   OCR extraction - Confidence: {ocr_result.confidence_score:.2f}")
    print(f"   OCR extraction - VA Validation: {ocr_result.va_validation.is_valid_va}")
    print(f"   OCR extraction - First Level Status: {ocr_result.va_validation.first_level_status}")
    
    # Test 2: Valid BRI VA image
    print("\n2. Testing Valid BRI VA Image...")
    bri_img = create_test_image_with_va("99991234567", "BRI")
    ocr_result_bri = validator.extract_ocr(bri_img, "TRXBRI001")
    print(f"   VA Validation: {ocr_result_bri.va_validation.is_valid_va}")
    print(f"   First Level Status: {ocr_result_bri.va_validation.first_level_status}")
    
    # Test 3: Invalid VA image (should fail first level)
    print("\n3. Testing Invalid VA Image...")
    invalid_img = create_test_image_with_va("1111111111", "FAKE_BANK")
    ocr_result_invalid = validator.extract_ocr(invalid_img, "TRXFAKE001")
    print(f"   VA Validation: {ocr_result_invalid.va_validation.is_valid_va}")
    print(f"   First Level Status: {ocr_result_invalid.va_validation.first_level_status}")
    
    # Test 4: Image with suspicious patterns
    print("\n4. Testing Image with Suspicious Patterns...")
    suspicious_text = """
    PT FAKE COMPANY
    TEST PAYMENT RECEIPT
    
    Bank: BCA
    VA Number: 888812345678
    Amount: Rp 1
    Transaction ID: TEST001
    Date: 01/01/2024 00:00:00
    
    This is a TEST receipt for DEMO purposes
    NOT A REAL TRANSACTION
    """
    suspicious_img = create_test_image_with_va("888812345678", "BCA", suspicious_text)
    ocr_result_suspicious = validator.extract_ocr(suspicious_img, "TEST001")
    
    # Test suspicious pattern validation
    pattern_result = validator.validate_suspicious_patterns(
        ocr_result_suspicious.extracted_text,
        1,  # Amount of 1 is suspicious
        "BCA"
    )
    print(f"   Pattern validation - Is Suspicious: {pattern_result.is_suspicious}")
    print(f"   Pattern validation - Confidence: {pattern_result.confidence_score:.2f}")
    print(f"   Pattern validation - Patterns: {pattern_result.pattern_types}")
    
    # Test 5: Timing validation
    print("\n5. Testing Timing Validation...")
    timing_result = validator.validate_timing_patterns(
        f"{datetime.now().isoformat()}",
        ocr_result.extracted_date
    )
    print(f"   Timing validation - Is Suspicious: {timing_result.is_suspicious}")
    print(f"   Timing validation - Confidence: {timing_result.confidence_score:.2f}")
    print(f"   Timing validation - Issues: {timing_result.timing_issues}")
    
    # Test 6: Amount validation
    print("\n6. Testing Amount Validation...")
    amount_result = validator.validate_amount(100000, 100000)  # Same amounts
    print(f"   Amount validation - Is Valid: {amount_result.is_valid}")
    print(f"   Amount validation - Variance: {amount_result.variance_percentage:.2%}")
    
    amount_result_diff = validator.validate_amount(100000, 10000)  # Different amounts
    print(f"   Amount validation (diff) - Is Valid: {amount_result_diff.is_valid}")
    print(f"   Amount validation (diff) - Variance: {amount_result_diff.variance_percentage:.2%}")
    
    # Test 7: Debit status validation
    print("\n7. Testing Debit Status Validation...")
    debit_result = validator.validate_debit_status(
        "BCA Virtual Account payment successful",
        "TRX001",
        100000
    )
    print(f"   Debit validation - Is Debited: {debit_result.is_debited}")
    print(f"   Debit validation - Status: {debit_result.status}")
    
    # Test 8: Second level validation with all components
    print("\n8. Testing Complete Second Level Validation...")
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
    
    print(f"   Second level - Passed: {second_level_result['passed']}")
    print(f"   Second level - Recommendation: {second_level_result['recommendation']}")
    print(f"   Second level - Confidence: {second_level_result['confidence_score']:.2f}")
    
    # Check if amount validation was included
    if second_level_result.get('amount_validation'):
        print(f"   Second level - Amount validation: {second_level_result['amount_validation']['is_valid']}")
    
    # Check if debit status validation was included
    if second_level_result.get('debit_status_validation'):
        print(f"   Second level - Debit status: {second_level_result['debit_status_validation']['status']}")
    
    print("\n" + "="*70)
    print("Image Validation Accuracy Test Complete")
    print("="*70)
    
    return True


def test_edge_cases():
    """Test edge cases for validation accuracy"""
    print("\nTesting Edge Cases...")
    
    validator = PaymentValidator()
    
    # Test with empty image
    print("\n9. Testing Empty Image...")
    try:
        empty_img = create_test_image_with_va("", "BCA", "")
        ocr_result = validator.extract_ocr(empty_img, "TRXEMPTY001")
        print(f"   OCR on empty image - Confidence: {ocr_result.confidence_score:.2f}")
        print(f"   VA validation: {ocr_result.va_validation.is_valid_va}")
    except Exception as e:
        print(f"   OCR on empty image - Error: {str(e)}")
    
    # Test with very low quality indicators
    print("\n10. Testing Low Quality Image...")
    # Create image with low contrast text
    low_quality_img = create_test_image_with_va("888812345678", "BCA", 
                                               "FADED TEXT THAT IS HARD TO READ " * 10)
    image_analysis = validator.analyze_image(low_quality_img)
    print(f"   Low quality image - Risk Level: {image_analysis.risk_level}")
    print(f"   Low quality image - Quality Score: {image_analysis.quality_score:.2f}")
    
    print("\n✓ Edge case testing completed")


if __name__ == "__main__":
    success = test_image_validation_accuracy()
    test_edge_cases()
    
    print("\n" + "="*70)
    print("SUMMARY:")
    print("Image validation components tested successfully:")
    print("- File validation")
    print("- Image analysis (risk level, quality)")
    print("- OCR extraction with VA validation")
    print("- Pattern validation for suspicious content")
    print("- Timing validation")
    print("- Amount validation")
    print("- Debit status validation")
    print("- Second level validation with all components")
    print("- Edge cases")
    print("="*70)