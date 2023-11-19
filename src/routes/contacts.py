from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.models import Role, User
from src.database.db import get_db
from src.schemas import (
    ContactModel,
    ContactUpdate,
    ContactResponse,
)
from src.repository import contacts as repository_contacts
from src.services.auth import auth_servise
from src.services.roles import RoleAccess


router = APIRouter(prefix="/contacts", tags=["contacts"])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get(
    "/",
    response_model=List[ContactResponse],
    dependencies=[
        Depends(allowed_operation_get),
        Depends(RateLimiter(times=10, seconds=60)),
    ],
    description="No more than 10 requests per minute",
)
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(allowed_operation_get)],
)
async def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get(
    "/search_by/",
    response_model=List[ContactResponse],
    dependencies=[Depends(allowed_operation_get)],
)
async def search_contact(
    name: str = None,
    last_name: str = None,
    e_mail: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    contact = await repository_contacts.search_contacts(name, last_name, e_mail, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.get(
    "/upcoming_birthdays/",
    response_model=List[ContactResponse],
    dependencies=[Depends(allowed_operation_get)],
)
async def read_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    contacts = await repository_contacts.get_upcoming_birthdays(db)
    if contacts is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contacts not found"
        )
    return contacts


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allowed_operation_create)],
)
async def create_contact(
    body: ContactModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    return await repository_contacts.create_contact(body, db)


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(allowed_operation_update)],
    description="Only moderator and admin",
)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete(
    "/{contact_id}",
    response_model=ContactResponse,
    dependencies=[Depends(allowed_operation_remove)],
)
async def remove_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_servise.get_current_user),
):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
