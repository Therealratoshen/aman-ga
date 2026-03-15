from database import supabase
from datetime import datetime
import requests
import os

class NotificationService:
    """Notification service for WhatsApp, Email, and Push notifications"""
    
    def __init__(self):
        self.whatsapp_api_key = os.getenv("WHATSAPP_API_KEY", "")
        self.whatsapp_api_url = os.getenv("WHATSAPP_API_URL", "")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        self.sendgrid_from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@amanga.id")
        self.sendgrid_from_name = os.getenv("SENDGRID_FROM_NAME", "Aman ga?")
        self.mock_mode = not (self.whatsapp_api_key and self.sendgrid_api_key)
    
    def send_whatsapp(self, phone: str, message: str) -> dict:
        """Send WhatsApp message via Fonnte"""
        
        if not self.whatsapp_api_key:
            print(f"📱 [WhatsApp MOCK] To: {phone}")
            print(f"   Message: {message[:100]}...")
            return {"success": True, "mock": True, "message": "Mock mode - no API key configured"}
        
        try:
            # Fonnte API format
            response = requests.post(
                self.whatsapp_api_url or "https://api.fonnte.com/send",
                headers={
                    "Authorization": self.whatsapp_api_key
                },
                data={
                    "target": phone,
                    "message": message,
                    "countryCode": "62"  # Indonesia
                }
            )
            
            result = response.json()
            return {
                "success": result.get("status", False),
                "response": result,
                "mock": False
            }
        except Exception as e:
            print(f"❌ [WhatsApp Error] {str(e)}")
            return {"success": False, "error": str(e), "mock": False}
    
    def send_email(self, email: str, subject: str, body: str) -> dict:
        """Send email via SendGrid"""
        
        if not self.sendgrid_api_key:
            print(f"📧 [Email MOCK] To: {email}")
            print(f"   Subject: {subject}")
            print(f"   Body: {body[:100]}...")
            return {"success": True, "mock": True, "message": "Mock mode - no API key configured"}
        
        try:
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {self.sendgrid_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [
                        {
                            "to": [{"email": email}],
                            "subject": subject
                        }
                    ],
                    "from": {
                        "email": self.sendgrid_from_email,
                        "name": self.sendgrid_from_name
                    },
                    "content": [
                        {
                            "type": "text/html",
                            "value": body
                        }
                    ]
                }
            )
            
            return {
                "success": response.status_code == 202,
                "status_code": response.status_code,
                "mock": False
            }
        except Exception as e:
            print(f"❌ [Email Error] {str(e)}")
            return {"success": False, "error": str(e), "mock": False}
    
    def notify_payment_uploaded(self, user_email: str, user_phone: str, payment_id: str, service_type: str, amount: int, status: str):
        """Notify user when payment proof is uploaded"""
        
        # WhatsApp notification
        whatsapp_msg = f"""🔔 *Aman ga? - Payment Received*

Payment ID: {payment_id[:8]}...
Service: {service_type}
Amount: Rp {amount:,}
Status: {status}

{'✅ Auto-approved! Service activated.' if status == 'AUTO_APPROVED' else '⏳ Waiting for verification (5-30 minutes)'}

Thank you for using Aman ga?"""
        
        if user_phone:
            self.send_whatsapp(user_phone, whatsapp_msg)
        
        # Email notification
        email_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; text-align: center;">
        <h1 style="color: white; margin: 0;">🔔 Payment Received</h1>
    </div>
    <div style="padding: 20px;">
        <p>Thank you for your payment!</p>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Payment ID</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">{payment_id[:8]}...</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Service</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">{service_type}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Amount</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">Rp {amount:,}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Status</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">
                    <span style="background: {'#d1fae5' if status == 'AUTO_APPROVED' else '#fef3c7'}; color: {'#065f46' if status == 'AUTO_APPROVED' else '#92400e'}; padding: 4px 8px; border-radius: 4px;">
                        {status}
                    </span>
                </td>
            </tr>
        </table>
        <div style="background: {'#d1fae5' if status == 'AUTO_APPROVED' else '#fef3c7'}; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; color: {'#065f46' if status == 'AUTO_APPROVED' else '#92400e'};">
                <strong>
                    {'✅ Your service has been auto-approved and activated!' if status == 'AUTO_APPROVED' else '⏳ Your payment is being verified. You will be notified once approved.'}
                </strong>
            </p>
        </div>
        <p>Thank you for using <strong style="color: #10b981;">Aman ga?</strong></p>
    </div>
</body>
</html>"""
        
        self.send_email(user_email, f"Aman ga? - Payment Received ({status})", email_body)
    
    def notify_payment_approved(self, user_email: str, user_phone: str, payment_id: str, service_type: str):
        """Notify user when payment is approved"""
        
        whatsapp_msg = f"""✅ *Payment Approved!*

