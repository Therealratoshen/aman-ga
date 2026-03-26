from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from database import supabase, is_mock_mode
from auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from services.payment import PaymentService
from services.fraud import FraudService
from services.notification import NotificationService
from models import UserCreate, PaymentProofCreate
from validators import PaymentValidator, FileValidationResult, OCRResult, ImageAnalysisResult
from rate_limiter import RateLimiter, upload_limit, get_client_ip, check_ip_blocked
from ocr_learning import SelfLearningOCR, UserFeedback, LearningMetrics
from feedback_models import UserFeedbackCreate, OCRUncertaintyReport, LearningMetricsResponse, ReceiptFormatInfo
from admin_api import router as admin_router
from second_level_validator import SecondLevelValidator
from datetime import datetime, timedelta
from typing import Optional, List
import aiofiles
import os
from uuid import uuid4
import base64

app = FastAPI(title="Aman ga? API", version="2.1.1", description="Receipt OCR Validation System with Deepfake Detection")

# Initialize rate limiter
rate_limiter = RateLimiter()
rate_limiter.setup_app(app)

# Initialize self-learning OCR
self_learning_ocr = SelfLearningOCR()

# Start automatic learning system
try:
    from automatic_learning import start_automatic_learning
    start_automatic_learning()
    print("✅ Automatic learning system started")
except Exception as e:
    print(f"⚠️ Failed to start automatic learning system: {e}")

# CORS - Hardened configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://147.139.202.129",
        # Add production domains here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Initialize services
payment_service = PaymentService()
fraud_service = FraudService()
notification_service = NotificationService()
validator = PaymentValidator()
second_level_validator = SecondLevelValidator()

# Include admin API routes
app.include_router(admin_router)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# ============ AUTH ENDPOINTS ============

@app.post("/register", tags=["Authentication"])
async def register(user: UserCreate, request: Request):
    """Register a new user account"""

    # Check if IP is blocked
    client_ip = get_client_ip(request)
    if check_ip_blocked(client_ip):
        raise HTTPException(status_code=429, detail="Too many attempts. Please try again later.")

    # Check if user exists
    existing = supabase.table("users").select("*").eq("email", user.email).execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate email format
    if not user.email or "@" not in user.email or "." not in user.email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    # Validate password strength
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(c.isupper() for c in user.password) or not any(c.isdigit() for c in user.password):
        raise HTTPException(status_code=400, detail="Password must contain uppercase letter and number")

    # Create user
    user_data = {
        "email": user.email,
        "password_hash": get_password_hash(user.password),
        "full_name": user.full_name,
        "phone": user.phone,
        "role": "USER",
        "status": "ACTIVE"
    }

    result = supabase.table("users").insert(user_data).execute()

    return {"success": True, "user_id": result.data[0]["id"], "message": "Registration successful"}

