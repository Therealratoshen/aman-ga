from database import supabase
from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple

class FraudService:
    """Fraud detection and prevention service"""
    
    # Duplicate detection thresholds
    IMAGE_HASH_SIMILARITY_THRESHOLD = 0.95  # 95% similar = duplicate
    AMOUNT_MATCH_TOLERANCE = 0  # Exact match required
    
    def check_duplicate_proof(self, user_id: str, transaction_id: str) -> bool:
        """Check if transaction ID already exists"""

        result = supabase.table("payment_proofs").select("*").eq("transaction_id", transaction_id).execute()

        return len(result.data) > 0
    
    def check_duplicate_image(self, image_hash: str, user_id: str = None) -> Tuple[bool, Optional[str]]:
        """
        Check if image hash matches existing payment proof
        Returns (is_duplicate, existing_payment_id)
        """
        try:
            from validators import PaymentValidator
            validator = PaymentValidator()
            
            # Get all payment proofs with image hashes
            result = supabase.table("payment_proofs").select("id, user_id, proof_image_hash, created_at").execute()
            
            if not result.data:
                return False, None
            
            for payment in result.data:
                existing_hash = payment.get("proof_image_hash")
                if not existing_hash:
                    continue
                
                # Calculate similarity
                similarity = validator.calculate_image_similarity(image_hash, existing_hash)
                
                if similarity >= self.IMAGE_HASH_SIMILARITY_THRESHOLD:
                    # Found duplicate
                    return True, payment["id"]
            
            return False, None
            
        except Exception as e:
            print(f"Error checking duplicate image: {e}")
            return False, None
    
    def check_duplicate_transaction(self, user_id: str, amount: int, transaction_date: str, bank_name: str) -> Tuple[bool, Optional[str]]:
        """
        Check for duplicate transaction with same amount, date, and bank
        Returns (is_duplicate, existing_payment_id)
        """
        try:
            # Get user's recent payments
            result = supabase.table("payment_proofs").select("*").eq("user_id", user_id).execute()
            
            if not result.data:
                return False, None
            
            for payment in result.data:
                # Check if same amount, date, and bank
                if (payment.get("amount") == amount and 
                    payment.get("bank_name") == bank_name):
                    
                    # Check if same date (compare just the date part)
                    try:
                        existing_date = payment.get("transaction_date", "")[:10]
                        new_date = transaction_date[:10]
                        
                        if existing_date == new_date:
                            return True, payment["id"]
                    except:
                        continue
            
            return False, None
            
        except Exception as e:
            print(f"Error checking duplicate transaction: {e}")
            return False, None
    
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
    
    def calculate_risk_score(
        self,
        user_id: str,
        payment_data: dict,
        image_analysis: dict = None,
        ocr_result: dict = None,
        authenticity_result: dict = None,
        validator_instance=None  # Pass validator instance for additional checks
    ) -> dict:
        """Calculate fraud risk score for a payment"""

        risk_score = 0
        risk_factors = []

        # Check fraud history
        fraud_history = supabase.table("fraud_flags").select("*").eq("user_id", user_id).eq("status", "CONFIRMED").execute()

        if len(fraud_history.data) > 0:
            risk_score += 50
            risk_factors.append("Previous fraud history")

        # Check for duplicate transaction ID
        if self.check_duplicate_proof(user_id, payment_data.get("transaction_id", "")):
            risk_score += 40
            risk_factors.append("Duplicate transaction ID")

        # Check for duplicate image (if hash provided)
        if payment_data.get("proof_image_hash"):
            is_duplicate, existing_id = self.check_duplicate_image(
                payment_data["proof_image_hash"],
                user_id
            )
            if is_duplicate:
                risk_score += 60
                risk_factors.append(f"Duplicate image detected (matches payment {existing_id[:8]})")

        # Check for duplicate transaction pattern
        if payment_data.get("amount") and payment_data.get("transaction_date") and payment_data.get("bank_name"):
            is_duplicate, existing_id = self.check_duplicate_transaction(
                user_id,
                payment_data["amount"],
                payment_data["transaction_date"],
                payment_data["bank_name"]
            )
            if is_duplicate:
                risk_score += 35
                risk_factors.append(f"Duplicate transaction pattern (same amount, date, bank)")

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

        # Check image analysis results
        if image_analysis:
            if image_analysis.get("is_manipulated"):
                risk_score += 70
                risk_factors.append("Image manipulation detected")

            if image_analysis.get("risk_level") == "HIGH":
                risk_score += 30
                risk_factors.append("High risk image indicators")
            elif image_analysis.get("risk_level") == "CRITICAL":
                risk_score += 50
                risk_factors.append("Critical risk image indicators")

            if image_analysis.get("manipulation_indicators"):
                for indicator in image_analysis["manipulation_indicators"]:
                    risk_factors.append(f"Image: {indicator}")

        # Check OCR mismatches
        if ocr_result and ocr_result.get("mismatches"):
            mismatch_count = len(ocr_result["mismatches"])
            risk_score += min(50, mismatch_count * 25)  # 25 points per mismatch, max 50
            risk_factors.append(f"OCR detected {mismatch_count} mismatch(es) between form and image")

        # Check OCR confidence
        if ocr_result and ocr_result.get("confidence_score", 1.0) < 0.3:
            risk_score += 15
            risk_factors.append("Low OCR confidence - image may be unclear or manipulated")

        # Check authenticity results
        if authenticity_result:
            authenticity_score = authenticity_result.get("authenticity_score", 0.5)
            is_likely_authentic = authenticity_result.get("is_likely_authentic", True)

            if not is_likely_authentic:
                # Lower authenticity score increases risk
                authenticity_risk = (1 - authenticity_score) * 80  # Max 80 points for low authenticity
                risk_score += authenticity_risk
                risk_factors.append(f"Receipt authenticity low (score: {authenticity_score:.2f})")

        # Additional validations using validator instance
        if validator_instance:
            # Check transaction frequency
            try:
                from database import supabase as db_client
                freq_result = validator_instance.validate_transaction_frequency(
                    user_id, 
                    db_client, 
                    period_hours=1, 
                    max_transactions=5
                )
                
                if not freq_result.is_within_limit:
                    risk_score += 20
                    risk_factors.append(f"High transaction frequency: {freq_result.transaction_count} transactions in last hour")
            except:
                # If frequency check fails, continue without penalty
                pass

            # Check for suspicious patterns
            try:
                pattern_result = validator_instance.validate_suspicious_patterns(
                    ocr_result.get("extracted_text", "") if ocr_result else "",
                    payment_data.get("amount", 0),
                    payment_data.get("bank_name", "")
                )
                
                if pattern_result.is_suspicious:
                    risk_score += int(pattern_result.confidence_score * 50)  # Scale to 0-50 points
                    risk_factors.append(f"Suspicious pattern detected: {', '.join(pattern_result.pattern_types)}")
            except:
                # If pattern check fails, continue without penalty
                pass

            # Check timing patterns
            try:
                timing_result = validator_instance.validate_timing_patterns(
                    payment_data.get("transaction_date", ""),
                    ocr_result.get("extracted_date", "") if ocr_result else ""
                )
                
                if timing_result.is_suspicious:
                    risk_score += int(timing_result.confidence_score * 40)  # Scale to 0-40 points
                    risk_factors.append(f"Suspicious timing pattern: {', '.join(timing_result.timing_issues)}")
            except:
                # If timing check fails, continue without penalty
                pass

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
