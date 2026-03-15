from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from database import supabase
from auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from services.payment import PaymentService
from services.fraud import FraudService
from services.notification import NotificationService
from models import UserCreate, PaymentProofCreate
from datetime import datetime, timedelta
import aiofiles
import os
from uuid import uuid4

app = FastAPI(title="Aman ga? API", version="1.0.0", description="Payment verification system with auto-approval and fraud detection")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
payment_service = PaymentService()
fraud_service = FraudService()
notification_service = NotificationService()

# ============ AUTH ENDPOINTS ============

@app.post("/register", tags=["Authentication"])
async def register(user: UserCreate):
    """Register a new user account"""
    
    # Check if user exists
    existing = supabase.table("users").select("*").eq("email", user.email).execute()
    
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
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
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    
    user = supabase.table("users").select("*").eq("email", form_data.username).execute()
    
    if not user.data:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(form_data.password, user.data[0]["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if user.data[0]["status"] != "ACTIVE":
        raise HTTPException(status_code=400, detail="Account is suspended or banned")
    
    access_token = create_access_token(
        data={"sub": user.data[0]["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": user.data[0]["email"], "role": user.data[0]["role"]}}

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
    proof_image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload payment proof for verification"""
    
    # Validate file type
    if not proof_image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Upload image to storage
    file_extension = proof_image.filename.split(".")[-1]
    file_name = f"{uuid4()}.{file_extension}"
    file_path = f"payment_proofs/{file_name}"
    
    async with aiofiles.open(f"/tmp/{file_name}", 'wb') as out_file:
        content = await proof_image.read()
        await out_file.write(content)
    
    # In production, upload to Supabase Storage or S3
    # For POC, we'll use a placeholder URL
    proof_url = f"https://storage.example.com/{file_path}"
    
    # Prepare payment data
    payment_data = {
        "service_type": service_type,
        "amount": amount,
        "payment_method": payment_method,
        "bank_name": bank_name,
        "transaction_id": transaction_id,
        "transaction_date": transaction_date,
        "proof_image_url": proof_url
    }
    
    # Fraud check
    fraud_check = fraud_service.calculate_risk_score(current_user["id"], payment_data)
    
    if fraud_check["risk_level"] == "CRITICAL":
        # Flag for fraud
        fraud_service.create_fraud_flag(
            current_user["id"],
            "",  # Will be set after payment proof creation
            "SUSPICIOUS_PATTERN",
            "HIGH"
        )
        raise HTTPException(status_code=400, detail="Payment flagged for review due to suspicious activity")
    
    # Create payment proof
    result = payment_service.create_payment_proof(current_user["id"], payment_data)
    
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
    
    return {
        "success": True,
        "payment_id": result["id"],
        "status": result["status"],
        "message": "Payment auto-approved! Service activated." if result["status"] == "AUTO_APPROVED" else "Payment pending verification (5-30 minutes)",
        "risk_assessment": fraud_check if fraud_check["risk_score"] > 0 else None
    }

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

# ============ HEALTH CHECK ============

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
