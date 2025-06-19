from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.services.event import EventService
from app.apis.dependencies import get_event_service
from app.apis.v1.schemas.event import EventCreate, EventUpdate
from app.models.event import Event
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()

@router.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event_endpoint(
    event_create: EventCreate,
    event_service: EventService = Depends(get_event_service)
):
    try:
        return await event_service.create_event(event_create)
    except BadRequestException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{event_id}", response_model=Event)
async def get_event_endpoint(
    event_id: str,
    event_service: EventService = Depends(get_event_service)
):
    event = await event_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event

@router.put("/{event_id}", response_model=Event)
async def update_event_endpoint(
    event_id: str,
    event_update: EventUpdate,
    event_service: EventService = Depends(get_event_service)
):
    updated_event = await event_service.update_event(event_id, event_update)
    if not updated_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or update failed")
    return updated_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event_endpoint(
    event_id: str,
    event_service: EventService = Depends(get_event_service)
):
    if not await event_service.delete_event(event_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or deletion failed")
    return

@router.get("/", response_model=List[Event])
async def list_events_endpoint(
    event_service: EventService = Depends(get_event_service)
):
    return await event_service.list_events()