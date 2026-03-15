from database import supabase
from datetime import datetime
import random

class PaymentService:
    AUTO_APPROVE_THRESHOLD = 1000  # Rp 1.000
    RANDOM_AUDIT_RATE = 0.10  # 10%
    
    def create_payment_proof(self, user_id: str, payment_data: dict):
        """Create payment proof record"""
        
        # Determine if auto-approve
        auto_approve = self.should_auto_approve(user_id, payment_data)
        status = "AUTO_APPROVED" if auto_approve else "PENDING"
        
        payment_proof = {
            "user_id": user_id,
            "service_type": payment_data["service_type"],
            "amount": payment_data["amount"],
            "payment_method": payment_data["payment_method"],
            "bank_name": payment_data.get("bank_name"),
            "transaction_id": payment_data["transaction_id"],
            "transaction_date": payment_data["transaction_date"],
            "proof_image_url": payment_data["proof_image_url"],
            "status": status
        }
        
        result = supabase.table("payment_proofs").insert(payment_proof).execute()
        
        # If auto-approved, credit service immediately
        if auto_approve:
            self.credit_service(user_id, payment_data["service_type"], result.data[0]["id"])
        
        return result.data[0]
    
    def should_auto_approve(self, user_id: str, payment_data: dict) -> bool:
        """Determine if payment can be auto-approved"""
        
        # Check amount threshold
        if payment_data["amount"] > self.AUTO_APPROVE_THRESHOLD:
            return False
        
        # Check service type
        if payment_data["service_type"] != "CEK_DASAR":
            return False
        
        # Check user fraud history
        fraud_history = supabase.table("fraud_flags").select("*").eq("user_id", user_id).eq("status", "CONFIRMED").execute()
        
        if len(fraud_history.data) > 0:
            return False
        
        # Random audit (10%)
        if random.random() < self.RANDOM_AUDIT_RATE:
            return False
        
        return True
    
    def credit_service(self, user_id: str, service_type: str, payment_proof_id: str):
        """Credit service to user account"""
        
        service_credit = {
            "user_id": user_id,
            "service_type": service_type,
            "quantity": 1,
            "used_quantity": 0,
            "status": "ACTIVE",
            "payment_proof_id": payment_proof_id
        }
        
        supabase.table("service_credits").insert(service_credit).execute()
    
    def approve_payment(self, payment_id: str, admin_id: str, notes: str = ""):
        """Manually approve payment"""
        
        # Get payment proof
        payment = supabase.table("payment_proofs").select("*").eq("id", payment_id).execute()
        
        if not payment.data:
            return {"error": "Payment not found"}
        
        payment_data = payment.data[0]
        
        # Update status
        supabase.table("payment_proofs").update({
            "status": "APPROVED",
            "verified_by": admin_id,
            "verified_at": datetime.now().isoformat(),
            "verification_notes": notes,
            "updated_at": datetime.now().isoformat()
        }).eq("id", payment_id).execute()
        
        # Credit service
        self.credit_service(payment_data["user_id"], payment_data["service_type"], payment_id)
        
        # Log audit
        self.log_admin_action(admin_id, "APPROVE_PAYMENT", payment_id)
        
        return {"success": True, "payment_id": payment_id}
    
    def reject_payment(self, payment_id: str, admin_id: str, reason: str):
        """Reject payment"""
        
        supabase.table("payment_proofs").update({
            "status": "REJECTED",
            "verified_by": admin_id,
            "verified_at": datetime.now().isoformat(),
            "verification_notes": reason,
            "updated_at": datetime.now().isoformat()
        }).eq("id", payment_id).execute()
        
        # Log audit
        self.log_admin_action(admin_id, "REJECT_PAYMENT", payment_id)
        
        return {"success": True, "payment_id": payment_id}
    
    def flag_fraud(self, payment_id: str, admin_id: str, flag_type: str, severity: str):
        """Flag payment as fraudulent"""
        
        # Get payment proof
        payment = supabase.table("payment_proofs").select("*").eq("id", payment_id).execute()
        
        if not payment.data:
            return {"error": "Payment not found"}
        
        user_id = payment.data[0]["user_id"]
        
        # Create fraud flag
        fraud_flag = {
            "user_id": user_id,
            "payment_proof_id": payment_id,
            "flag_type": flag_type,
            "severity": severity,
            "status": "CONFIRMED",
            "action_taken": "SUSPENSION",
            "reviewed_by": admin_id,
            "reviewed_at": datetime.now().isoformat()
        }
        
        supabase.table("fraud_flags").insert(fraud_flag).execute()
        
        # Suspend user
        supabase.table("users").update({
            "status": "SUSPENDED",
            "updated_at": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        
        # Revoke service credits
        supabase.table("service_credits").update({
            "status": "REVOKED"
        }).eq("user_id", user_id).eq("status", "ACTIVE").execute()
        
        # Log audit
        self.log_admin_action(admin_id, "FLAG_FRAUD", payment_id)
        
        return {"success": True, "user_suspended": user_id}
    
    def log_admin_action(self, admin_id: str, action: str, target_id: str, details: dict = None):
        """Log admin action for audit"""
        
        audit_log = {
            "admin_id": admin_id,
            "action": action,
            "target_type": "payment_proof",
            "target_id": target_id,
            "details": details or {}
        }
        
        supabase.table("admin_audit_log").insert(audit_log).execute()
    
    def get_pending_payments(self):
        """Get all pending payments for admin review"""
        
        result = supabase.table("payment_proofs").select("""
            *,
            users (email, full_name, phone)
        """).eq("status", "PENDING").order("created_at", desc=True).execute()
        
        return result.data
    
    def get_user_credits(self, user_id: str):
        """Get user's service credits"""
        
        result = supabase.table("service_credits").select("*").eq("user_id", user_id).eq("status", "ACTIVE").execute()
        
        return result.data
