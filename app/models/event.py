# app/models/event_model.py
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str
    title: str
    description: Optional[str] = None
    startAt: datetime
    endAt: datetime
    venue: str
    maxCapacity: int
    ownerId: str
    hosts: List[str] = []
    createdAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.utcnow().isoformat())