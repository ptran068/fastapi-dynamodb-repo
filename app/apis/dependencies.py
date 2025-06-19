# app/api/dependencies.py
from fastapi import Depends
from app.database.dynamodb_connector import get_db_client
from app.repositories.user import UserRepository
from app.repositories.event import EventRepository
from app.repositories.user_event import UserEventRepository
from app.services.user import UserService
from app.services.event import EventService
from app.services.email import EmailService
from app.services.analytics import AnalyticsService

def get_user_repository() -> UserRepository:
    return UserRepository(get_db_client())

def get_event_repository() -> EventRepository:
    return EventRepository(get_db_client())

def get_user_event_repository() -> UserEventRepository:
    return UserEventRepository(get_db_client())

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    user_event_repo: UserEventRepository = Depends(get_user_event_repository)
) -> UserService:
    return UserService(user_repo, user_event_repo)

def get_event_service(
    event_repo: EventRepository = Depends(get_event_repository),
    user_event_repo: UserEventRepository = Depends(get_user_event_repository) # Inject user_event_repo
) -> EventService:
    return EventService(event_repo, user_event_repo)

def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()

def get_email_service(analytics_service: AnalyticsService = Depends(get_analytics_service)) -> EmailService:
    return EmailService(analytics_service)


