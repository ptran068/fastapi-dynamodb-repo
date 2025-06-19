from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user import UserService
from app.services.email import EmailService
from app.apis.dependencies import get_user_service, get_email_service
from app.apis.v1.schemas.email import SendEmailRequest, SendEmailResponse
from app.models.user import User
import uuid

router = APIRouter()

@router.post("/send-emails", response_model=SendEmailResponse, status_code=status.HTTP_200_OK)
async def send_emails_endpoint(
    request: SendEmailRequest,
    user_service: UserService = Depends(get_user_service),
    email_service: EmailService = Depends(get_email_service)
):
    users_to_email = []
    if request.recipient_emails:
        # Placeholder: In a real app, you might fetch user objects if templating requires more than just email
        # For simplicity, if explicit emails are given, create dummy user objects for bulk sending
        users_to_email = [
            User(email=email, firstName=email.split('@')[0], lastName="", id=str(uuid.uuid4()), phoneNumber="")
            for email in request.recipient_emails
        ]
    elif request.filters:
        paginated_response = await user_service.filter_users(request.filters, page=1, page_size=10000)
        users_to_email = paginated_response.items
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'recipient_emails' or 'filters' must be provided."
        )

    if not users_to_email:
        return SendEmailResponse(
            message="No users found to send emails to based on criteria.",
            sent_count=0,
            failed_count=0,
            failed_recipients=[]
        )

    result = await email_service.send_bulk_emails(
        users=users_to_email,
        subject=request.subject,
        template_name=request.template_name,
        template_data=request.template_data
    )

    return SendEmailResponse(
        message="Email sending process initiated.",
        sent_count=result["sent_count"],
        failed_count=result["failed_count"],
        failed_recipients=result["failed_recipients"]
    )