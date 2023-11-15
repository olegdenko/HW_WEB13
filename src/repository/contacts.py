from fastapi import HTTPException
from datetime import timedelta, datetime
from typing import List
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import (
    ContactModel,
    ContactUpdate,
    ContactStatusUpdate,
    ContactResponse,
)


async def get_contact(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()


async def get_upcoming_birthdays(db: Session) -> List[ContactResponse]:
    today = datetime.now()
    end_date = today + timedelta(days=7)
    contacts = (
        db.query(Contact)
        .filter(Contact.born_date >= today, Contact.born_date <= end_date)
        .all()
    )
    return [
        ContactResponse(
            id=contact.id,
            name=contact.name,
            last_name=contact.last_name,
            e_mail=contact.e_mail,
            phone_number=contact.phone_number,
            born_date=contact.born_date,
            description=contact.description,
        )
        for contact in contacts
    ]


async def search_contacts(
    name: str, last_name: str, e_mail: str, db: Session
) -> Contact:
    query = db.query(Contact)

    if name:
        query = query.filter(Contact.name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if e_mail:
        query = query.filter(Contact.e_mail.ilike(f"%{e_mail}%"))

    contacts = query.all()
    if name and last_name:
        contacts = [
            contact
            for contact in contacts
            if contact.name.lower() == name.lower()
            and contact.last_name.lower() == last_name.lower()
        ]

    if last_name and e_mail:
        contacts = [
            contact
            for contact in contacts
            if contact.last_name.lower() == last_name.lower()
            and contact.e_mail.lower() == e_mail.lower()
        ]

    return contacts


async def create_contact(body: ContactModel, db: Session) -> ContactResponse:
    try:
        contact = Contact(
            name=body.name,
            last_name=body.last_name,
            e_mail=body.e_mail,
            phone_number=body.phone_number,
            born_date=body.born_date,
            description=body.description,
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        return ContactResponse(
            id=contact.id,
            name=contact.name,
            last_name=contact.last_name,
            e_mail=contact.e_mail,
            phone_number=contact.phone_number,
            born_date=contact.born_date,
            description=contact.description,
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=409, detail="Conflict: Something went wrong")


async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(
    contact_id: int, body: ContactUpdate, db: Session
) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.name = (body.name,)
        contact.last_name = (body.last_name,)
        contact.e_mail = (body.e_mail,)
        contact.phone_number = (body.phone_number,)
        contact.born_date = (body.born_date,)
        contact.description = (body.description,)
        db.commit()
    return contact


async def update_status_contact(
    contact_id: int, body: ContactStatusUpdate, db: Session
) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.done = body.done
        db.commit()
    return contact
