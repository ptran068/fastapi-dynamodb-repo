# app/services/event_service.py
from typing import List, Dict, Any, Optional
from app.repositories.event import EventRepository
from app.repositories.user_event import UserEventRepository # Import UserEventRepository
from app.apis.v1.schemas.event import EventCreate, EventUpdate
from app.models.event import Event
from app.core.exceptions import NotFoundException, BadRequestException

class EventService:
    def __init__(self, event_repo: EventRepository, user_event_repo: UserEventRepository): # Inject UserEventRepository
        self.event_repo = event_repo
        self.user_event_repo = user_event_repo # Store it

    async def create_event(self, event_data: EventCreate) -> Event:
        event_dict = event_data.model_dump()

        # Check for existing slug
        existing_event = await self.event_repo.get_by_slug(event_data.slug)
        if existing_event:
            raise BadRequestException(detail=f"Event with slug '{event_data.slug}' already exists.")

        # Ensure ownerId is in the hosts list
        if event_data.ownerId not in event_data.hosts:
            event_data.hosts.append(event_data.ownerId)
            event_dict['hosts'] = event_data.hosts # Update dict for consistency before saving

        created_event_data = await self.event_repo.create(event_dict)
        created_event = Event(**created_event_data)

        # --- NEW LOGIC: Create UserEvent for the owner as a host ---
        try:
            await self.user_event_repo.create_user_event(
                user_id=created_event.ownerId,
                event_id=created_event.id,
                role="host" # Or "owner" if you define that role in UserEventRole
            )
        except Exception as e:
            # Handle potential errors, e.g., if user_event already exists (unlikely here)
            # You might want to log this or consider rolling back the event creation if critical
            print(f"Warning: Could not create UserEvent for owner {created_event.ownerId} for event {created_event.id}: {e}")
        # -----------------------------------------------------------

        return created_event

    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        event_data = await self.event_repo.get_by_id(event_id)
        return Event(**event_data) if event_data else None

    async def get_event_by_slug(self, slug: str) -> Optional[Event]:
        event_data = await self.event_repo.get_by_slug(slug)
        return Event(**event_data) if event_data else None

    async def update_event(self, event_id: str, event_update: EventUpdate) -> Optional[Event]:
        updates = event_update.model_dump(exclude_unset=True)
        if not updates:
            return await self.get_event_by_id(event_id)

        # If hosts are updated, ensure ownerId remains a host (optional, based on desired strictness)
        # current_event = await self.get_event_by_id(event_id)
        # if current_event and 'hosts' in updates and current_event.ownerId not in updates['hosts']:
        #     updates['hosts'].append(current_event.ownerId)


        updated_event_data = await self.event_repo.update(event_id, updates)
        return Event(**updated_event_data) if updated_event_data else None

    async def delete_event(self, event_id: str) -> bool:
        # Consider deleting associated UserEvents here as well for cleanup
        return await self.event_repo.delete(event_id)

    async def list_events(self) -> List[Event]:
        events_data = await self.event_repo.query()
        return [Event(**data) for data in events_data]