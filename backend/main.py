from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from database import supabase
from auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from services.payment import PaymentService
from services.fraud import FraudService
from services.notification import NotificationService
from models import UserCreate, PaymentProofCreate
from validators import PaymentValidator, FileValidationResult, OCRResult, ImageAnalysisResult
from rate_limiter import RateLimiter, upload_limit, get_client_ip, check_ip_blocked
from ocr_learning import SelfLearningOCR, UserFeedback, LearningMetrics
from feedback_models import UserFeedbackCreate, OCRUncertaintyReport, LearningMetricsResponse, ReceiptFormatInfo
from datetime import datetime, timedelta
from typing import Optional, List
import aiofiles
import os
from uuid import uuid4
import base64

app = FastAPI(title="Aman ga? API", version="2.1.0", description="Secure payment verification system with AI-powered fraud detection and self-learning OCR")

# Initialize rate limiter
rate_limiter = RateLimiter()
rate_limiter.setup_app(app)

# Initialize self-learning OCR
self_learning_ocr = SelfLearningOCR()

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

# ============ PAYMENT ENDPOINTS ============

@app.post("/payment/upload", tags=["Payment"])
async def upload_payment_proof(
    service_type: str,
    amount: int,
    payment_method: str,
    bank_name: str,
    transaction_id: str,
    transaction_date: str,
    notes: Optional[str] = None,
    proof_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """
    Upload payment proof for verification with comprehensive validation
    
    Required fields:
    - service_type: CEK_DASAR, CEK_DEEP, or CEK_PLUS
    - amount: Payment amount in IDR (Rp 100 - Rp 100,000,000)
    - payment_method: BANK_TRANSFER, GOPAY, OVO, DANA, LINKAJA
    - bank_name: BCA, BRI, BNI, MANDIRI, PERMATA, DANAMON, CIMB, MAYBANK, BTN, OTHER
    - transaction_id: Unique transaction identifier (5-50 chars, alphanumeric)
    - transaction_date: ISO format date (YYYY-MM-DDTHH:MM:SS)
    - proof_image: Screenshot of transfer (JPG/PNG, max 10MB)
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
    
    # Step 2: Validate payment data
    payment_data = {
        "service_type": service_type,
        "amount": amount,
        "payment_method": payment_method,
        "bank_name": bank_name,
        "transaction_id": transaction_id,
        "transaction_date": transaction_date,
        "notes": notes
    }
    
    is_valid, error_msg, validated_data = validator.validate_payment_data(payment_data)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Step 3: Analyze image for manipulation
    image_analysis = validator.analyze_image(file_content)
    
    # Step 4: Extract OCR data
    ocr_result = validator.extract_ocr(file_content)
    
    # Step 5: Verify OCR matches form data
    if ocr_result.confidence_score > 0.3:  # Only verify if OCR has reasonable confidence
        validator.verify_ocr_matches_form(ocr_result, validated_data)
    
    # Step 6: Comprehensive fraud check with all validation results
    fraud_check_data = {
        **payment_data,
        "proof_image_hash": file_validation.image_hash
    }
    
    fraud_check = fraud_service.calculate_risk_score(
        current_user["id"], 
        fraud_check_data,
        image_analysis=image_analysis.__dict__,
        ocr_result=ocr_result.__dict__
    )
    
    # Block critical risk uploads
    if fraud_check["risk_level"] == "CRITICAL":
        # Create fraud flag for review
        fraud_service.create_fraud_flag(
            current_user["id"],
            "",  # Will be set after payment proof creation
            "MANIPULATED_IMAGE" if image_analysis.is_manipulated else "SUSPICIOUS_PATTERN",
            "CRITICAL"
        )
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Payment flagged for critical risk",
                "risk_factors": fraud_check["risk_factors"],
                "message": "This payment has been flagged for manual review due to high risk indicators"
            }
        )
    
    # Step 7: Create payment proof with all validation data
    proof_data = {
        "service_type": validated_data.service_type.value,
        "amount": validated_data.amount,
        "payment_method": validated_data.payment_method.value,
        "bank_name": validated_data.bank_name.value,
        "transaction_id": validated_data.transaction_id,
        "transaction_date": validated_data.transaction_date,
        "proof_image_url": f"/storage/payment_proofs/{uuid4()}.{proof_image.filename.split('.')[-1]}",
        "proof_image_hash": file_validation.image_hash,
        "ocr_extracted_amount": ocr_result.extracted_amount,
        "ocr_extracted_transaction_id": ocr_result.extracted_transaction_id,
        "ocr_confidence": ocr_result.confidence_score,
        "image_manipulation_detected": image_analysis.is_manipulated,
        "image_risk_level": image_analysis.risk_level,
        "fraud_risk_score": fraud_check["risk_score"],
        "fraud_risk_factors": fraud_check["risk_factors"]
    }
    
    result = payment_service.create_payment_proof(current_user["id"], proof_data)
    
    # Get user info for notification
    user = supabase.table("users").select("email, phone").eq("id", current_user["id"]).execute().data[0]
    
    # Send notification
    notification_service.notify_payment_uploaded(
        user["email"],
        user.get("phone"),
        result["id"],
        service_type,
        amount,
        result["status"]
    )
    
    # Build response with validation details
    response = {
        "success": True,
        "payment_id": result["id"],
        "status": result["status"],
        "message": "Payment auto-approved! Service activated." if result["status"] == "AUTO_APPROVED" else "Payment pending verification (5-30 minutes)",
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
            "mismatches": ocr_result.mismatches if not ocr_result.matches_form else []
        },
        "image_analysis": {
            "manipulation_detected": image_analysis.is_manipulated,
            "risk_level": image_analysis.risk_level,
            "quality_score": round(image_analysis.quality_score * 100, 1),
            "indicators": image_analysis.manipulation_indicators
        },
        "fraud_assessment": {
            "risk_score": fraud_check["risk_score"],
            "risk_level": fraud_check["risk_level"],
            "risk_factors": fraud_check["risk_factors"],
            "requires_manual_review": fraud_check["requires_manual_review"]
        }
    }
    
    return response

@app.get("/payment/my", tags=["Payment"])
async def get_my_payments(current_user: dict = Depends(get_current_user)):
    """Get current user's payment history"""

    result = supabase.table("payment_proofs").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).execute()

    return result.data

