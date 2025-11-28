
from fastapi import FastAPI
from app.database.models import async_main
from app.api.models_api import users_api, events_api, tasks_api

app = FastAPI(title="Kislorod API")

app.include_router(users_api.router)
app.include_router(events_api.router)
app.include_router(tasks_api.router)

@app.on_event("startup")
async def on_startup():
    # Инициализация БД (создание базы/таблиц если нужно)
    try:
        await async_main()
    except Exception as e:
        # Логируйте ошибку; в среде докера/хоста возможно DB недоступна на старте
        print("DB init error:", e)