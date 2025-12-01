import logging

from sqlalchemy import Integer, BigInteger, String, DateTime, Date
from sqlalchemy import Column, Enum, ForeignKey, UniqueConstraint, func, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import DEFAULT_DB_URL, TARGET_DB_URL

logger = logging.getLogger(__name__)

def _get_admin_db_url() -> str:
    """
    Return a connection string that points to an existing database
    (usually the default `postgres`) so we can create the target DB
    if it is missing. Falls back to TARGET_DB_URL with the database
    name swapped to `postgres` when DEFAULT_DB_URL is not provided.
    """
    if DEFAULT_DB_URL:
        return DEFAULT_DB_URL

    target_url = make_url(TARGET_DB_URL)
    if not target_url.database:
        raise RuntimeError("TARGET_DB_URL must include database name")

    admin_url = target_url.set(database="postgres")
    return admin_url.render_as_string(hide_password=False)

async def create_database_if_not_exists() -> None:
    """
    Ensure the database referenced in TARGET_DB_URL exists.
    This keeps docker/remote deployments idempotent even when
    the user forgets to pre-create the DB.
    """
    admin_url = _get_admin_db_url()
    target_url = make_url(TARGET_DB_URL)
    db_name = target_url.database

    temp_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with temp_engine.connect() as conn:
            exists = await conn.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": db_name},
            )
            if not exists:
                logger.info("Database %s not found, creating...", db_name)
                await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                logger.info("Database %s created", db_name)
    finally:
        await temp_engine.dispose()

engine = create_async_engine(url=TARGET_DB_URL)
# Do not expire attributes on commit to avoid lazy-loading after commit
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
   pass

class User(Base):
    __tablename__ = 'users'

    # Use Telegram id as the primary key (BigInteger). Remove separate `tg_id`.
    # Telegram id is unique per user and suits being a primary key here.
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(32), nullable=False)
    last_name: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    events = relationship("UserEvent", back_populates="user", cascade="all, delete-orphan")
    task_completions = relationship("TaskCompletion", back_populates="user", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    code: Mapped[str] = mapped_column(String(128), nullable=False)

    attendances = relationship("UserEvent", back_populates="event", cascade="all, delete-orphan")

class UserEvent(Base):
    __tablename__ = 'user_events'
    __table_args__ = (UniqueConstraint('user_id', 'event_id', name='uq_user_event'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id'), nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    awarded_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="events")
    event = relationship("Event", back_populates="attendances")

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    date_start: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    date_end: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    type: Mapped[str] = mapped_column(
        Enum('TF', 'AI', 'DISH', name='task_type'),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(512), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    completions = relationship("TaskCompletion", back_populates="task", cascade="all, delete-orphan")

class TaskCompletion(Base):
    __tablename__ = 'task_completions'
    __table_args__ = (UniqueConstraint('user_id', 'task_id', name='uq_user_task'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'), nullable=False)
    awarded_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    user_answer: Mapped[str] = mapped_column(String(256), nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="task_completions")
    task = relationship("Task", back_populates="completions")

async def async_main():
   await create_database_if_not_exists()

   async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
