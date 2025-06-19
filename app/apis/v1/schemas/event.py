from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.event import Event

class EventCreate(BaseModel):
    slug: str
    title: str
    description: Optional[str] = None
    startAt: datetime
    endAt: datetime
    venue: str
    maxCapacity: int
    ownerId: str
    hosts: List[str] = []

class EventUpdate(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    startAt: Optional[datetime] = None
    endAt: Optional[datetime] = None
    venue: Optional[str] = None
    maxCapacity: Optional[int] = None
    ownerId: Optional[str] = None
    hosts: Optional[List[str]] = None

class PaginatedEventsResponse(BaseModel):
    items: List[Event]
    total_count: int
    page: int
    page_size: int