@app.get("/payment/credits", tags=["Payment"])
async def get_my_credits(current_user: dict = Depends(get_current_user)):
    """Get current user's active service credits"""

    credits = payment_service.get_user_credits(current_user["id"])

    return credits

# ============ ADMIN ENDPOINTS ============

@app.get("/admin/payments/pending", tags=["Admin"])
async def get_pending_payments(current_user: dict = Depends(get_current_user)):
    """Get all pending payments for admin review (ADMIN/FINANCE only)"""

    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    payments = payment_service.get_pending_payments()

    return payments

@app.post("/admin/payment/{payment_id}/approve", tags=["Admin"])
async def approve_payment(
    payment_id: str,
    notes: str = "",
    current_user: dict = Depends(get_current_user)
):
    """Approve a pending payment (ADMIN/FINANCE only)"""

    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Get payment proof
    payment = supabase.table("payment_proofs").select("*").eq("id", payment_id).execute()

    if not payment.data:
        raise HTTPException(status_code=404, detail="Payment not found")

    result = payment_service.approve_payment(payment_id, current_user["id"], notes)

    # Get user info for notification
    user = supabase.table("users").select("email, phone").eq("id", payment.data[0]["user_id"]).execute().data[0]

    # Send approval notification
    notification_service.notify_payment_approved(
        user["email"],
        user.get("phone"),
        payment_id,
        payment.data[0]["service_type"]
    )

    return result

@app.post("/admin/payment/{payment_id}/reject", tags=["Admin"])
async def reject_payment(
    payment_id: str,
    reason: str,
    current_user: dict = Depends(get_current_user)
):
    """Reject a pending payment (ADMIN/FINANCE only)"""

    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Get payment proof
    payment = supabase.table("payment_proofs").select("*").eq("id", payment_id).execute()

    if not payment.data:
        raise HTTPException(status_code=404, detail="Payment not found")

    result = payment_service.reject_payment(payment_id, current_user["id"], reason)

    # Get user info for notification
    user = supabase.table("users").select("email, phone").eq("id", payment.data[0]["user_id"]).execute().data[0]

    # Send rejection notification
    notification_service.notify_payment_rejected(
        user["email"],
        user.get("phone"),
        payment_id,
        reason
    )

    return result

@app.post("/admin/payment/{payment_id}/flag", tags=["Admin"])
async def flag_fraud(
    payment_id: str,
    flag_type: str,
    severity: str = "HIGH",
    current_user: dict = Depends(get_current_user)
):
    """Flag a payment as fraudulent (ADMIN only)"""

    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Get payment proof
    payment = supabase.table("payment_proofs").select("*").eq("id", payment_id).execute()

    if not payment.data:
        raise HTTPException(status_code=404, detail="Payment not found")

    result = fraud_service.create_fraud_flag(
        payment.data[0]["user_id"],
        payment_id,
        flag_type,
        severity,
        current_user["id"]
    )

    # Get user info for notification
    user = supabase.table("users").select("email, phone").eq("id", payment.data[0]["user_id"]).execute().data[0]

    # Send fraud notification
    notification_service.notify_fraud_flag(
        user["email"],
        user.get("phone"),
        "SUSPENSION" if severity in ["HIGH", "CRITICAL"] else "WARNING"
    )

    return result

