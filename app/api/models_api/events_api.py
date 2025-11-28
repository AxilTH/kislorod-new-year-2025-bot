from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Event
from app.api.deps import get_session, admin_auth

router = APIRouter(prefix="/events", tags=["events"])

class EventCreate(BaseModel):
    title: str
    date: datetime
    score: int = Field(0, ge=0)
    code: str

class EventUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[datetime] = None
    score: Optional[int] = None
    code: Optional[str] = None

class EventOut(BaseModel):
    id: int
    title: str
    date: datetime
    score: int
    code: str

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=List[EventOut], dependencies=[Depends(admin_auth)])
async def get_all_events(session: AsyncSession = Depends(get_session)):
   q = select(Event).order_by(Event.date)
   res = await session.execute(q)
   return res.scalars().all()

@router.get("/{event_id}", response_model=EventOut, dependencies=[Depends(admin_auth)])
async def get_event(event_id: int, session: AsyncSession = Depends(get_session)):
   event = await session.scalar(select(Event).where(Event.id == event_id))
   if not event:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
   return event

@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_auth)])
async def create_event(payload: EventCreate, session: AsyncSession = Depends(get_session)):
   existing = await session.scalar(select(Event).where(Event.code == payload.code))
   if existing:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event already exists")
   event = Event(
      title=payload.title,
      date=payload.date,
      score=payload.score,
      code=payload.code,
   )
   session.add(event)
   await session.commit()
   await session.refresh(event)
   return event

@router.put("/{event_id}", response_model=EventOut, dependencies=[Depends(admin_auth)])
async def update_event(event_id: int, payload: EventUpdate, session: AsyncSession = Depends(get_session)):
   event = await session.scalar(select(Event).where(Event.id == event_id))
   if not event:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
   data = payload.dict(exclude_unset=True)
   for k, v in data.items():
       setattr(event, k, v)
   session.add(event)
   await session.commit()
   await session.refresh(event)
   return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_auth)])
async def delete_event(event_id: int, session: AsyncSession = Depends(get_session)):
   event = await session.scalar(select(Event).where(Event.id == event_id))
   if not event:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
   await session.delete(event)
   await session.commit()
   return None