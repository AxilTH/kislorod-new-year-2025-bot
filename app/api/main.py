import logging

from fastapi import FastAPI
from app.database.models import engine
from app.api.models_api import users_api, events_api, tasks_api
from sqlalchemy import text

logger = logging.getLogger(__name__)

app = FastAPI(title="Kislorod API")

app.include_router(users_api.router)
app.include_router(events_api.router)
app.include_router(tasks_api.router)

@app.on_event("startup")
async def on_startup():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified for API")
    except Exception as e:
        logger.error("Failed to connect to database: %s", e, exc_info=True)

@app.on_event("shutdown")
async def on_shutdown():
    """Закрытие соединений с БД при остановке API"""
    from app.database.models import engine
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed")