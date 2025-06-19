from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from app.services.user import UserService
from app.apis.dependencies import get_user_service
from app.apis.v1.schemas.user import UserCreate, UserUpdate, UserFilter, PaginatedUsersResponse
from app.models.user import User
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return await user_service.create_user(user_create)
    except BadRequestException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get("/{user_id}", response_model=User)
async def get_user_endpoint(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user_endpoint(
    user_id: str,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    updated_user = await user_service.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or update failed")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    if not await user_service.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or deletion failed")
    return

@router.get("/", response_model=PaginatedUsersResponse)
async def filter_users_endpoint(
    company: Optional[str] = Query(None),
    job_title: Optional[str] = Query(None, alias="jobTitle"),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    min_events_hosted: Optional[int] = Query(None, ge=0),
    max_events_hosted: Optional[int] = Query(None, ge=0),
    min_events_attended: Optional[int] = Query(None, ge=0),
    max_events_attended: Optional[int] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    user_service: UserService = Depends(get_user_service)
):
    filters = UserFilter(
        company=company,
        jobTitle=job_title,
        city=city,
        state=state,
        email=email,
        min_events_hosted=min_events_hosted,
        max_events_hosted=max_events_hosted,
        min_events_attended=min_events_attended,
        max_events_attended=max_events_attended
    )
    return await user_service.filter_users(filters, page, page_size, sort_by, sort_order)