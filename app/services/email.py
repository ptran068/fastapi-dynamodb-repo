from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings
from typing import List, Dict, Any
from app.models.user import User
import asyncio
from app.services.analytics import AnalyticsService # Import

class EmailService:
    def __init__(self, analytics_service: AnalyticsService): # Add analytics_service as dependency
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        self.sender_email = settings.SENDGRID_SENDER_EMAIL
        self.analytics_service = analytics_service # Store it

    async def send_single_email(self, recipient_email: str, subject: str, html_content: str) -> bool:
        message = Mail(
            from_email=self.sender_email,
            to_emails=recipient_email,
            subject=subject,
            html_content=html_content
        )
        try:
            response = await asyncio.to_thread(self.sg.send, message)
            success = 200 <= response.status_code < 300
            await self.analytics_service.record_email_send_status( # Record status
                user_id="unknown_if_not_fetched", # You'd pass actual user_id here
                email=recipient_email,
                subject=subject,
                status="sent" if success else "failed",
                error_message=str(response.body) if not success else None
            )
            return success
        except Exception as e:
            await self.analytics_service.record_email_send_status( # Record status on exception
                user_id="unknown_if_not_fetched", # You'd pass actual user_id here
                email=recipient_email,
                subject=subject,
                status="failed",
                error_message=str(e)
            )
            return False

    async def send_bulk_emails(self, users: List[User], subject: str, template_name: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        sent_count = 0
        failed_count = 0
        failed_recipients = []

        html_content = f"<html><body><h1>{subject}</h1><p>Dear user,</p><p>This is a test email.</p><p>{template_data.get('message', '')}</p></body></html>"

        tasks = []
        for user in users:
            user_specific_html = html_content.replace("Dear user", f"Dear {user.firstName}")
            # Pass user ID to send_single_email if available for analytics
            tasks.append(self.send_single_email(user.email, subject, user_specific_html)) # Simplified for this example, user_id not passed

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if result is True:
                sent_count += 1
            else:
                failed_count += 1
                failed_recipients.append(users[i].email)

        return {
            "sent_count": sent_count,
            "failed_count": failed_count,
            "failed_recipients": failed_recipients
        }