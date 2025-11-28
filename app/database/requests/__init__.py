from .users_requests import (
    is_user_registered,
    get_all_users,
    get_user_by_tg_id,
    create_user,
)

from .events_requests import (
    visited_events,
    get_event_by_id,
    get_all_events,
    create_event,
    mark_attendance,
)

from .tasks_requests import (
   get_tasks_by_date,
   get_completed_tasks,
   get_current_task,
   get_task_by_id,
   mark_task_completed,
   update_user_score,
   get_tasks_status,
)

__all__ = [
   'is_user_registered',
   'get_all_users',
   'get_user_by_tg_id',
   'create_user',
   'visited_events',
   'get_event_by_id',
   'get_all_events',
   'create_event',
   'mark_attendance',
   'get_tasks_by_date',
   'get_completed_tasks',
   'get_current_task',
   'get_task_by_id',
   'mark_task_completed',
   'update_user_score',
   'get_tasks_status'
]
