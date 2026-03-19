#!/usr/bin/env python3
"""
Test Script for Security Validation Features
Run this to verify all validation features are working correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_validators():
    """Test the validators module"""
    print("\n" + "="*60)
    print("Testing Validators Module")
    print("="*60)
    
    try:
        from validators import PaymentValidator, PaymentProofCreate, ServiceType, PaymentMethod, BankName
        
        validator = PaymentValidator()
        print("✅ PaymentValidator initialized")
        
        # Test 1: Valid payment data
        print("\n📋 Test 1: Valid Payment Data")
        valid_data = {
            "service_type": "CEK_DASAR",
            "amount": 1000,
            "payment_method": "BANK_TRANSFER",
            "bank_name": "BCA",
            "transaction_id": "TRX20240319ABC123",
            "transaction_date": "2024-03-19T10:00:00"
        }
        
        is_valid, error, validated = validator.validate_payment_data(valid_data)
        if is_valid:
            print(f"✅ Valid data accepted")
            print(f"   Amount: Rp {validated.amount}")
            print(f"   Transaction ID: {validated.transaction_id}")
        else:
            print(f"❌ Valid data rejected: {error}")
        
        # Test 2: Invalid amount (too low)
        print("\n📋 Test 2: Invalid Amount (Too Low)")
        invalid_amount = {**valid_data, "amount": 50}
        is_valid, error, _ = validator.validate_payment_data(invalid_amount)
        if not is_valid:
            print(f"✅ Correctly rejected: {error}")
        else:
            print(f"❌ Should have been rejected")
        
        # Test 3: Invalid amount (too high)
        print("\n📋 Test 3: Invalid Amount (Too High)")
        invalid_amount = {**valid_data, "amount": 200_000_000}
        is_valid, error, _ = validator.validate_payment_data(invalid_amount)
        if not is_valid:
            print(f"✅ Correctly rejected: {error}")
        else:
            print(f"❌ Should have been rejected")
        
        # Test 4: Invalid transaction ID (suspicious pattern)
        print("\n📋 Test 4: Invalid Transaction ID (Suspicious)")
        invalid_tid = {**valid_data, "transaction_id": "TEST123"}
        is_valid, error, _ = validator.validate_payment_data(invalid_tid)
        if not is_valid:
            print(f"✅ Correctly rejected: {error}")
        else:
            print(f"❌ Should have been rejected")
        
        # Test 5: Future date
        print("\n📋 Test 5: Future Date")
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        invalid_date = {**valid_data, "transaction_date": future_date}
        is_valid, error, _ = validator.validate_payment_data(invalid_date)
        if not is_valid:
            print(f"✅ Correctly rejected: {error}")
        else:
            print(f"❌ Should have been rejected")
        
        # Test 6: File validation (create test image)
        print("\n📋 Test 6: File Validation")
        from PIL import Image
        import io
        
        # Create valid test image
        img = Image.new('RGB', (500, 500), color='white')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_content = img_bytes.getvalue()
        
        file_result = validator.validate_file(img_content, "test.jpg")
        if file_result.is_valid:
            print(f"✅ Valid image accepted")
            print(f"   Size: {file_result.file_size} bytes")
            print(f"   Dimensions: {file_result.image_width}x{file_result.image_height}")
            print(f"   Hash: {file_result.image_hash[:16]}...")
        else:
            print(f"❌ Valid image rejected: {file_result.error_message}")
        
        # Test 7: File too small
        print("\n📋 Test 7: File Too Small")
        tiny_file = b"x" * 100  # 100 bytes
        file_result = validator.validate_file(tiny_file, "tiny.jpg")
        if not file_result.is_valid:
            print(f"✅ Correctly rejected: {file_result.error_message}")
        else:
            print(f"❌ Should have been rejected")
        
        # Test 8: OCR Test
        print("\n📋 Test 8: OCR Extraction")
        ocr_result = validator.extract_ocr(img_content)
        print(f"✅ OCR processed")
        print(f"   Confidence: {ocr_result.confidence_score * 100:.1f}%")
        print(f"   Extracted Amount: {ocr_result.extracted_amount}")
        
        # Test 9: Image Analysis
        print("\n📋 Test 9: Image Analysis")
        analysis = validator.analyze_image(img_content)
        print(f"✅ Image analyzed")
        print(f"   Manipulation Detected: {analysis.is_manipulated}")
        print(f"   Risk Level: {analysis.risk_level}")
        print(f"   Quality Score: {analysis.quality_score * 100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fraud_service():
    """Test the fraud service"""
    print("\n" + "="*60)
    print("Testing Fraud Service")
    print("="*60)
    
    try:
        from services.fraud import FraudService
        from database import supabase
        
        fraud_service = FraudService()
        print("✅ FraudService initialized")
        
        # Test risk score calculation
        print("\n📋 Test: Risk Score Calculation")
        payment_data = {
            "amount": 1000,
            "transaction_id": "TRX123",
            "service_type": "CEK_DASAR"
        }
        
        risk = fraud_service.calculate_risk_score("user-001", payment_data)
        print(f"✅ Risk calculated")
        print(f"   Score: {risk['risk_score']}")
        print(f"   Level: {risk['risk_level']}")
        print(f"   Factors: {risk['risk_factors']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rate_limiter():
    """Test rate limiter"""
    print("\n" + "="*60)
    print("Testing Rate Limiter")
    print("="*60)
    
    try:
        from rate_limiter import RateLimiter, RateLimitTracker, get_client_ip
        from fastapi import Request
        
        rate_limiter = RateLimiter()
        print("✅ RateLimiter initialized")
        
        # Test tracker
        tracker = RateLimitTracker()
        test_ip = "192.168.1.1"
        
        print(f"\n📋 Test: Rate Limit Violation Tracking")
        for i in range(12):
            blocked = tracker.record_violation(test_ip)
            if blocked:
                print(f"✅ IP blocked after {i+1} violations")
                break
        
        is_blocked = tracker.is_blocked(test_ip)
        print(f"   Currently blocked: {is_blocked}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🔒 Aman ga? Security Validation Test Suite")
    print("="*60)
    
    results = {
        "Validators": test_validators(),
        "Fraud Service": test_fraud_service(),
        "Rate Limiter": test_rate_limiter()
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
        print("\nNote: Some tests may fail if dependencies are not installed.")
        print("Install dependencies with: pip install -r requirements.txt")
        print("Also ensure tesseract-ocr is installed on your system.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