@app.post("/token", tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    """Login and get access token"""

    # Check if IP is blocked
    if request:
        client_ip = get_client_ip(request)
        if check_ip_blocked(client_ip):
            raise HTTPException(status_code=429, detail="Too many attempts. Please try again later.")

    user = supabase.table("users").select("*").eq("email", form_data.username).execute()

    if not user.data:
        # Record failed attempt for rate limiting
        if request:
            from rate_limiter import rate_limit_tracker
            rate_limit_tracker.record_violation(client_ip)
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not verify_password(form_data.password, user.data[0]["password_hash"]):
        # Record failed attempt
        if request:
            from rate_limiter import rate_limit_tracker
            rate_limit_tracker.record_violation(client_ip)
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if user.data[0]["status"] != "ACTIVE":
        raise HTTPException(status_code=400, detail="Account is suspended or banned")

    access_token = create_access_token(
        data={"sub": user.data[0]["email"], "user_id": user.data[0]["id"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.data[0]["email"],
            "role": user.data[0]["role"],
            "user_id": user.data[0]["id"]
        }
    }

@app.get("/me", tags=["Authentication"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user

# ============ RECEIPT VALIDATION ENDPOINTS ============

@app.post("/receipt/validate", tags=["Receipt Validation"])
async def validate_receipt(
    bank_name: str,
    transaction_id: str,
    transaction_date: str,
    amount: int,
    proof_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """
    Validate a receipt for authenticity and deepfake detection

    Validates receipt authenticity with comprehensive analysis:
    - First level: Virtual Account validation
    - Second level: Comprehensive receipt validation
    - OCR extraction and validation
    - Image manipulation detection
    - Deepfake detection
    - Authenticity scoring
    """

    # Check if IP is blocked
    if request:
        client_ip = get_client_ip(request)
        if check_ip_blocked(client_ip):
            raise HTTPException(status_code=429, detail="Too many attempts. Please try again later.")

    # Read file content
    try:
        file_content = await proof_image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Step 1: Validate file
    file_validation = validator.validate_file(file_content, proof_image.filename)
    if not file_validation.is_valid:
        raise HTTPException(status_code=400, detail=file_validation.error_message)

    # Step 2: Analyze image for manipulation (deepfake detection)
    image_analysis = validator.analyze_image(file_content)

    # Step 3: Extract OCR data (includes VA validation)
    ocr_result = validator.extract_ocr(file_content, transaction_id)

    # Step 4: Analyze receipt authenticity based on user feedback patterns
    extracted_data = {
        "bank_name": bank_name,
        "amount": amount,
        "transaction_id": transaction_id,
        "transaction_date": transaction_date
    }

    authenticity_result = self_learning_ocr.analyze_authenticity(
        "",  # payment_id not created yet
        extracted_data,
        current_user["id"]
    )

    # Step 5: Deepfake detection analysis
    deepfake_indicators = validator.detect_deepfake_indicators(file_content)

    # Step 6: Receipt structure validation (includes VA validation)
    receipt_validation = validator.validate_receipt_structure(ocr_result.extracted_text)

    # Step 7: Two-level validation
    # First level: VA validation (already performed in OCR extraction)
    first_level_result = ocr_result.va_validation
    
    # Calculate fraud risk score using the enhanced method
    fraud_result = fraud_service.calculate_risk_score(
        current_user["id"],
        {
            "amount": amount,
            "payment_method": "BANK_TRANSFER",  # Default for this endpoint
            "bank_name": bank_name,
            "transaction_id": transaction_id,
            "transaction_date": transaction_date,
            "proof_image_hash": file_validation.image_hash if file_validation.is_valid else None
        },
        image_analysis.__dict__ if image_analysis else None,
        ocr_result.__dict__ if ocr_result else None,
        None,  # authenticity_result - not calculated here
        validator  # Pass validator instance for additional checks
    )

    # Second level: Comprehensive validation if first level passed
    second_level_result = None
    if first_level_result and first_level_result.first_level_status == "VALIDATED":
        form_data = {
            "bank_name": bank_name,
            "amount": amount,
            "transaction_id": transaction_id,
            "transaction_date": transaction_date
        }
        second_level_result = second_level_validator.validate_second_level(
            ocr_result, 
            image_analysis, 
            form_data,
            validator  # Pass validator instance for additional checks
        )
    else:
        # If first level failed, skip second level and return early
        response = {
            "success": False,
            "validation_status": "REJECTED_AT_FIRST_LEVEL",
            "first_level_validation": {
                "is_valid_va": first_level_result.is_valid_va if first_level_result else False,
                "matched_accounts": first_level_result.matched_accounts if first_level_result else [],
                "first_level_status": first_level_result.first_level_status if first_level_result else "REJECTED",
                "notes": "Receipt does not match any of the authorized Virtual Accounts"
            },
            "fraud_detection": fraud_result,  # Include fraud detection results
            "message": "Receipt validation failed at first level - does not match any authorized Virtual Account"
        }
        return response

    # Build comprehensive response with two-level validation results
    response = {
        "success": True,
        "validation_status": "COMPLETED",
        "first_level_validation": {
            "is_valid_va": first_level_result.is_valid_va if first_level_result else False,
            "matched_accounts": first_level_result.matched_accounts if first_level_result else [],
            "matched_details": first_level_result.matched_details if first_level_result else [],
            "first_level_status": first_level_result.first_level_status if first_level_result else "PENDING",
            "va_validation_notes": first_level_result.va_validation_notes if first_level_result else None,
            "transaction_validation": first_level_result.transaction_validation if first_level_result else None
        },
        "second_level_validation": second_level_result,
        "fraud_detection": fraud_result,  # Include comprehensive fraud detection results
        "validation": {
            "file_valid": True,
            "file_size": file_validation.file_size,
            "image_dimensions": f"{file_validation.image_width}x{file_validation.image_height}",
            "image_hash": file_validation.image_hash[:16] + "..." if file_validation.image_hash else None,
        },
        "ocr": {
            "extracted_amount": ocr_result.extracted_amount,
            "extracted_transaction_id": ocr_result.extracted_transaction_id,
            "confidence": round(ocr_result.confidence_score * 100, 1),
            "matches_form": ocr_result.matches_form,
            "mismatches": ocr_result.mismatches if not ocr_result.matches_form else [],
            "va_validation": {
                "is_valid_va": ocr_result.va_validation.is_valid_va if ocr_result.va_validation else False,
                "matched_accounts": ocr_result.va_validation.matched_accounts if ocr_result.va_validation else [],
                "first_level_status": ocr_result.va_validation.first_level_status if ocr_result.va_validation else "PENDING",
                "transaction_validation": ocr_result.va_validation.transaction_validation if ocr_result.va_validation else None
            }
        },
        "image_analysis": {
            "manipulation_detected": image_analysis.is_manipulated,
            "risk_level": image_analysis.risk_level,
            "quality_score": round(image_analysis.quality_score * 100, 1),
            "indicators": image_analysis.manipulation_indicators
        },
        "receipt_validation": {
            "business_info": receipt_validation["business_info"],
            "items_and_totals": receipt_validation["items_and_totals"],
            "format_validation": {
                "has_header": receipt_validation["format_validation"]["has_header"],
                "has_items": receipt_validation["format_validation"]["has_items"],
                "has_totals": receipt_validation["format_validation"]["has_totals"],
                "has_footer": receipt_validation["format_validation"]["has_footer"],
                "format_consistency_score": round(receipt_validation["format_validation"]["format_consistency_score"] * 100, 1)
            },
            "logical_consistency_score": round(receipt_validation["logical_consistency"] * 100, 1),
            "overall_receipt_validity": round(receipt_validation["overall_receipt_validity"] * 100, 1),
            "va_validation": receipt_validation["va_validation"]  # Include VA validation in receipt validation
        },
        "amount_validation": second_level_result.get("amount_validation") if second_level_result else None,
        "debit_status_validation": second_level_result.get("debit_status_validation") if second_level_result else None,
        "frequency_validation": fraud_result.get("frequency_validation") if fraud_result else None,
        "pattern_validation": fraud_result.get("pattern_validation") if fraud_result else None,
        "timing_validation": fraud_result.get("timing_validation") if fraud_result else None,
        "deepfake_analysis": {
            "is_likely_deepfake": deepfake_indicators["is_likely_deepfake"],
            "confidence_score": deepfake_indicators["confidence_score"],
            "indicators": deepfake_indicators["indicators"],
            "recommendation": deepfake_indicators["recommendation"]
        },
        "authenticity_assessment": {
            "authenticity_score": round(authenticity_result["authenticity_score"] * 100, 1),
            "is_likely_authentic": authenticity_result["is_likely_authentic"],
            "confidence_level": authenticity_result["confidence_level"],
            "breakdown": authenticity_result["breakdown"],
            "recommendation": authenticity_result["recommendation"]
        }
    }

    return response


# Simplified payment endpoints that work without DB
@app.get("/payment/credits", tags=["Payment"])
async def get_my_credits(current_user: dict = Depends(get_current_user)):
    """Get current user's active service credits - simplified for mock mode"""
    
    # If using mock mode, return unlimited credits
    if is_mock_mode():
        return [
            {
                "id": "mock-credit-1",
                "service_type": "CEK_DASAR",
                "quantity": 999,
                "used_quantity": 0,
                "status": "ACTIVE",
                "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
            },
            {
                "id": "mock-credit-2", 
                "service_type": "CEK_DEEP",
                "quantity": 999,
                "used_quantity": 0,
                "status": "ACTIVE",
                "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
            },
            {
                "id": "mock-credit-3",
                "service_type": "CEK_PLUS",
                "quantity": 999,
                "used_quantity": 0,
                "status": "ACTIVE",
                "expires_at": (datetime.now() + timedelta(days=365)).isoformat()
            }
        ]
    else:
        # For real DB mode, use the original service
        credits = payment_service.get_user_credits(current_user["id"])
        return credits

# ============ FEEDBACK & LEARNING ENDPOINTS ============

@app.post("/feedback/submit", tags=["Feedback"])
async def submit_feedback(
    feedback_data: UserFeedbackCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit feedback on OCR extraction results.

    This helps the system learn and improve accuracy over time.
    Every correction makes the system smarter!
    """

    # Create feedback record
    feedback = UserFeedback(
        feedback_id=feedback_data.generate_id(),
        payment_proof_id=feedback_data.payment_proof_id,
        timestamp=feedback_data.generate_timestamp(),
        ocr_extracted_amount=feedback_data.corrected_amount,  # Using corrected amount as original for feedback
        ocr_extracted_transaction_id=feedback_data.corrected_transaction_id,
        ocr_extracted_date=feedback_data.corrected_date,
        ocr_confidence=0.8,  # Default confidence
        user_corrected_amount=feedback_data.corrected_amount,
        user_corrected_transaction_id=feedback_data.corrected_transaction_id,
        user_corrected_date=feedback_data.corrected_date,
        feedback_type=feedback_data.feedback_type.value,
        notes=feedback_data.notes,
        used_for_learning=False,
        learning_impact=0.0,
        is_legitimate_receipt=feedback_data.is_legitimate_receipt
    )

    # Submit to self-learning system
    self_learning_ocr.submit_feedback(feedback)

    # Save to database for persistence (only if not in mock mode)
    if not is_mock_mode():
        feedback_record = {
            "id": feedback.feedback_id,
            "payment_proof_id": feedback_data.payment_proof_id,
            "user_id": current_user["id"],
            "feedback_type": feedback_data.feedback_type.value,
            "corrected_amount": feedback_data.corrected_amount,
            "corrected_transaction_id": feedback_data.corrected_transaction_id,
            "corrected_date": feedback_data.corrected_date,
            "corrected_bank": feedback_data.corrected_bank,
            "corrected_fields": [f.value for f in feedback_data.corrected_fields],
            "notes": feedback_data.notes,
            "is_legitimate_receipt": feedback_data.is_legitimate_receipt,
            "quality_rating": feedback_data.quality_rating,
        }

        supabase.table("ocr_feedback").insert(feedback_record).execute()

    return {
        "success": True,
        "message": "Terima kasih! Feedback Anda membantu sistem kami belajar.",
        "feedback_id": feedback.feedback_id
    }

@app.get("/feedback/uncertainty-report/{payment_id}", tags=["Feedback"])
async def get_uncertainty_report(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed uncertainty report for a payment proof.

    This shows all the doubts and alternative interpretations
    so users can make informed decisions.
    """

    # Build a mock OCR result for demonstration
    ocr_result = {
        "extracted_amount": 100000,
        "extracted_transaction_id": "TRX123456",
        "extracted_date": "2024-01-01",
        "extracted_bank": "BCA",
        "confidence_score": 0.75
    }

    # Build image analysis from mock data
    image_analysis = {
        "dominant_colors": ["#00529F", "#FFFFFF"],  # BCA blue and white
        "risk_level": "LOW"
    }

    # Generate uncertainty report
    extraction = self_learning_ocr.extract_with_uncertainty(
        ocr_result,
        image_analysis,
        provider="BCA"
    )

    # Determine confidence level
    overall_conf = extraction["overall_confidence"]
    if overall_conf < 0.5:
        confidence_level = "LOW"
    elif overall_conf < 0.7:
        confidence_level = "MEDIUM"
    else:
        confidence_level = "HIGH"

    report = OCRUncertaintyReport(
        overall_confidence=overall_conf,
        confidence_level=confidence_level,
        amount_confidence=extraction["amount"]["confidence"],
        transaction_id_confidence=extraction["transaction_id"]["confidence"],
        date_confidence=extraction["date"]["confidence"],
        bank_confidence=extraction["bank"]["confidence"],
        uncertainty_flags=extraction["uncertainty_flags"],
        warnings=extraction["warnings"],
        alternatives={
            "amount": extraction["amount"]["alternatives"],
            "transaction_id": extraction["transaction_id"]["alternatives"],
            "date": extraction["date"]["alternatives"]
        },
        needs_manual_verification=extraction["needs_verification"],
        verification_reason="Confidence level below threshold" if extraction["needs_verification"] else ""
    )

    return report.dict()

# ============ HEALTH CHECK ============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.1.1", "timestamp": datetime.now().isoformat()}

@app.get("/validation/test", tags=["Health"])
async def test_validation():
    """Test validation endpoint for debugging"""
    return {
        "validator_initialized": validator is not None,
        "fraud_service_initialized": fraud_service is not None,
        "rate_limiter_initialized": rate_limiter is not None,
        "self_learning_ocr_initialized": self_learning_ocr is not None,
        "mock_mode": is_mock_mode()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)