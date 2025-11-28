from typing import AsyncGenerator, Optional
from fastapi import Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import async_session
import config

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def admin_auth(authorization: Optional[str] = Header(None)):
    # Простая проверка заголовка Authorization: Bearer <TOKEN>
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No auth token")
    token = authorization.split(" ", 1)[1]
    if token != getattr(config, "ADMIN_TOKEN", None):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")
    return True