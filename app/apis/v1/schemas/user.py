from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.user import User

class UserCreate(BaseModel):
    firstName: str
    lastName: str
    phoneNumber: str
    email: str
    avatar: Optional[str] = None
    gender: Optional[str] = None
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class UserUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class UserFilter(BaseModel):
    company: Optional[str] = None
    jobTitle: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    min_events_hosted: Optional[int] = Field(None, ge=0)
    max_events_hosted: Optional[int] = Field(None, ge=0)
    min_events_attended: Optional[int] = Field(None, ge=0)
    max_events_attended: Optional[int] = Field(None, ge=0)

class PaginatedUsersResponse(BaseModel):
    items: List[User]
    total_count: int
    page: int
    page_size: int