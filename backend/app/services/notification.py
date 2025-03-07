from typing import Dict, List, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aioredis
import json
from loguru import logger
import asyncio
from datetime import datetime

from app.core.config import settings
from app.db.models import Alert, User

class NotificationService:
    def __init__(self):
        self.redis_pool = None
        self.connected = False
    
    async def connect(self):
        """
        Connect to Redis for pub/sub messaging
        """
        if not self.connected:
            try:
                self.redis_pool = await aioredis.create_redis_pool(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
                )
                self.connected = True
                logger.info("Connected to Redis for notifications")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self.connected = False
    
    async def disconnect(self):
        """
        Disconnect from Redis
        """
        if self.connected and self.redis_pool:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()
            self.connected = False
            logger.info("Disconnected from Redis")
    
    async def publish_alert(self, alert: Alert) -> bool:
        """
        Publish alert to Redis for real-time notifications
        """
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            logger.error("Cannot publish alert: not connected to Redis")
            return False
        
        try:
            # Create alert message
            alert_message = {
                "id": alert.id,
                "patient_id": alert.patient_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "created_at": alert.created_at.isoformat() if alert.created_at else datetime.now().isoformat(),
                "status": alert.status
            }
            
            # Create channel based on alert severity
            channel = f"alerts:severity:{alert.severity}"
            
            # Publish to severity-specific channel
            await self.redis_pool.publish(channel, json.dumps(alert_message))
            
            # Also publish to patient-specific channel
            patient_channel = f"alerts:patient:{alert.patient_id}"
            await self.redis_pool.publish(patient_channel, json.dumps(alert_message))
            
            # Also publish to all-alerts channel
            await self.redis_pool.publish("alerts:all", json.dumps(alert_message))
            
            logger.info(f"Published alert {alert.id} to Redis")
            return True
        
        except Exception as e:
            logger.error(f"Failed to publish alert: {str(e)}")
            return False
    
    async def send_email_alert(
        self, 
        recipient_email: str, 
        subject: str, 
        message: str, 
        html_message: Optional[str] = None
    ) -> bool:
        """
        Send an email alert
        """
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured, skipping email alert")
            return False
        
        try:
            # Create email message
            email = MIMEMultipart("alternative")
            email["From"] = settings.SMTP_USER
            email["To"] = recipient_email
            email["Subject"] = subject
            
            # Attach plain text and HTML versions
            email.attach(MIMEText(message, "plain"))
            if html_message:
                email.attach(MIMEText(html_message, "html"))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, recipient_email, email.as_string())
            
            logger.info(f"Sent email alert to {recipient_email}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
            return False
    
    async def send_sms_alert(self, phone_number: str, message: str) -> bool:
        """
        Send an SMS alert (placeholder - would integrate with Twilio or similar service)
        """
        # This is a placeholder for SMS integration
        logger.info(f"Would send SMS to {phone_number}: {message}")
        return True
    
    def format_email_html(self, alert: Alert, patient_data: Dict[str, Any]) -> str:
        """
        Format HTML email content for sepsis alert
        """
        patient_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}".strip()
        mrn = patient_data.get('mrn', 'Unknown')
        
        severity_color = "#000000"
        if alert.severity == 5:
            severity_color = "#FF0000"  # Red for critical
        elif alert.severity == 4:
            severity_color = "#FF6600"  # Orange for high
        elif alert.severity == 3:
            severity_color = "#FFCC00"  # Yellow for medium
        elif alert.severity == 2:
            severity_color = "#33CC33"  # Green for low
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #003366; color: white; padding: 10px; text-align: center; }}
                .alert-box {{ border: 2px solid {severity_color}; padding: 15px; margin-top: 20px; }}
                .alert-title {{ color: {severity_color}; font-weight: bold; font-size: 18px; }}
                .patient-info {{ background-color: #f0f0f0; padding: 10px; margin-top: 20px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Sepsis Alert Notification</h1>
                </div>
                <div class="alert-box">
                    <div class="alert-title">{alert.alert_type.replace('_', ' ')}</div>
                    <p>{alert.message}</p>
                </div>
                <div class="patient-info">
                    <h3>Patient Information</h3>
                    <p><strong>Name:</strong> {patient_name}</p>
                    <p><strong>MRN:</strong> {mrn}</p>
                    <p><strong>Alert Generated:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S') if alert.created_at else 'N/A'}</p>
                </div>
                <div>
                    <h3>Required Action</h3>
                    <p>Please review this patient's status as soon as possible and update the alert status in the Sepsis Management System.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Sepsis Management System. Please do not reply to this email.</p>
                    <p>If you have any questions, please contact IT support.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def notify_users_of_alert(
        self, 
        alert: Alert, 
        patient_data: Dict[str, Any],
        users: List[User]
    ) -> Dict[str, Any]:
        """
        Send notifications to multiple users about an alert
        """
        notification_results = {
            "email_sent": [],
            "email_failed": [],
            "sms_sent": [],
            "sms_failed": [],
            "published_to_redis": False
        }
        
        # Publish to Redis for real-time updates
        redis_result = await self.publish_alert(alert)
        notification_results["published_to_redis"] = redis_result
        
        # Process each user
        for user in users:
            # Skip inactive users
            if not user.is_active:
                continue
            
            # Prepare email content
            subject = f"SEPSIS ALERT: {alert.alert_type.replace('_', ' ')} - Severity {alert.severity}"
            message = alert.message
            html_message = self.format_email_html(alert, patient_data)
            
            # Send email if user has an email
            if user.email:
                email_sent = await self.send_email_alert(user.email, subject, message, html_message)
                if email_sent:
                    notification_results["email_sent"].append(user.id)
                else:
                    notification_results["email_failed"].append(user.id)
        
        return notification_results