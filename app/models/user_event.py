from pydantic import BaseModel, Field
from datetime import datetime

class UserEvent(BaseModel):
    userId: str
    eventId: str
    role: str
    registeredAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())