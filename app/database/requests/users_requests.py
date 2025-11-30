from sqlalchemy import select
from sqlalchemy.types import BigInteger

from app.database.models import User, async_session


async def is_user_registered(tg_id: BigInteger) -> bool:
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.id == tg_id))
      return user is not None

async def get_all_users() -> list[User]:
   async with async_session() as session:
      result = await session.execute(select(User))
      users = result.scalars().all()
      return users

async def get_user_by_tg_id(tg_id: BigInteger) -> User | None:
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.id == tg_id))
      return user

async def create_user(tg_id: BigInteger, firstName: str, lastName: str) -> User | None:
   async with async_session() as session:
      user = await session.scalar(select(User).where(User.id == tg_id))

      if not user:
         user = User(
            id=tg_id,
            first_name=firstName,
            last_name=lastName,
         )
         session.add(user)

         await session.commit()
         await session.refresh(user)

      return user