Payment ID: {payment_id[:8]}...
Service: {service_type}

Your service credit has been activated. You can now use it in your dashboard.

Thank you for using Aman ga?"""
        
        if user_phone:
            self.send_whatsapp(user_phone, whatsapp_msg)
        
        email_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 20px; text-align: center;">
        <h1 style="color: white; margin: 0;">✅ Payment Approved</h1>
    </div>
    <div style="padding: 20px;">
        <p>Great news! Your payment has been approved.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Payment ID</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">{payment_id[:8]}...</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Service</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">{service_type}</td>
            </tr>
        </table>
        <div style="background: #d1fae5; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; color: #065f46;">
                <strong>Your service credit has been activated. Login to your dashboard to use it.</strong>
            </p>
        </div>
        <p>Thank you for using <strong style="color: #10b981;">Aman ga?</strong></p>
    </div>
</body>
</html>"""
        
        self.send_email(user_email, "Aman ga? - Payment Approved ✅", email_body)
    
    def notify_payment_rejected(self, user_email: str, user_phone: str, payment_id: str, reason: str):
        """Notify user when payment is rejected"""
        
        whatsapp_msg = f"""❌ *Payment Rejected*

Payment ID: {payment_id[:8]}...
Reason: {reason}

Please check your payment proof and resubmit. Contact support if you need help."""
        
        if user_phone:
            self.send_whatsapp(user_phone, whatsapp_msg)
        
        email_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding: 20px; text-align: center;">
        <h1 style="color: white; margin: 0;">❌ Payment Rejected</h1>
    </div>
    <div style="padding: 20px;">
        <p>We're sorry, but your payment could not be approved.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Payment ID</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">{payment_id[:8]}...</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Reason</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb; color: #dc2626;">{reason}</td>
            </tr>
        </table>
        <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; color: #92400e;">
                <strong>Please check your payment proof and resubmit. If you believe this is an error, contact our support team.</strong>
            </p>
        </div>
        <p><strong style="color: #10b981;">Aman ga?</strong> Support</p>
    </div>
</body>
</html>"""
        
        self.send_email(user_email, "Aman ga? - Payment Rejected ❌", email_body)
    
    def notify_fraud_flag(self, user_email: str, user_phone: str, action_taken: str):
        """Notify user when fraud is detected"""
        
        whatsapp_msg = f"""⚠️ *Account Alert*

Suspicious activity detected on your account.
Action Taken: {action_taken}

Contact support immediately if you believe this is an error."""
        
        if user_phone:
            self.send_whatsapp(user_phone, whatsapp_msg)
        
        email_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); padding: 20px; text-align: center;">
        <h1 style="color: white; margin: 0;">⚠️ Account Alert</h1>
    </div>
    <div style="padding: 20px;">
        <p>Suspicious activity has been detected on your account.</p>
        <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p style="margin: 0; color: #92400e;">
                <strong>Action Taken: {action_taken}</strong>
            </p>
        </div>
        <p>If you believe this is an error, please contact our support team immediately.</p>
        <p><strong style="color: #10b981;">Aman ga?</strong> Security Team</p>
    </div>
</body>
</html>"""
        
        self.send_email(user_email, "Aman ga? - Account Alert ⚠️", email_body)
    
    def notify_admin_new_payment(self, admin_email: str, payment_id: str, user_email: str, amount: int):
        """Notify admin of new payment requiring review"""
        
        subject = f"📋 New Payment for Review - Rp {amount:,}"
        
        email_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); padding: 20px; text-align: center;">
        <h1 style="color: white; margin: 0;">📋 New Payment for Review</h1>
    </div>
    <div style="padding: 20px;">
        <p>A new payment requires your review.</p>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Payment ID</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">{payment_id[:8]}...</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">User</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">{user_email}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #e5e7eb; font-weight: bold;">Amount</td>
                <td style="padding: 10px; border: 1px solid #e5e7eb;">Rp {amount:,}</td>
            </tr>
        </table>
        <div style="text-align: center; margin: 30px 0;">
            <a href="http://localhost:3000/admin" style="background: #4f46e5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block;">Review in Admin Panel</a>
        </div>
    </div>
</body>
</html>"""
        
        self.send_email(admin_email, subject, email_body)
    
    def log_notification(self, user_id: str, type: str, status: str, details: dict = None):
        """Log notification for audit trail"""
        
        notification_log = {
            "user_id": user_id,
            "type": type,
            "status": status,
            "details": details or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Log to console in mock mode
        if self.mock_mode:
            print(f"📝 [Notification Log] {type}: {status} for user {user_id}")
        
        return notification_log
