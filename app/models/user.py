from typing import Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firstName: str
    lastName: str
    phoneNumber: str
    email: str
    avatar: Optional[str] = None
    gender: Optional[str] = None
    jobTitle: Optional[str] = None
    company: Optional[str] = None # should be company ID
    city: Optional[str] = None
    state: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())