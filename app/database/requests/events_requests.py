from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.database.models import Event, User, UserEvent, async_session
from app.helpers.snowflake_helper import get_snowflakes_word

async def visited_events(tg_id: int) -> list[Event]:
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.id == tg_id))
      
      if not user:
         return []

      events = await session.execute(
         select(Event)
         .join(UserEvent, Event.id == UserEvent.event_id)
         .where(UserEvent.user_id == user.id)
      )
      return events.scalars().all()
      
async def get_event_by_id(event_id: int) -> Event | None:
   async with async_session() as session:
      event = await session.scalar(select(Event).where(Event.id == event_id))
      return event
   
async def get_all_events() -> list[Event]:
   async with async_session() as session:
      result = await session.execute(select(Event).order_by(Event.date))
      events = result.scalars().all()
      return events
      
async def create_event(title: str, date: str, score: int, code: str) -> Event:
   async with async_session() as session:
      event = Event(
         title=title,
         date=date,
         score=score,
         code=code
      )
      session.add(event)

      await session.commit()
      await session.refresh(event)

      return event
   
async def mark_attendance(user_id: int, event_id: int, codeword: str) -> tuple[bool, str, int]:
   # Returns (success, message, awarded_points)
   async with async_session() as session:
      event = await session.scalar(select(Event).where(Event.id == event_id))
      if not event:
         return False, "Мероприятие не найдено", 0

      # case-insensitive codeword check
      if event.code.strip().lower() != codeword.strip().lower():
         return False, "Неверное кодовое слово", 0

      awarded = event.score
      userEvent = UserEvent(user_id=user_id, event_id=event_id, awarded_points=awarded)
      session.add(userEvent)

      try:
         await session.execute(update(User).where(User.id == user_id).values(score=User.score + awarded))
         await session.commit()
         return True, f"Отметка принята, было зачислено +{awarded} {get_snowflakes_word(awarded)}!", awarded
      except IntegrityError:
         await session.rollback()
         return False, "Вы уже отмечены на этом мероприятии!", 0
