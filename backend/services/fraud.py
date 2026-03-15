from database import supabase
from datetime import datetime
import re

class FraudService:
    """Fraud detection and prevention service"""
    
    def check_duplicate_proof(self, user_id: str, transaction_id: str) -> bool:
        """Check if transaction ID already exists"""
        
        result = supabase.table("payment_proofs").select("*").eq("transaction_id", transaction_id).execute()
        
        return len(result.data) > 0
    
    def check_suspicious_pattern(self, user_id: str) -> dict:
        """Check for suspicious payment patterns"""
        
        # Get user's payment history
        payments = supabase.table("payment_proofs").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        
        flags = {
            "rapid_submissions": False,
            "multiple_rejections": False,
            "unusual_amounts": False
        }
        
        if len(payments.data) < 2:
            return flags
        
        # Check rapid submissions (multiple payments within 1 hour)
        recent_payments = [p for p in payments.data if datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) > datetime.now().replace(tzinfo=None) - __import__("datetime").timedelta(hours=1)]
        if len(recent_payments) > 3:
            flags["rapid_submissions"] = True
        
        # Check multiple rejections
        rejected = [p for p in payments.data if p["status"] == "REJECTED"]
        if len(rejected) >= 3:
            flags["multiple_rejections"] = True
        
        return flags
    
    def analyze_image_metadata(self, image_url: str) -> dict:
        """
        Analyze image for manipulation signs
        In production, integrate with AI image analysis service
        """
        
        # Placeholder for AI image analysis
        # In production, use services like:
        # - AWS Rekognition
        # - Google Cloud Vision
        # - Custom ML model
        
        return {
            "manipulation_detected": False,
            "confidence": 0.0,
            "flags": []
        }
    
    def calculate_risk_score(self, user_id: str, payment_data: dict) -> dict:
        """Calculate fraud risk score for a payment"""
        
        risk_score = 0
        risk_factors = []
        
        # Check fraud history
        fraud_history = supabase.table("fraud_flags").select("*").eq("user_id", user_id).eq("status", "CONFIRMED").execute()
        
        if len(fraud_history.data) > 0:
            risk_score += 50
            risk_factors.append("Previous fraud history")
        
        # Check for duplicate transaction
        if self.check_duplicate_proof(user_id, payment_data.get("transaction_id", "")):
            risk_score += 40
            risk_factors.append("Duplicate transaction ID")
        
        # Check suspicious patterns
        patterns = self.check_suspicious_pattern(user_id)
        if patterns["rapid_submissions"]:
            risk_score += 20
            risk_factors.append("Rapid submissions detected")
        if patterns["multiple_rejections"]:
            risk_score += 25
            risk_factors.append("Multiple previous rejections")
        
        # Check amount threshold
        if payment_data.get("amount", 0) > 100000:
            risk_score += 15
            risk_factors.append("High amount transaction")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "CRITICAL"
        elif risk_score >= 50:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "requires_manual_review": risk_score >= 30
        }
    
    def create_fraud_flag(self, user_id: str, payment_proof_id: str, flag_type: str, severity: str, reviewed_by: str = None) -> dict:
        """Create a fraud flag record"""
        
        fraud_flag = {
            "user_id": user_id,
            "payment_proof_id": payment_proof_id,
            "flag_type": flag_type,
            "severity": severity,
            "status": "PENDING_REVIEW" if reviewed_by is None else "CONFIRMED",
            "action_taken": "NO_ACTION",
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.now().isoformat() if reviewed_by else None
        }
        
        result = supabase.table("fraud_flags").insert(fraud_flag).execute()
        
        # Auto-suspend for critical severity
        if severity == "CRITICAL":
            supabase.table("users").update({
                "status": "SUSPENDED",
                "updated_at": datetime.now().isoformat()
            }).eq("id", user_id).execute()
            
            # Revoke active service credits
            supabase.table("service_credits").update({
                "status": "REVOKED"
            }).eq("user_id", user_id).eq("status", "ACTIVE").execute()
        
        return result.data[0]
    
    def get_fraud_flags_by_user(self, user_id: str) -> list:
        """Get all fraud flags for a user"""
        
        result = supabase.table("fraud_flags").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        
        return result.data
    
    def get_pending_fraud_reviews(self) -> list:
        """Get all pending fraud flag reviews"""
        
        result = supabase.table("fraud_flags").select("""
            *,
            users (email, full_name),
            payment_proofs (service_type, amount)
        """).eq("status", "PENDING_REVIEW").order("created_at", desc=True).execute()
        
        return result.data
    
    def review_fraud_flag(self, flag_id: str, reviewer_id: str, status: str, action_taken: str) -> dict:
        """Review and resolve a fraud flag"""
        
        update_data = {
            "status": status,
            "reviewed_by": reviewer_id,
            "reviewed_at": datetime.now().isoformat(),
            "action_taken": action_taken
        }
        
        result = supabase.table("fraud_flags").update(update_data).eq("id", flag_id).execute()
        
        # Get flag details
        flag = supabase.table("fraud_flags").select("*").eq("id", flag_id).execute().data[0]
        
        # Take action based on decision
        if status == "CONFIRMED":
            if action_taken == "SUSPENSION":
                supabase.table("users").update({
                    "status": "SUSPENDED",
                    "updated_at": datetime.now().isoformat()
                }).eq("id", flag["user_id"]).execute()
            elif action_taken == "BAN":
                supabase.table("users").update({
                    "status": "BANNED",
                    "updated_at": datetime.now().isoformat()
                }).eq("id", flag["user_id"]).execute()
        elif status == "FALSE_POSITIVE":
            # Restore user status if was suspended
            user = supabase.table("users").select("status").eq("id", flag["user_id"]).execute().data[0]
            if user["status"] == "SUSPENDED":
                supabase.table("users").update({
                    "status": "ACTIVE",
                    "updated_at": datetime.now().isoformat()
                }).eq("id", flag["user_id"]).execute()
        
        return result.data[0]
