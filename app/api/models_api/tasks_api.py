from typing import List, Optional
from datetime import date as date_type, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Task
from app.api.deps import get_session, admin_auth

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    date_start: datetime
    date_end: datetime
    type: str  # 'TF', 'AI', or 'DISH'
    description: Optional[str] = None
    correct_answer: str  # 'true'/'false' for TF, text answer for AI/DISH
    score: int

class TaskUpdate(BaseModel):
    date_start: Optional[datetime] = None
    date_end: Optional[datetime] = None
    type: Optional[str] = None
    description: Optional[str] = None
    correct_answer: Optional[str] = None
    score: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    date_start: datetime
    date_end: datetime
    type: str
    description: Optional[str]
    correct_answer: str
    score: int

    model_config = {"from_attributes": True}

@router.get("", response_model=List[TaskOut], dependencies=[Depends(admin_auth)])
async def get_all_tasks(session: AsyncSession = Depends(get_session)):
    """Get all tasks"""
    result = await session.execute(select(Task))
    return result.scalars().all()

@router.get("/{task_id}", response_model=TaskOut, dependencies=[Depends(admin_auth)])
async def get_task_by_id(task_id: int, session: AsyncSession = Depends(get_session)):
    """Get a single task by its id (admin only)"""
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_auth)])
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(get_session)):
    """Create a new task (admin only)"""
    # Validate type
    if payload.type not in ['TF', 'AI', 'DISH']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task type. Must be one of: TF, AI, DISH"
        )
    
    task = Task(
        date_start=payload.date_start,
        date_end=payload.date_end,
        type=payload.type,
        description=payload.description,
        correct_answer=payload.correct_answer,
        score=payload.score
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.put("/{task_id}", response_model=TaskOut, dependencies=[Depends(admin_auth)])
async def update_task(task_id: int, payload: TaskUpdate, session: AsyncSession = Depends(get_session)):
    """Update a task (admin only)"""
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Validate type if provided
    if payload.type and payload.type not in ['TF', 'AI', 'DISH']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid task type. Must be one of: TF, AI, DISH"
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_auth)])
async def delete_task(task_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a task (admin only)"""
    task = await session.scalar(select(Task).where(Task.id == task_id))
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    await session.delete(task)
    await session.commit()
    return None
