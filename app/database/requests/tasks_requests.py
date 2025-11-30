from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date as date_type, time

from app.database.models import Task, TaskCompletion, async_session

async def get_tasks_by_date(task_date: date_type) -> list[Task]:
    """Get all tasks that are active on a specific date."""
    async with async_session() as session:
        day_start = datetime.combine(task_date, time.min)
        day_end = datetime.combine(task_date, time.max)
        
        result = await session.execute(
            select(Task).where(
                Task.date_start <= day_end,
                Task.date_end >= day_start
            ).order_by(Task.type)  # Порядок: TF, AI, DISH (по алфавиту enum)
        )
        return result.scalars().all()

async def get_completed_tasks(user_id: int, task_date: date_type) -> list[Task]:
    """Get tasks that a user has completed on a specific date."""
    async with async_session() as session:
        day_start = datetime.combine(task_date, time.min)
        day_end = datetime.combine(task_date, time.max)
        
        result = await session.execute(
            select(Task)
            .join(TaskCompletion, Task.id == TaskCompletion.task_id)
            .where(TaskCompletion.user_id == user_id)
            .where(Task.date_start <= day_end, Task.date_end >= day_start)
            .order_by(Task.type)
        )
        return list(result.scalars().all())

async def get_current_task(user_id: int, task_date: date_type) -> Task | None:
    """Get the current task for user (first not completed task for today in order: TF -> AI -> DISH)."""
    async with async_session() as session:
        day_start = datetime.combine(task_date, time.min)
        day_end = datetime.combine(task_date, time.max)
        
        # Get all tasks for today in correct order
        all_tasks = await session.execute(
            select(Task).where(
                Task.date_start <= day_end,
                Task.date_end >= day_start
            ).order_by(Task.type)  # TF, AI, DISH
        )
        all_tasks = list(all_tasks.scalars().all())
        
        # Get completed tasks for today
        completed_tasks = await session.execute(
            select(TaskCompletion.task_id)
            .join(Task, Task.id == TaskCompletion.task_id)
            .where(TaskCompletion.user_id == user_id)
            .where(Task.date_start <= day_end, Task.date_end >= day_start)
        )
        completed_task_ids = set(completed_tasks.scalars().all())
        
        # Find first not completed task in order
        for task in all_tasks:
            if task.id not in completed_task_ids:
                return task
        
        return None  # All tasks completed

async def get_task_by_id(task_id: int) -> Task | None:
    async with async_session() as session:
        return await session.scalar(select(Task).where(Task.id == task_id))

async def mark_task_completed(user_id: int, task_id: int, awarded_points: int, user_answer: str) -> bool:
    """Mark task as completed. Returns True if successful, False if already completed."""
    async with async_session() as session:
        # Check if already completed
        existing = await session.scalar(
            select(TaskCompletion).where(
                TaskCompletion.user_id == user_id,
                TaskCompletion.task_id == task_id
            )
        )
        
        if existing:
            return False  # Already completed
        
        completion = TaskCompletion(
            user_id=user_id,
            task_id=task_id,
            awarded_points=awarded_points,
            user_answer=user_answer,
            timestamp=datetime.utcnow()
        )
        session.add(completion)
        try:
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False

async def update_user_score(user_id: int, points_to_add: int) -> None:
    """Update user's total score."""
    from app.database.models import User
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user:
            user.score += points_to_add
            await session.commit()

async def get_tasks_status(user_id: int, task_date: date_type) -> dict:
    """Get status of all tasks for today with completion info."""
    async with async_session() as session:
        day_start = datetime.combine(task_date, time.min)
        day_end = datetime.combine(task_date, time.max)
        
        # Get all tasks for today in order
        all_tasks_result = await session.execute(
            select(Task).where(
                Task.date_start <= day_end,
                Task.date_end >= day_start
            ).order_by(Task.type)
        )
        all_tasks = list(all_tasks_result.scalars().all())
        
        # Get completed task IDs
        completed_result = await session.execute(
            select(TaskCompletion.task_id)
            .join(Task, Task.id == TaskCompletion.task_id)
            .where(TaskCompletion.user_id == user_id)
            .where(Task.date_start <= day_end, Task.date_end >= day_start)
        )
        completed_ids = set(completed_result.scalars().all())
        
        # Build status
        task_types_order = ['TF', 'AI', 'DISH']
        status = {}
        
        for task_type in task_types_order:
            tasks_of_type = [t for t in all_tasks if t.type == task_type]
            if tasks_of_type:
                task = tasks_of_type[0]  # Assuming one task per type per day
                status[task_type] = {
                    'task': task,
                    'completed': task.id in completed_ids,
                    'current': False
                }
        
        # Mark current task (first not completed)
        for task_type in task_types_order:
            if task_type in status and not status[task_type]['completed']:
                status[task_type]['current'] = True
                break
        
        return status