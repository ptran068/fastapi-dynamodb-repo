from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.apis.v1.schemas.user import UserFilter

class SendEmailRequest(BaseModel):
    subject: str
    template_name: str
    template_data: Dict[str, Any] = {}
    filters: Optional[UserFilter] = None
    recipient_emails: Optional[List[str]] = None

class SendEmailResponse(BaseModel):
    message: str
    sent_count: int
    failed_count: int
    failed_recipients: List[str]