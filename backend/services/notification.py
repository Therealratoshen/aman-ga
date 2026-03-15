from database import supabase
from datetime import datetime
import requests
import os

class NotificationService:
    """Notification service for WhatsApp, Email, and Push notifications"""
    
    def __init__(self):
        self.whatsapp_api_key = os.getenv("WHATSAPP_API_KEY", "")
        self.whatsapp_api_url = os.getenv("WHATSAPP_API_URL", "")
        self.email_api_key = os.getenv("EMAIL_API_KEY", "")
    
    def send_whatsapp(self, phone: str, message: str) -> dict:
        """Send WhatsApp message"""
        
        if not self.whatsapp_api_key:
            # Log notification for development
            print(f"[WhatsApp] To: {phone}, Message: {message}")
            return {"success": True, "mock": True}
        
        try:
            response = requests.post(
                self.whatsapp_api_url,
                headers={
                    "Authorization": f"Bearer {self.whatsapp_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "to": phone,
                    "message": message
                }
            )
            
            return {"success": response.status_code == 200, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_email(self, email: str, subject: str, body: str) -> dict:
        """Send email notification"""
        
        if not self.email_api_key:
            # Log notification for development
            print(f"[Email] To: {email}, Subject: {subject}, Body: {body}")
            return {"success": True, "mock": True}
        
        try:
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {self.email_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{"to": [{"email": email}]}],
                    "from": {"email": "noreply@amanga.id", "name": "Aman ga?"},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": body}]
                }
            )
            
            return {"success": response.status_code == 202, "response": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def notify_payment_uploaded(self, user_email: str, user_phone: str, payment_id: str, service_type: str, amount: int, status: str):
        """Notify user when payment proof is uploaded"""
        
        # WhatsApp notification
        message = f"""
🔔 *Aman ga? - Payment Received*

Payment ID: {payment_id[:8]}...
Service: {service_type}
Amount: Rp {amount:,}
Status: {status}

{'✅ Auto-approved! Service activated.' if status == 'AUTO_APPROVED' else '⏳ Waiting for verification (5-30 minutes)'}

Thank you for using Aman ga?
        """.strip()
        
        if user_phone:
            self.send_whatsapp(user_phone, message)
        
        # Email notification
        email_body = f"""
<html>
<body>
    <h2>🔔 Payment Received</h2>
    <p>Thank you for your payment!</p>
    <table>
        <tr><td>Payment ID:</td><td>{payment_id[:8]}...</td></tr>
        <tr><td>Service:</td><td>{service_type}</td></tr>
        <tr><td>Amount:</td><td>Rp {amount:,}</td></tr>
        <tr><td>Status:</td><td>{status}</td></tr>
    </table>
    <p>{'✅ Your service has been auto-approved and activated!' if status == 'AUTO_APPROVED' else '⏳ Your payment is being verified. You will be notified once approved.'}</p>
    <p>Thank you for using <strong>Aman ga?</strong></p>
</body>
</html>
        """
        
        self.send_email(user_email, f"Aman ga? - Payment Received ({status})", email_body)
    
    def notify_payment_approved(self, user_email: str, user_phone: str, payment_id: str, service_type: str):
        """Notify user when payment is approved"""
        
        # WhatsApp notification
        message = f"""
✅ *Payment Approved!*

Payment ID: {payment_id[:8]}...
Service: {service_type}

Your service credit has been activated. You can now use it in your dashboard.

Thank you for using Aman ga?
        """.strip()
        
        if user_phone:
            self.send_whatsapp(user_phone, message)
        
        # Email notification
        email_body = f"""
<html>
<body>
    <h2>✅ Payment Approved</h2>
    <p>Great news! Your payment has been approved.</p>
    <table>
        <tr><td>Payment ID:</td><td>{payment_id[:8]}...</td></tr>
        <tr><td>Service:</td><td>{service_type}</td></tr>
    </table>
    <p>Your service credit has been activated. Login to your dashboard to use it.</p>
    <p>Thank you for using <strong>Aman ga?</strong></p>
</body>
</html>
        """
        
        self.send_email(user_email, "Aman ga? - Payment Approved ✅", email_body)
    
    def notify_payment_rejected(self, user_email: str, user_phone: str, payment_id: str, reason: str):
        """Notify user when payment is rejected"""
        
        # WhatsApp notification
        message = f"""
❌ *Payment Rejected*

Payment ID: {payment_id[:8]}...
Reason: {reason}

Please check your payment proof and resubmit. Contact support if you need help.
        """.strip()
        
        if user_phone:
            self.send_whatsapp(user_phone, message)
        
        # Email notification
        email_body = f"""
<html>
<body>
    <h2>❌ Payment Rejected</h2>
    <p>We're sorry, but your payment could not be approved.</p>
    <table>
        <tr><td>Payment ID:</td><td>{payment_id[:8]}...</td></tr>
        <tr><td>Reason:</td><td>{reason}</td></tr>
    </table>
    <p>Please check your payment proof and resubmit. If you believe this is an error, contact our support team.</p>
    <p><strong>Aman ga?</strong> Support</p>
</body>
</html>
        """
        
        self.send_email(user_email, "Aman ga? - Payment Rejected ❌", email_body)
    
    def notify_fraud_flag(self, user_email: str, user_phone: str, action_taken: str):
        """Notify user when fraud is detected"""
        
        # WhatsApp notification
        message = f"""
⚠️ *Account Alert*

Suspicious activity detected on your account.
Action Taken: {action_taken}

Contact support immediately if you believe this is an error.
        """.strip()
        
        if user_phone:
            self.send_whatsapp(user_phone, message)
        
        # Email notification
        email_body = f"""
<html>
<body>
    <h2>⚠️ Account Alert</h2>
    <p>Suspicious activity has been detected on your account.</p>
    <p><strong>Action Taken:</strong> {action_taken}</p>
    <p>If you believe this is an error, please contact our support team immediately.</p>
    <p><strong>Aman ga?</strong> Security Team</p>
</body>
</html>
        """
        
        self.send_email(user_email, "Aman ga? - Account Alert ⚠️", email_body)
    
    def notify_admin_new_payment(self, admin_email: str, payment_id: str, user_email: str, amount: int):
        """Notify admin of new payment requiring review"""
        
        message = f"""
📋 *New Payment for Review*

Payment ID: {payment_id[:8]}...
User: {user_email}
Amount: Rp {amount:,}

Please review in the admin dashboard.
        """
        
        # Send to admin
        self.send_email(admin_email, "Aman ga? - New Payment for Review", message)
    
    def log_notification(self, user_id: str, type: str, status: str, details: dict = None):
        """Log notification for audit trail"""
        
        notification_log = {
            "user_id": user_id,
            "type": type,
            "status": status,
            "details": details or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Note: Create notifications table if needed
        # supabase.table("notifications").insert(notification_log).execute()
        
        return notification_log
