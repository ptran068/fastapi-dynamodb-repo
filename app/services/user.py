from typing import List, Dict, Any, Optional
from app.repositories.user import UserRepository
from app.repositories.user_event import UserEventRepository
from app.apis.v1.schemas.user import UserCreate, UserUpdate, UserFilter, PaginatedUsersResponse
from app.models.user import User
from app.core.exceptions import NotFoundException, BadRequestException
import math

class UserService:
    def __init__(self, user_repo: UserRepository, user_event_repo: UserEventRepository):
        self.user_repo = user_repo
        self.user_event_repo = user_event_repo

    async def create_user(self, user_data: UserCreate) -> User:
        user_dict = user_data.model_dump()
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise BadRequestException(detail=f"User with email '{user_data.email}' already exists.")
        created_user = await self.user_repo.create(user_dict)
        return User(**created_user)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        user_data = await self.user_repo.get_by_id(user_id)
        return User(**user_data) if user_data else None

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        updates = user_update.model_dump(exclude_unset=True)
        if not updates:
            return await self.get_user_by_id(user_id) # No updates provided

        updated_user_data = await self.user_repo.update(user_id, updates)
        return User(**updated_user_data) if updated_user_data else None

    async def delete_user(self, user_id: str) -> bool:
        return await self.user_repo.delete(user_id)

    async def filter_users(
        self,
        filters: UserFilter,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> PaginatedUsersResponse:
        # Step 1: Get all users (this is a full table scan from user_repo.query())
        all_users_data = await self.user_repo.query() # Remember: This is a SCAN operation

        # Initialize the list to be filtered
        current_filtered_users = all_users_data

        if filters.email is not None:
            target_email_lower = filters.email.lower()
            current_filtered_users = [
                user_data for user_data in current_filtered_users
                if user_data.get('email', '').lower() == target_email_lower
            ]

        if filters.city is not None:
            target_city_lower = filters.city.lower()
            current_filtered_users = [
                user_data for user_data in current_filtered_users
                if user_data.get('city', '').lower() == target_city_lower
            ]

        if filters.company is not None:
            company = filters.company.lower()
            current_filtered_users = [
                user_data for user_data in current_filtered_users
                if user_data.get('company', '').lower() == company
            ]

        final_filtered_users = []
        for user_data in current_filtered_users: # Iterate over the potentially pre-filtered list
            user_id = user_data.get('id')
            hosted_events = await self.user_event_repo.get_events_for_user(user_id, role="host")
            attended_events = await self.user_event_repo.get_events_for_user(user_id, role="participant")

            hosted_count = len(hosted_events)
            attended_count = len(attended_events)

            match_hosted = True
            if filters.min_events_hosted is not None and hosted_count < filters.min_events_hosted:
                match_hosted = False
            if filters.max_events_hosted is not None and hosted_count > filters.max_events_hosted:
                match_hosted = False

            match_attended = True
            if filters.min_events_attended is not None and attended_count < filters.min_events_attended:
                match_attended = False
            if filters.max_events_attended is not None and attended_count > filters.max_events_attended:
                match_attended = False

            if match_hosted and match_attended:
                final_filtered_users.append(user_data) # Use a new list to avoid modifying in place incorrectly

        # Step 4: Apply sorting
        if sort_by:
            # Ensure sort_by attribute exists and is comparable, or provide default
            final_filtered_users.sort(key=lambda x: x.get(sort_by, ''), reverse=(sort_order == "desc"))

        # Step 5: Apply pagination
        total_count = len(final_filtered_users)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_users_data = final_filtered_users[start_index:end_index]

        users = [User(**data) for data in paginated_users_data]

        return PaginatedUsersResponse(
            items=users,
            total_count=total_count,
            page=page,
            page_size=page_size
        )