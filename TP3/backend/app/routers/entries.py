import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional
from app.database import get_db
from app.models.entry import Entry, CategoryEnum
from app.models.user import User
from app.schemas.entry import EntryCreate, EntryRead
from app.auth.deps import get_current_user

router = APIRouter(prefix="/api/entries", tags=["entries"])

@router.get("", response_model=list[EntryRead])
def list_entries(
    category: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Entry).filter(Entry.user_id == current_user.id)
    if category:
        q = q.filter(Entry.category == CategoryEnum[category])
    if year:
        q = q.filter(extract("year", Entry.date) == year)
    if month:
        q = q.filter(extract("month", Entry.date) == month)
    return q.order_by(Entry.date.desc()).all()

@router.post("", response_model=EntryRead, status_code=201)
def create_entry(
    body: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = Entry(user_id=current_user.id, **body.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/{entry_id}", response_model=EntryRead)
def get_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.put("/{entry_id}", response_model=EntryRead)
def update_entry(
    entry_id: uuid.UUID,
    body: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    for field, value in body.model_dump().items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{entry_id}", status_code=204)
def delete_entry(
    entry_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(Entry).filter(Entry.id == entry_id, Entry.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
