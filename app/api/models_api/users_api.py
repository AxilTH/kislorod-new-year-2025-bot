from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.api.deps import get_session, admin_auth

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    id: int
    first_name: str
    last_name: str
    score: int

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    score: Optional[int] = None

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    score: int

    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[UserOut])
async def get_all_users(session: AsyncSession = Depends(get_session)):
   q = select(User)
   res = await session.execute(q)
   return res.scalars().all()

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    # `id` in model is Telegram id (primary key)
    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_auth)])
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.scalar(select(User).where(User.id == payload.id))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    user = User(
        id=payload.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        score=payload.score,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserOut, dependencies=[Depends(admin_auth)])
async def update_user(user_id: int, payload: UserUpdate, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_data = payload.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(user, k, v)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_auth)])
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await session.delete(user)
    await session.commit()
    return None
