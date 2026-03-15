from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from database import supabase
from auth import get_password_hash, verify_password, create_access_token, get_current_user
from services.payment import PaymentService
from models import UserCreate, PaymentProofCreate
from datetime import timedelta
import aiofiles
import os
from uuid import uuid4

app = FastAPI(title="aman ga? API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

payment_service = PaymentService()

# ============ AUTH ENDPOINTS ============

@app.post("/register")
async def register(user: UserCreate):
    """Register new user"""
    
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
    
    return {"success": True, "user_id": result.data[0]["id"]}

@app.post("/token")
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
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user

# ============ PAYMENT ENDPOINTS ============

@app.post("/payment/upload")
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
    """Upload payment proof"""
    
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
    
    # Create payment proof
    payment_data = {
        "service_type": service_type,
        "amount": amount,
        "payment_method": payment_method,
        "bank_name": bank_name,
        "transaction_id": transaction_id,
        "transaction_date": transaction_date,
        "proof_image_url": proof_url
    }
    
    result = payment_service.create_payment_proof(current_user["id"], payment_data)
    
    return {
        "success": True,
        "payment_id": result["id"],
        "status": result["status"],
        "message": "Payment auto-approved" if result["status"] == "AUTO_APPROVED" else "Payment pending verification"
    }

@app.get("/payment/my")
async def get_my_payments(current_user: dict = Depends(get_current_user)):
    """Get user's payment history"""
    
    result = supabase.table("payment_proofs").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).execute()
    
    return result.data

@app.get("/payment/credits")
async def get_my_credits(current_user: dict = Depends(get_current_user)):
    """Get user's service credits"""
    
    credits = payment_service.get_user_credits(current_user["id"])
    
    return credits

# ============ ADMIN ENDPOINTS ============

@app.get("/admin/payments/pending")
async def get_pending_payments(current_user: dict = Depends(get_current_user)):
    """Get all pending payments (admin only)"""
    
    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    payments = payment_service.get_pending_payments()
    
    return payments

@app.post("/admin/payment/{payment_id}/approve")
async def approve_payment(
    payment_id: str,
    notes: str = "",
    current_user: dict = Depends(get_current_user)
):
    """Approve payment (admin only)"""
    
    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = payment_service.approve_payment(payment_id, current_user["id"], notes)
    
    return result

@app.post("/admin/payment/{payment_id}/reject")
async def reject_payment(
    payment_id: str,
    reason: str,
    current_user: dict = Depends(get_current_user)
):
    """Reject payment (admin only)"""
    
    if current_user["role"] not in ["ADMIN", "FINANCE"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = payment_service.reject_payment(payment_id, current_user["id"], reason)
    
    return result

@app.post("/admin/payment/{payment_id}/flag")
async def flag_fraud(
    payment_id: str,
    flag_type: str,
    severity: str,
    current_user: dict = Depends(get_current_user)
):
    """Flag payment as fraud (admin only)"""
    
    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = payment_service.flag_fraud(payment_id, current_user["id"], flag_type, severity)
    
    return result

# ============ SERVICE ENDPOINTS ============

@app.get("/service/use/{service_type}")
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
    # For POC, return mock result
    
    return {
        "success": True,
        "service_type": service_type,
        "message": "Service activated. In production, this would call AI analysis.",
        "mock_result": {
            "risk_score": 75,
            "risk_level": "HIGH",
            "indicators": ["Pattern matches known fraud cases"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
