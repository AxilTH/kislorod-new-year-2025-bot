from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

import app.database.requests as db_requests

import textwrap

router = Router()

@router.message(Command('profile'))
async def handler_profile(message: Message):
   try:
      is_user_registered = await db_requests.is_user_registered(message.from_user.id)
   except Exception as e:
      import logging
      logging.getLogger(__name__).error("Database error in profile handler: %s", e, exc_info=True)
      await message.answer("❌ Произошла ошибка при обращении к базе данных. Попробуйте позже.")
      return

   if not is_user_registered:
      text = textwrap.dedent(
      '''
         Ты еще не зарегистрирован!

         Для регистрации введи команду /start
      '''
      )
      await message.answer(text)
      return
   
   user = await db_requests.get_user_by_tg_id(message.from_user.id)
   visited_events = await db_requests.visited_events(message.from_user.id)

   text = textwrap.dedent(f'''
      <b>🎅 Ваш новогодний профиль:</b>
                          
      👤 {user.first_name} {user.last_name}
      📊 Статус: Боец 🧤

      💰 Волшебных снежинок собрано: {user.score}

      📈 Мероприятий посещено: {len(visited_events)}
   ''')
   await message.answer(text, parse_mode='HTML')