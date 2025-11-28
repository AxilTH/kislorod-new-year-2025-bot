from aiogram import Router

from .registration import router as registration_router
from .checkin import router as checkin_router
from .profile import router as profile_router
from .help import router as help_router
from .stats import router as stats_router
from .events import router as events_router
from .message import router as message_router
from .tasks import router as tasks_router

router = Router()
router.include_router(registration_router)
router.include_router(checkin_router)
router.include_router(events_router)
router.include_router(profile_router)
router.include_router(stats_router)
router.include_router(help_router)
router.include_router(message_router)
router.include_router(tasks_router)