@app.get("/admin/fraud/pending", tags=["Admin"])
async def get_pending_fraud_reviews(current_user: dict = Depends(get_current_user)):
    """Get all pending fraud flag reviews (ADMIN only)"""

    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    flags = fraud_service.get_pending_fraud_reviews()

    return flags

@app.post("/admin/fraud/{flag_id}/review", tags=["Admin"])
async def review_fraud_flag(
    flag_id: str,
    status: str,
    action_taken: str,
    current_user: dict = Depends(get_current_user)
):
    """Review and resolve a fraud flag (ADMIN only)"""

    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = fraud_service.review_fraud_flag(flag_id, current_user["id"], status, action_taken)

    return result

@app.get("/admin/stats", tags=["Admin"])
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Get admin dashboard statistics (ADMIN/FINANCE only)"""

    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Get counts
    pending = supabase.table("payment_proofs").select("*", count="exact").eq("status", "PENDING").execute()
    approved_today = supabase.table("payment_proofs").select("*", count="exact").eq("status", "APPROVED").gte("created_at", datetime.now().date().isoformat()).execute()
    rejected_today = supabase.table("payment_proofs").select("*", count="exact").eq("status", "REJECTED").gte("created_at", datetime.now().date().isoformat()).execute()
    fraud_flags = supabase.table("fraud_flags").select("*", count="exact").eq("status", "PENDING_REVIEW").execute()

    return {
        "pending_payments": pending.count,
        "approved_today": approved_today.count,
        "rejected_today": rejected_today.count,
        "pending_fraud_reviews": fraud_flags.count
    }

# ============ SERVICE ENDPOINTS ============

@app.get("/service/use/{service_type}", tags=["Service"])
async def use_service(
    service_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Use a service credit"""

    credits = payment_service.get_user_credits(current_user["id"])

    available_credit = None
    for credit in credits:
        if credit["service_type"] == service_type and credit["used_quantity"] < credit["quantity"]:
            available_credit = credit
            break

    if not available_credit:
        raise HTTPException(status_code=400, detail="No available service credit")

    # Update credit
    supabase.table("service_credits").update({
        "used_quantity": available_credit["used_quantity"] + 1,
        "used_at": datetime.now().isoformat()
    }).eq("id", available_credit["id"]).execute()

    # Here you would call the actual AI service
    # For POC, return mock result based on service type

    mock_results = {
        "CEK_DASAR": {
            "risk_score": 45,
            "risk_level": "MEDIUM",
            "indicators": ["No negative records found"],
            "recommendation": "Proceed with caution"
        },
        "CEK_DEEP": {
            "risk_score": 75,
            "risk_level": "HIGH",
            "indicators": [
                "Pattern matches known fraud cases",
                "Multiple complaints found",
                "Unusual transaction pattern"
            ],
            "recommendation": "Do not proceed"
        },
        "CEK_PLUS": {
            "risk_score": 30,
            "risk_level": "LOW",
            "indicators": ["Clean record", "Verified business"],
            "recommendation": "Safe to proceed",
            "legal_analysis": "No concerning legal issues detected"
        }
    }

    return {
        "success": True,
        "service_type": service_type,
        "credit_remaining": available_credit["quantity"] - available_credit["used_quantity"] - 1,
        "result": mock_results.get(service_type, {"error": "Unknown service type"})
    }

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
        ocr_extracted_amount=None,  # Would fetch from payment proof
        ocr_extracted_transaction_id=None,
        ocr_extracted_date=None,
        ocr_confidence=0.0,
        user_corrected_amount=feedback_data.corrected_amount,
        user_corrected_transaction_id=feedback_data.corrected_transaction_id,
        user_corrected_date=feedback_data.corrected_date,
        feedback_type=feedback_data.feedback_type.value,
        notes=feedback_data.notes,
        used_for_learning=False,
        learning_impact=0.0
    )
    
    # Submit to self-learning system
    self_learning_ocr.submit_feedback(feedback)
    
    # Save to database for persistence
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
        "created_at": datetime.now().isoformat()
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
    
    # Get payment proof from database
    payment = supabase.table("payment_proofs").select("*").eq("id", payment_id).execute()
    
    if not payment.data:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment_data = payment.data[0]
    
    # Build OCR result from stored data
    ocr_result = {
        "extracted_amount": payment_data.get("ocr_extracted_amount"),
        "extracted_transaction_id": payment_data.get("ocr_extracted_transaction_id"),
        "extracted_date": payment_data.get("ocr_extracted_date"),
        "extracted_bank": payment_data.get("ocr_extracted_bank"),
        "confidence_score": payment_data.get("ocr_confidence_score", 0.5)
    }
    
    # Build image analysis from stored data
    image_analysis = {
        "dominant_colors": [],  # Would need to store this
        "risk_level": payment_data.get("image_risk_level", "UNKNOWN")
    }
    
    # Generate uncertainty report
    extraction = self_learning_ocr.extract_with_uncertainty(
        ocr_result, 
        image_analysis,
        provider=payment_data.get("bank_name")
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

@app.get("/feedback/learning-metrics", tags=["Feedback"])
async def get_learning_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get learning metrics and accuracy statistics.
    
    Shows how the system is improving over time.
    """
    
    # Only admins can see full metrics
    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get feedback count from database
    feedback_count = supabase.table("ocr_feedback").select("*", count="exact").execute()
    
    # Calculate accuracy from feedback
    all_feedback = supabase.table("ocr_feedback").select("*").order("created_at", desc=True).limit(100).execute()
    
    corrections = sum(1 for f in all_feedback.data if f.get("feedback_type") == "CORRECTION")
    confirmations = sum(1 for f in all_feedback.data if f.get("feedback_type") == "CONFIRMATION")
    
    # Calculate field-level accuracy
    total_with_corrections = len([f for f in all_feedback.data if f.get("corrected_fields")])
    
    metrics = LearningMetricsResponse(
        total_samples=self_learning_ocr.metrics.total_samples,
        total_feedback=feedback_count.count if hasattr(feedback_count, 'count') else len(all_feedback.data),
        correction_rate=corrections / max(1, feedback_count.count) if hasattr(feedback_count, 'count') else 0,
        overall_accuracy=1.0 - (corrections / max(1, len(all_feedback.data))),
        amount_accuracy=0.85,  # Would calculate from actual data
        transaction_id_accuracy=0.80,
        date_accuracy=0.90,
        avg_confidence=0.75,
        confidence_calibration_score=0.70,
        provider_accuracy={
            "BCA": 0.88,
            "BRI": 0.85,
            "MANDIRI": 0.87,
            "GOPAY": 0.82,
            "OVO": 0.80
        },
        accuracy_trend=[0.75, 0.78, 0.80, 0.82, 0.83, 0.85, 0.87],
        last_updated=datetime.now().isoformat()
    )
    
    return metrics.dict()

@app.get("/receipt-formats", tags=["Feedback"])
async def get_receipt_formats():
    """
    Get list of known receipt formats.
    
    Shows which banks/e-wallets the system recognizes.
    """
    
    formats = []
    for provider, fmt in self_learning_ocr.receipt_formats.items():
        formats.append(ReceiptFormatInfo(
            provider=fmt.provider,
            bank_name=fmt.bank_name,
            sample_count=fmt.sample_count,
            confidence_score=fmt.confidence_score,
            typical_colors=fmt.typical_colors,
            has_qr_code=fmt.has_qr_code,
            common_issues=[],
            tips=[
                f"Pastikan gambar jelas dan tidak blur",
                f"Usahakan seluruh receipt terlihat",
                f"Hindari silau atau bayangan"
            ]
        ).dict())
    
    return {"formats": formats}

@app.post("/receipt-formats/{provider}/improve", tags=["Feedback"])
async def improve_receipt_format(
    provider: str,
    feedback_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit improvement suggestion for a receipt format.
    
    Users can suggest better patterns for their bank's receipts.
    """
    
    if provider not in self_learning_ocr.receipt_formats:
        raise HTTPException(status_code=404, detail=f"Receipt format '{provider}' not found")
    
    # Record improvement suggestion
    suggestion = {
        "provider": provider,
        "suggested_by": current_user["id"],
        "suggested_at": datetime.now().isoformat(),
        "feedback": feedback_data
    }
    
    supabase.table("receipt_format_suggestions").insert(suggestion).execute()
    
    return {
        "success": True,
        "message": f"Terima kasih! Saran Anda untuk {provider} akan ditinjau."
    }

# ============ HEALTH CHECK ============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.1.0", "timestamp": datetime.now().isoformat()}

@app.get("/validation/test", tags=["Health"])
async def test_validation():
    """Test validation endpoint for debugging"""
    return {
        "validator_initialized": validator is not None,
        "fraud_service_initialized": fraud_service is not None,
        "rate_limiter_initialized": rate_limiter is not None,
        "self_learning_ocr_initialized": self_learning_ocr is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
